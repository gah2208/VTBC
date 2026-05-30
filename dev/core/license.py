__version__ = "1.0.1"
# Copyright 2026 Gregory Howard  all rights reserved.

import requests
import hashlib
import socket
import uuid
import json
import os
import time
from datetime import datetime

AUTH_URL = "https://raw.githubusercontent.com/gah2208/ctv/main/auth.json"

CACHE_FILE = "auth_cache.json"
CACHE_TTL_SECONDS = 3600  # 1 hour


def get_user_id():
    raw = f"{socket.gethostname()}-{uuid.getnode()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def fetch_auth():

    try:
        r = requests.get(AUTH_URL, timeout=5)
        r.raise_for_status()
        data = r.json()

        # ✅ Save cache
        with open(CACHE_FILE, "w") as f:
            json.dump({
                "timestamp": time.time(),
                "data": data
            }, f)

        return data

    except Exception:

        # ✅ Attempt cache fallback
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)

                age = time.time() - cache.get("timestamp", 0)

                if age <= CACHE_TTL_SECONDS:
                    return cache.get("data")

        # ❌ No valid cache
        raise Exception("AUTH FETCH FAILED AND CACHE EXPIRED")


def version_to_float(v):
    try:
        return float(v)
    except:
        return 0.0


def check_license(system_version):

    user_id = get_user_id()
    auth = fetch_auth()

    users = auth.get("users", {})

    if user_id not in users:
        return False, f"UNAUTHORIZED USER: {user_id}"

    user = users[user_id]

    if not user.get("enabled", False):
        return False, f"USER DISABLED: {user_id}"

    min_version = auth.get("min_version", 0)

    if version_to_float(system_version) < float(min_version):
        return False, f"VERSION TOO OLD: {system_version} < {min_version}"

    exp = user.get("expires")
    if exp:
        try:
            if datetime.now().date() > datetime.strptime(exp, "%Y-%m-%d").date():
                return False, f"LICENSE EXPIRED: {exp}"
        except:
            pass

    return True, f"AUTHORIZED: {user_id}"