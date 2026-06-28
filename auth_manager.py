__version__ = "1.0.1"
copyright (c) Gregory Howard 2026  all rights reserved

import os
import uuid
import requests
import hashlib
import socket
import sys
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.py")

AUTH_URL = "https://raw.githubusercontent.com/gah2208/vtbc/main/auth.json"


# ===== LOAD CONFIG =====
def load_config():
    values = {}
    with open(CONFIG_FILE) as f:
        for line in f:
            if "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"')
    return values


# ===== MACHINE ID =====
def get_machine_id():
    raw = str(uuid.getnode())
    return hashlib.md5(raw.encode()).hexdigest()[:8]


# ===== USER NAME =====
def get_user_name():
    try:
        return os.getlogin()
    except:
        return socket.gethostname()


# ===== ADMIN ALERT =====
def send_admin_alert(msg):
    cfg = load_config()

    token = cfg.get("ADMIN_PUSHOVER_API_TOKEN", "")
    user = cfg.get("ADMIN_PUSHOVER_USER_KEY", "")

    if not token or not user:
        return

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": token,
                "user": user,
                "message": msg
            },
            timeout=5
        )
    except:
        pass


# ===== FETCH AUTH =====
def fetch_auth():
    try:
        r = requests.get(AUTH_URL, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


# ===== AUTH CHECK =====
def check_authorization(data):

    machine_id = get_machine_id()
    users = data.get("users", {})

    if machine_id not in users:
        return False

    return users[machine_id].get("enabled", False)


# ===== MAIN ENFORCER =====
def enforce_auth():

    data = fetch_auth()

    # ❌ FAIL-CLOSED: GitHub not available
    if not data:
        messagebox.showerror(
            "Authorization Error",
            "GitHub authorization not available.\n\n"
            "Check your internet connection and try again."
        )
        sys.exit(1)

    # ✅ AUTH CHECK
    if check_authorization(data):
        return True

    # ❌ UNAUTHORIZED → SEND ALERT
    msg = (
        "UNAUTHORIZED ACCESS ATTEMPT\n\n"
        f"User: {get_user_name()}\n"
        f"Machine ID: {get_machine_id()}"
    )

    send_admin_alert(msg)

    return False
