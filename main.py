# main.py
__version__ = "1.1.16"
# Copyright 2026 Gregory Howard  all rights reserved.

# Ensure merged config.py exists before importing modules that expect flat config constants
try:
    from config_gen import generate_config_py
    generate_config_py()
except Exception as e:
    print(f"Warning: failed to generate config.py at startup: {e}")

# Optional non-fatal assertion to detect drift between merged JSON and generated config.py
try:
    from config_loader import load_merged_config
    import config as _cfg
    merged = load_merged_config()
    if getattr(_cfg, "CONFIG", None) != merged:
        print("Warning: generated config.py differs from merged config.json + admin defaults.")
except Exception:
    pass

import time
import socket
import requests
import ctypes
import sys
import os
import json
import hashlib
from datetime import datetime

from ts_client import TSClient
from execution_state import ExecutionState, State
from order_builder import format_option_symbol
from market_data import get_atm_surface, get_minute_prices_for_rebuild
from eligibility_engine import evaluate_trade
# OLD EMA IMPORTS (COMMENTED OUT)
# from ema_engine import EMAEngine
# from ema_rebuild import rebuild_emas
from trade_logger import log_event

from build_check import run_build_check
from license import check_license

# NEW EMA IMPORTS
from ema_bootstrap import initialize_ema_engine
from ema_persistence import save_ema_state
from ema_constants import EMA3_SECONDS, EMA5_SECONDS, EMA20_SECONDS

# ===== CONFIG IMPORTS (REPLACING ADMIN_CONFIG) =====
# Load all config constants from the generated config module
from config import (
    API_KEY,
    REFRESH_TOKEN,
    ACCOUNT_ID,
    ENABLE_LIVE_TRADING,
    PUSHOVER_USER_KEY,
    PUSHOVER_API_TOKEN,
    ADMIN_PUSHOVER_USER_KEY,
    ADMIN_PUSHOVER_API_TOKEN,
    PUSHOVER_ENABLED,
    WINDOWS_ALERT_ENABLED,
    STRIKE_STEP,
    SPREAD_WIDTH,
    MARKET_OPEN_TIME,
    TRADE_START_TIME,
    STOP_NEW_ENTRIES,
    FORCE_EXIT_TIME,
    FORCE_EXIT_ENABLED,
    ORDER_TIMEOUT,
    LOOP
)

# OLD ADMIN CONFIG LOAD (COMMENTED OUT)
# ADMIN_CONFIG_LOADED = False
# try:
#     from admin_config import *
#     ADMIN_CONFIG_LOADED = True
# except:
#     ADMIN_PUSHOVER_ENABLED = False
#     ADMIN_ENFORCEMENT_MODE = False

# ===== ENFORCEMENT CHECK (DEPRECATED - COMMENTED OUT) =====
# OLD ENFORCEMENT LOGIC (COMMENTED OUT)
# if ADMIN_ENFORCEMENT_MODE and not ADMIN_CONFIG_LOADED:
#     msg = """
# VTBC FATAL ERROR
# 
# Admin configuration required but not found.
# System cannot run in enforcement mode.
# """
#     print(msg)
#     try:
#         ctypes.windll.user32.MessageBoxW(0, msg, "VTBC CONFIG ERROR", 0x10)
#     except:
#         pass
#     sys.exit(1)


# ===== UNAUTHORIZED HANDLER (NEW) =====

def handle_unauthorized():

    user_id = socket.gethostname()

    msg = f"""
VTBC NOT AUTHORIZED

User ID:
{user_id}

Contact administrator for access.
"""

    print(msg)

    try:
        ctypes.windll.user32.MessageBoxW(0, msg, "VTBC AUTHORIZATION", 0x10)
    except:
        pass

    send_admin_alert(f"UNAUTHORIZED ACCESS ATTEMPT\nUser ID: {user_id}")


# ===== SYSTEM CONTROL =====
system_safe_mode = False


# ===== ALERTING =====

def send_alert(message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()

    full_msg = f"""
VTBC ALERT

Time: {timestamp}
Host: {hostname}
Version: {__version__}

{message}
"""

    if WINDOWS_ALERT_ENABLED:
        try:
            ctypes.windll.user32.MessageBoxW(0, full_msg, "VTBC ALERT", 0x10)
        except Exception as e:
            print(f"Popup failed: {e}")

    if PUSHOVER_ENABLED:
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": PUSHOVER_API_TOKEN,
                    "user": PUSHOVER_USER_KEY,
                    "message": full_msg
                }
            )
        except Exception as e:
            print(f"Pushover failed: {e}")


