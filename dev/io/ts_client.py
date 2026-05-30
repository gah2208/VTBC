__version__ = "1.0.2"
# Copyright 2026 Gregory Howard  all rights reserved.

import requests, time
from config import *

class TSClient:

    def __init__(self, api_key, refresh_token, account_id):
        self.api_key = api_key
        self.refresh_token = refresh_token
        self.account_id = account_id
        self.base_url = "https://sim-api.tradestation.com/v3"
        self.auth_url = "https://signin.tradestation.com/oauth/token"
        self.access_token = None
        self.token_expiry = 0
        self.fail_count = 0
        self._refresh_access_token()


    def _refresh_access_token(self):

        for _ in range(ORDER_RETRY_ATTEMPTS):

            try:
                r = requests.post(self.auth_url, data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.api_key
                })

                data = r.json()

                self.access_token = data["access_token"]
                self.token_expiry = time.time() + data["expires_in"] - 60

                return

            except:
                time.sleep(TOKEN_REFRESH_DELAY)

        raise Exception("AUTH FAIL")


    def _headers(self):

        if time.time() >= self.token_expiry:
            self._refresh_access_token()

        return {"Authorization": f"Bearer {self.access_token}"}


    def _req(self, method, url, **kwargs):

        for _ in range(DATA_RETRY_ATTEMPTS):

            try:
                r = method(url, headers=self._headers(), **kwargs)

                if r.status_code == 200:
                    self.fail_count = 0
                    return r.json()

            except:
                pass

            time.sleep(DATA_RETRY_DELAY)

        self.fail_count += 1

        if self.fail_count >= MAX_API_FAILURES:
            raise Exception("API FAILURE")

        return None


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

        r = self._req(
            requests.post,
            f"{self.base_url}/orderexecution/orders",
            json=payload
        )

        return r and r.get("OrderID")


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