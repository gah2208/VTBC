__version__ = "1.1.11"
# Copyright 2026 Gregory Howard  all rights reserved.

import time
import socket
import requests
import ctypes
import sys
from datetime import datetime

from ts_client import TSClient
from execution_state import ExecutionState, State
from order_builder import format_option_symbol
from market_data import get_atm_surface, get_minute_prices_for_rebuild
from eligibility_engine import evaluate_trade
from ema_engine import EMAEngine
from ema_rebuild import rebuild_emas
from trade_logger import log_event
from config import *

from build_check import run_build_check
from checksum import verify_checksum
from license import check_license


# ===== ADMIN CONFIG LOAD =====
ADMIN_CONFIG_LOADED = False

try:
    from admin_config import *
    ADMIN_CONFIG_LOADED = True
except:
    ADMIN_PUSHOVER_ENABLED = False
    ADMIN_ENFORCEMENT_MODE = False


# ===== ENFORCEMENT CHECK =====
if ADMIN_ENFORCEMENT_MODE and not ADMIN_CONFIG_LOADED:

    msg = """
VTBC FATAL ERROR

Admin configuration required but not found.
System cannot run in enforcement mode.
"""

    print(msg)

    try:
        ctypes.windll.user32.MessageBoxW(0, msg, "VTBC CONFIG ERROR", 0x10)
    except:
        pass

    sys.exit(1)


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

    if not ADMIN_PUSHOVER_ENABLED:
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
        verify_checksum()

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


# ===== MAIN =====

if __name__ == "__main__":

    last_validation_date = None
    last_heartbeat_time = None

    validate_credentials()
    run_system_validation(send_notifications=True)

    ema_engine = EMAEngine([EMA3_SECONDS, EMA5_SECONDS, EMA20_SECONDS])

    client = TSClient(API_KEY, REFRESH_TOKEN, ACCOUNT_ID)
    state = ExecutionState()

    print("SYSTEM STARTED")

    expiry = get_today_expiry()
    prices = get_minute_prices_for_rebuild(client, expiry)
    rebuild_emas(ema_engine, prices)

    while True:

        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        if (
            last_heartbeat_time is None
            or (now - last_heartbeat_time).total_seconds() >= HEARTBEAT_INTERVAL_SECONDS
        ):
            status = "SAFE MODE — HOLD" if system_safe_mode else "SYSTEM OK"
            print(f"[{time_str}] {status}")
            last_heartbeat_time = now

        today = now.date()

        if now.strftime("%H:%M") == "09:00":
            if last_validation_date != today:
                print("\n=== DAILY VALIDATION ===")
                run_system_validation(send_notifications=True)
                last_validation_date = today

        allow_entries = not (time_str < TRADE_START_TIME or time_str >= STOP_NEW_ENTRIES)

        spx_data = client.get_spx_price()
        if not spx_data:
            time.sleep(LOOP_SLEEP_SECONDS)
            continue

        spx_price = float(spx_data["Quotes"][0]["Last"])

        surface = get_atm_surface(client, expiry, spx_price)

        ema_engine.update(spx_price, now)

        trade = evaluate_trade(spx_price, surface, ema_engine)

        if (
            trade
            and state.state == State.IDLE
            and allow_entries
            and ENABLE_TRADING
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
                    CONVERSION_WIDTH,
                    order_id=oid
                )

        time.sleep(LOOP_SLEEP_SECONDS)