def send_admin_alert(message):

    if not ADMIN_PUSHOVER_API_TOKEN or not ADMIN_PUSHOVER_USER_KEY:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = socket.gethostname()

    full_msg = f"""
VTBC ADMIN ALERT

Time: {timestamp}
Host: {hostname}
Version: {__version__}

{message}
"""

    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": ADMIN_PUSHOVER_API_TOKEN,
                "user": ADMIN_PUSHOVER_USER_KEY,
                "message": full_msg
            }
        )
    except Exception as e:
        print(f"Admin alert failed: {e}")


# ===== CREDENTIAL VALIDATION =====

def validate_credentials():

    missing = []

    if not API_KEY or API_KEY == "YOUR_API_KEY":
        missing.append("API_KEY")

    if not REFRESH_TOKEN or REFRESH_TOKEN == "YOUR_REFRESH_TOKEN":
        missing.append("REFRESH_TOKEN")

    if not ACCOUNT_ID:
        missing.append("ACCOUNT_ID")

    if PUSHOVER_ENABLED:

        if not PUSHOVER_USER_KEY or PUSHOVER_USER_KEY == "YOUR_USER_KEY":
            missing.append("PUSHOVER_USER_KEY")

        if not PUSHOVER_API_TOKEN or PUSHOVER_API_TOKEN == "YOUR_API_TOKEN":
            missing.append("PUSHOVER_API_TOKEN")

    if missing:

        msg = f"Missing credentials: {', '.join(missing)}"

        try:
            ctypes.windll.user32.MessageBoxW(0, msg, "VTBC STARTUP FAILURE", 0x10)
        except:
            pass

        raise Exception(msg)


# ===== VALIDATION FLOW =====

def run_system_validation(spx_price=None, send_notifications=False):

    global system_safe_mode

    try:
        ok, msg = check_license(__version__)
        if not ok:
            handle_unauthorized()
            raise Exception(msg)

        run_build_check()

        system_safe_mode = False

        log_event(
            "SYSTEM_VALIDATION_PASS",
            spx_price,
            None,
            None,
            None,
            details=msg
        )

        if send_notifications:
            send_alert(f"SYSTEM VALIDATION PASSED\n{msg}")

    except Exception as e:

        system_safe_mode = True

        error_msg = f"SYSTEM VALIDATION FAILED\nReason: {str(e)}"

        log_event(
            "SYSTEM_VALIDATION_FAIL",
            spx_price,
            None,
            None,
            None,
            details=error_msg
        )

        print(f"\nSYSTEM IN SAFE MODE: {error_msg}\n")

        if send_notifications:
            send_alert(error_msg)

        send_admin_alert(error_msg)


def get_today_expiry():
    return datetime.now().strftime("%y%m%d")


def select_strike_K(spx_price, atm, direction):
    if direction == "C":
        return atm + STRIKE_STEP if atm < spx_price else atm
    else:
        return atm - STRIKE_STEP if atm > spx_price else atm


