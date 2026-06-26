#!/usr/bin/env python3
"""
SIM smoke test for TSClient.
- Verifies authentication and basic API access via get_spx_price().
- Optionally places a SIM Market order with client_ref idempotency.
- Uses ORDER_TIMEOUT from merged config for order submission.

CAUTION: This may place real SIM orders. Do not run with LIVE credentials.
"""
import os
import sys
import json
import time

from ts_client import TSClient
from config_loader import load_merged_config

# Load merged config
cfg = load_merged_config()

API_KEY = cfg.get("API_KEY") or os.environ.get("API_KEY")
REFRESH_TOKEN = cfg.get("REFRESH_TOKEN") or os.environ.get("REFRESH_TOKEN")
ACCOUNT_ID = cfg.get("ACCOUNT_ID") or os.environ.get("ACCOUNT_ID")
ORDER_TIMEOUT = cfg.get("ORDER_TIMEOUT", 180)

if not (API_KEY and REFRESH_TOKEN and ACCOUNT_ID):
    print("Missing credentials. Set API_KEY, REFRESH_TOKEN, ACCOUNT_ID in merged config or env vars.")
    sys.exit(1)

print(f"[SIM SMOKE TEST] Creating TSClient (SIM mode, ORDER_TIMEOUT={ORDER_TIMEOUT}s)")
client = TSClient(API_KEY, REFRESH_TOKEN, ACCOUNT_ID, live=False)

print("\n[STEP 1] Testing market data / auth with get_spx_price()...")
spx = client.get_spx_price()
print("Response:")
try:
    print(json.dumps(spx, indent=2))
except Exception:
    print(spx)

if not spx:
    print("\nWARNING: get_spx_price returned no data. Check credentials. Aborting.")
    sys.exit(1)

print("\n[STEP 2] Non-interactive SIM order placement test")
TEST_SYMBOL = os.environ.get("TEST_SYMBOL", "SPXW 250619C00701000")
print(f"Test symbol: {TEST_SYMBOL}")

client_ref = f"vtbc-smoke-{int(time.time()*1000)}"
payload = {
    "AccountID": ACCOUNT_ID,
    "OrderType": "Market",
    "Legs": [
        {
            "Symbol": TEST_SYMBOL,
            "Quantity": "1",
            "TradeAction": "BUY"
        }
    ]
}

print(f"Submitting Market order with client_ref={client_ref}")
oid = client.place_order(payload, client_ref=client_ref, timeout=ORDER_TIMEOUT)

if oid:
    print(f"\n[SUCCESS] Order placed. OrderID: {oid}")
    print("Fetching order details...")
    details = client.get_order(oid)
    print("Order details:")
    try:
        print(json.dumps(details, indent=2))
    except Exception:
        print(details)
    sys.exit(0)

print("\n[AMBIGUOUS] No immediate OrderID. Checking by client_ref lookup...")
lookup = client.get_order_by_client_ref(client_ref, timeout=ORDER_TIMEOUT)
print("Lookup result:")
try:
    print(json.dumps(lookup, indent=2))
except Exception:
    print(lookup)

# Try to extract order ID from lookup
def _extract_order_id(resp):
    if not resp:
        return None
    if isinstance(resp, dict):
        for k in ("OrderID", "orderId", "id"):
            if k in resp and resp[k]:
                return resp[k]
        for v in resp.values():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                for k in ("OrderID", "orderId", "id"):
                    if k in v[0] and v[0][k]:
                        return v[0][k]
        return None
    if isinstance(resp, list) and len(resp) > 0 and isinstance(resp[0], dict):
        for k in ("OrderID", "orderId", "id"):
            if k in resp[0] and resp[0][k]:
                return resp[0][k]
    return None

found_oid = _extract_order_id(lookup)
if found_oid:
    print(f"\n[FOUND BY LOOKUP] OrderID={found_oid}")
    details = client.get_order(found_oid)
    print("Order details:")
    try:
        print(json.dumps(details, indent=2))
    except Exception:
        print(details)
    sys.exit(0)

print("\n[FAILED] No order found by client_ref. Submission is ambiguous (no duplicate resubmit performed).")
sys.exit(0)