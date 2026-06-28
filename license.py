# license.py
__version__ = "1.1.1"
# Copyright 2026 Gregory Howard  all rights reserved.

"""
License verification with local cache fallback.

Behavior (surgical, minimal, robust):
- Primary: query remote license server with machine id and current app version.
- On network failure or server error: fall back to cached license response if available and not expired.
- Cache is stored atomically in LICENSE_CACHE_FILE as JSON: {"machine_id": "...", "ok": true/false, "msg": "...", "timestamp": epoch_seconds}
- Public API: check_license(app_version: str) -> (bool, str)
"""

from pathlib import Path
import json
import time
import hashlib
import socket
import uuid
import requests

BASE_DIR = Path(__file__).parent
LICENSE_CACHE_FILE = BASE_DIR / "license_cache.json"
LICENSE_URL = "https://raw.githubusercontent.com/VTBC/license-check/main/license.json"  # canonical endpoint
AUTH_URL = "https://raw.githubusercontent.com/gah2208/vtbc/main/auth.json"
CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours

def _parse_version(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in str(value).strip().split("."))
    except Exception:
        return ()

def _check_auth_min_version(app_version: str) -> tuple[bool, str]:
    """
    Version gate sourced from auth.json.
    Returns (ok, message). If auth source is unavailable or malformed, allow startup.
    """
    try:
        r = requests.get(AUTH_URL, timeout=6.0)
        if r.status_code != 200:
            return True, ""
        payload = r.json()
        min_version = payload.get("min_version")
        if min_version is None:
            return True, ""

        current_version = _parse_version(app_version)
        required_version = _parse_version(min_version)
        if not current_version or not required_version:
            return True, ""

        if current_version >= required_version:
            return True, ""

        return False, (
            f"Version check failed: current version {app_version} "
            f"is below required version {min_version} from auth.json."
        )
    except Exception:
        return True, ""

def _machine_id() -> str:
    """
    Deterministic machine identifier used for license checks.
    Uses hostname + MAC (uuid.getnode()) hashed with SHA256.
    """
    try:
        mac = uuid.getnode()
        host = socket.gethostname()
        raw = f"{host}-{mac}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
    except Exception:
        # Fallback to hostname hash only
        try:
            host = socket.gethostname()
            return hashlib.sha256(host.encode("utf-8")).hexdigest()
        except Exception:
            return "unknown-machine"

def _load_cache() -> dict | None:
    try:
        if not LICENSE_CACHE_FILE.exists():
            return None
        data = json.loads(LICENSE_CACHE_FILE.read_text(encoding="utf-8"))
        return data
    except Exception:
        return None

def _save_cache(payload: dict) -> None:
    try:
        tmp = LICENSE_CACHE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(LICENSE_CACHE_FILE)
    except Exception:
        # best-effort; do not raise
        pass

def _is_cache_valid(cache: dict) -> bool:
    try:
        ts = float(cache.get("timestamp", 0))
        return (time.time() - ts) <= CACHE_TTL_SECONDS
    except Exception:
        return False

def _query_remote(machine_id: str, app_version: str) -> tuple[bool, str, dict | None]:
    """
    Query the remote license endpoint.
    Returns (ok, msg, raw_response_dict_or_none)
    """
    try:
        params = {"machine": machine_id, "version": app_version}
        r = requests.get(LICENSE_URL, params=params, timeout=6.0)
        if r.status_code != 200:
            return False, f"License server returned {r.status_code}", None
        try:
            payload = r.json()
        except Exception:
            return False, "License server returned invalid JSON", None

        # Expect payload to contain {"ok": true/false, "msg": "..."}
        ok = bool(payload.get("ok", False))
        msg = str(payload.get("msg", "")) or ("Authorized" if ok else "Not authorized")
        return ok, msg, payload
    except requests.RequestException as e:
        return False, f"Network error: {e}", None
    except Exception as e:
        return False, f"Unexpected error: {e}", None

def check_license(app_version: str) -> tuple[bool, str]:
    """
    Public API: check license for this machine and app version.
    Returns (ok: bool, message: str).

    Behavior:
    - Try remote query.
    - If remote succeeds, cache result and return it.
    - If remote fails, attempt to use cached result if present and not expired.
    - If no valid cache, return (False, reason).
    """
    machine = _machine_id()

    version_ok, version_msg = _check_auth_min_version(app_version)
    if not version_ok:
        return False, version_msg

    # Try remote first
    ok, msg, raw = _query_remote(machine, app_version)
    if raw is not None:
        # Cache the authoritative response with timestamp
        cache_payload = {
            "machine_id": machine,
            "ok": bool(ok),
            "msg": str(msg),
            "timestamp": time.time(),
            "server_payload": raw
        }
        _save_cache(cache_payload)
        return ok, msg

    # Remote failed; attempt cache fallback
    cache = _load_cache()
    if cache and cache.get("machine_id") == machine and _is_cache_valid(cache):
        return bool(cache.get("ok", False)), str(cache.get("msg", "Cached license result"))
    else:
        # No valid cache; return remote failure message
        return False, msg or "License check failed and no valid cache available."