# ===== DISTRIBUTION CHECKSUM VERIFICATION HELPER =====
# SURGICAL CHECKSUM VERIFICATION INSERTION
def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_distribution_checksums(checksums_json_path, target_dir, fail_on_mismatch=False):
    """
    Verify checksums.json produced by the build installer against files in target_dir.
    
    NEW: Changed fail_on_mismatch default to False (optional for development).
    Exits with code 1 on mismatch only if fail_on_mismatch=True.
    """
    if not os.path.exists(checksums_json_path):
        print(f"⚠️  Missing checksums.json: {checksums_json_path}")
        if fail_on_mismatch:
            sys.exit(1)
        return False

    with open(checksums_json_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    ok = True

    support = data.get("support", {})
    if support:
        fname = support.get("file")
        expected = (support.get("sha256") or "").lower()
        path = os.path.join(target_dir, fname)
        if not os.path.exists(path):
            print(f"Missing file: {path}")
            ok = False
        else:
            actual = _sha256(path).lower()
            if actual != expected:
                print(f"Checksum mismatch for {fname}\n expected: {expected}\n actual:   {actual}")
                ok = False

    separate = data.get("separate", {})
    for fname, expected in separate.items():
        expected = (expected or "").lower()
        path = os.path.join(target_dir, fname)
        if not os.path.exists(path):
            print(f"Missing file: {path}")
            ok = False
            continue
        actual = _sha256(path).lower()
        if actual != expected:
            print(f"Checksum mismatch for {fname}\n expected: {expected}\n actual:   {actual}")
            ok = False

    if not ok and fail_on_mismatch:
        print("Checksum verification FAILED. Aborting.")
        sys.exit(1)

    if ok:
        print("✅ All distribution checksums match.")
    return ok


# ===== MAIN =====

if __name__ == "__main__":

    last_validation_date = None

    # SURGICAL CHECKSUM VERIFICATION INSERTION
    # NEW: Optional checksum verification (non-fatal by default for development)
    install_dir = os.path.dirname(os.path.abspath(__file__))
    checksums_path = os.path.join(install_dir, "checksums.json")
    verify_distribution_checksums(checksums_path, install_dir, fail_on_mismatch=False)

    validate_credentials()
    run_system_validation(send_notifications=True)

    # OLD EMA INITIALIZATION (COMMENTED OUT)
    # ema_engine = EMAEngine([EMA3_SECONDS, EMA5_SECONDS, EMA20_SECONDS])

    client = TSClient(API_KEY, REFRESH_TOKEN, ACCOUNT_ID)
    state = ExecutionState()

    print("SYSTEM STARTED")

    expiry = get_today_expiry()

    # OLD REBUILD LOGIC (COMMENTED OUT)
    # prices = get_minute_prices_for_rebuild(client, expiry)
    # rebuild_emas(ema_engine, prices)

    # NEW BOOTSTRAP INITIALIZATION
    ema_engine = initialize_ema_engine(client, expiry)

    try:
        while True:

            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")

            today = now.date()

            if now.strftime("%H:%M") == "09:00":
                if last_validation_date != today:
                    print("\n=== DAILY VALIDATION ===")
                    run_system_validation(send_notifications=True)
                    last_validation_date = today

            # NEW: Check force-exit time
            if FORCE_EXIT_ENABLED and time_str >= FORCE_EXIT_TIME:
                if state.state != State.IDLE:
                    print(f"[{time_str}] FORCE-EXIT TIME REACHED — Canceling position")
                    if state.order_id:
                        try:
                            client.cancel_order(state.order_id)
                            log_event("FORCE_EXIT", None, None, None, None, order_id=state.order_id)
                        except Exception as e:
                            print(f"Failed to cancel order: {e}")
                    state.state = State.IDLE

            allow_entries = not (time_str < TRADE_START_TIME or time_str >= STOP_NEW_ENTRIES)

            spx_data = client.get_spx_price()
            if not spx_data:
                time.sleep(LOOP)
                continue

            spx_price = float(spx_data["Quotes"][0]["Last"])

            surface = get_atm_surface(client, expiry, spx_price)

            ema_engine.update(spx_price, now)

            trade = evaluate_trade(spx_price, surface, ema_engine)

            # NEW: Handle long entry state
            if state.state == State.LONG_WORKING:
                # Poll order status (simplified: just check if still working)
                try:
                    order_status = client.get_order(state.order_id)
                    status = order_status.get("OrderStatus", "UNKNOWN")
                    
                    check_result = state.check_long(status)
                    
                    if check_result == "FILLED":
                        print(f"[{time_str}] Order FILLED: {state.order_id}")
                        state.state = State.IDLE
                        log_event("ORDER_FILLED", spx_price, state.direction, state.short_strike, None, order_id=state.order_id)
                    elif check_result == "CANCEL":
                        print(f"[{time_str}] Order TIMEOUT — Canceling: {state.order_id}")
                        try:
                            client.cancel_order(state.order_id)
                        except Exception as e:
                            print(f"Cancel failed: {e}")
                        state.state = State.IDLE
                        log_event("ORDER_TIMEOUT", spx_price, state.direction, state.short_strike, None, order_id=state.order_id)
                except Exception as e:
                    print(f"Error checking order status: {e}")

            # NEW: Entry conditions with lifecycle
            if (
                trade
                and state.state == State.IDLE
                and allow_entries
                and ENABLE_LIVE_TRADING
                and not system_safe_mode
            ):

                direction = trade["direction"]
                atm = surface["atm"]
                K = select_strike_K(spx_price, atm, direction)

                oid = client.place_order({
                    "AccountID": ACCOUNT_ID,
                    "OrderType": "Market",
                    "Legs": [
                        {
                            "Symbol": format_option_symbol(expiry, K, direction),
                            "Quantity": "1",
                            "TradeAction": "BUY"
                        }
                    ]
                })

                if oid:
                    state.submit_long(oid, K, 1, direction, 0.0)

                    log_event(
                        "ENTRY_PLACED",
                        spx_price,
                        direction,
                        K,
                        SPREAD_WIDTH,
                        order_id=oid
                    )

            time.sleep(LOOP)

    finally:
        try:
            save_ema_state(ema_engine)
        except Exception as e:
            print(f"Failed to save EMA state: {e}")
