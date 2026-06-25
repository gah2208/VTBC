__version__ = "2.0.0"
# Copyright 2026 Gregory Howard

import requests
import time
import json
import os

# ============================================================
# CONFIG IMPORT
# ============================================================
from config import (
    ORDER_RETRY_ATTEMPTS,
    TOKEN_REFRESH_DELAY,
    DATA_RETRY_ATTEMPTS,
    DATA_RETRY_DELAY,
    MAX_API_FAILURES
)

# ============================================================
# OPTIONAL DEBUG LOGGING
# ============================================================
DEBUG_LOG = True   # Set to False to disable logging

def _log(msg):
    if DEBUG_LOG:
        print(f"[TSClient] {msg}")


class TSClient:

    # ========================================================
    # SIM vs LIVE ENDPOINTS
    # ========================================================
    BASE_URL_SIM  = "https://sim-api.tradestation.com/v3"
    BASE_URL_LIVE = "https://api.tradestation.com/v3"

    AUTH_URL = "https://signin.tradestation.com/oauth/token"

    def __init__(self, api_key, refresh_token, account_id, live=False):
        """
        live=False  → SIM trading
        live=True   → LIVE trading
        """

        self.api_key = api_key
        self.refresh_token = refresh_token
        self.account_id = account_id

        self.base_url = self.BASE_URL_LIVE if live else self.BASE_URL_SIM

        self.access_token = None
        self.token_expiry = 0
        self.fail_count = 0

        _log(f"Initialized TSClient (live={live})")
        self._refresh_access_token()


    # ========================================================
    # TOKEN REFRESH
    # ========================================================
    def _refresh_access_token(self):

        _log("Refreshing access token...")

        for attempt in range(ORDER_RETRY_ATTEMPTS):

            try:
                r = requests.post(self.AUTH_URL, data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.api_key
                })

                # OLD (commented out)
                # data = r.json()

                # NEW SAFE JSON
                data = self._safe_json(r)

                if "access_token" not in data:
                    raise Exception(f"Bad token response: {data}")

                self.access_token = data["access_token"]
                self.token_expiry = time.time() + data["expires_in"] - 60

                _log("Access token refreshed successfully.")
                return

            except Exception as e:
                _log(f"Token refresh failed: {e}")
                time.sleep(TOKEN_REFRESH_DELAY)

        raise Exception("AUTH FAIL — Could not refresh access token")


    # ========================================================
    # HEADERS
    # ========================================================
    def _headers(self):

        if time.time() >= self.token_expiry:
            self._refresh_access_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }


    # ========================================================
    # NEW SAFE JSON WRAPPER
    # ========================================================
    def _safe_json(self, r):
        try:
            return r.json()
        except:
            return {}


    # ========================================================
    # GENERIC REQUEST WRAPPER
    # ========================================================
    def _req(self, method, url, **kwargs):

        for attempt in range(DATA_RETRY_ATTEMPTS):

            try:
                _log(f"REQUEST → {url}")
                if "json" in kwargs:
                    _log(f"PAYLOAD → {json.dumps(kwargs['json'], indent=2)}")

                r = method(url, headers=self._headers(), **kwargs)

                if r.status_code == 200:
                    self.fail_count = 0

                    # OLD (commented out)
                    # return r.json()

                    # NEW SAFE JSON
                    return self._safe_json(r)

                _log(f"Non-200 response: {r.status_code} {r.text}")

            except Exception as e:
                _log(f"Request error: {e}")

            time.sleep(DATA_RETRY_DELAY)

        self.fail_count += 1

        if self.fail_count >= MAX_API_FAILURES:
            raise Exception("API FAILURE — Too many consecutive failures")

        # NEW SAFE FALLBACK
        return {}


    # ========================================================
    # PUBLIC API METHODS
    # ========================================================
    def get_spx_price(self):
        return self._req(
            requests.get,
            f"{self.base_url}/marketdata/quotes/SPX"
        )


    def get_quotes(self, symbols):
        return self._req(
            requests.get,
            f"{self.base_url}/marketdata/quotes/" + ",".join(symbols)
        )


    def place_order(self, payload):
        """
        payload MUST contain:
            - OrderType
            - LimitPrice
            - Legs: [ {Symbol, TradeAction, Quantity}, ... ]
        """

        url = f"{self.base_url}/orderexecution/orders"

        r = self._req(
            requests.post,
            url,
            json=payload
        )

        if r:
            _log(f"Order placed. OrderID={r.get('OrderID')}")
            return r.get("OrderID")

        return None


    def get_order(self, oid):
        return self._req(
            requests.get,
            f"{self.base_url}/orderexecution/orders/{oid}"
        )


    def cancel_order(self, oid):
        return self._req(
            requests.delete,
            f"{self.base_url}/orderexecution/orders/{oid}"
        )
