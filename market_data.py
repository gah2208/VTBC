__version__ = "1.1.0"
# Copyright 2026 Gregory Howard

import time
import requests


# ============================================================
# NEW IMPLEMENTATION (ACTIVE CODE)
# ============================================================

def get_historical_minute_bars(client, minutes_needed):
    """
    Fetch historical 1-minute SPX bars.

    If the broker supports historical queries, use them.
    If not, fallback to repeated polling (same behavior as old rebuild).
    """

    # NEW: Attempt historical endpoint using correct request method
    try:
        r = client._req(
            method=requests.get,
            url=f"{client.base_url}/marketdata/barcharts/SPX?interval=1&barsback={minutes_needed}"
        )
        if r and "Bars" in r:
            bars = r["Bars"]
            prices = [float(b["Close"]) for b in bars][-minutes_needed:]
            if len(prices) == minutes_needed:
                return prices
    except:
        pass

    # OLD CODE (COMMENTED OUT)
    # try:
    #     r = client._req(
    #         method=client._headers,  # WRONG: this is a method, not a request function
    #         url=f"{client.base_url}/marketdata/barcharts/SPX?interval=1&barsback={minutes_needed}"
    #     )
    #     if r and "Bars" in r:
    #         bars = r["Bars"]
    #         prices = [float(b["Close"]) for b in bars][-minutes_needed:]
    #         if len(prices) == minutes_needed:
    #             return prices
    # except:
    #     pass

    # Fallback: repeated polling (same as old get_minute_prices_for_rebuild)
    prices = []

    while len(prices) < minutes_needed:
        data = client.get_spx_price()
        if data:
            prices.append(float(data["Quotes"][0]["Last"]))
        time.sleep(60)

    return prices[-minutes_needed:]


# ============================================================
# SURGICAL ADDITIONS: compatibility wrappers expected by main.py
# ============================================================

# Note: main.py imports get_minute_prices_for_rebuild and get_atm_surface
# from this module. Provide thin wrappers here that adapt to the existing
# get_historical_minute_bars implementation so main.py can import
# successfully without changing its code.


def get_minute_prices_for_rebuild(client, expiry):
    """
    Compatibility wrapper that returns the last 60 1-minute SPX prices.
    """
    # expiry is currently unused in this wrapper but kept for API compatibility
    return get_historical_minute_bars(client, 60)



def get_atm_surface(client, expiry, spx_price):
    """
    Minimal ATM surface provider used by main.py. Returns a dictionary with
    an "atm" key representing the at-the-money strike as an integer.

    This is intentionally minimal and surgical: it allows main.py to run
    and perform downstream checks. A more feature-complete implementation
    can replace this later.
    """
    atm = int(round(spx_price))
    return {"atm": atm}


# ============================================================
# NEW: Option Quote + Vertical Spread Quote Helpers
# ============================================================

def get_option_quote(client, expiry, strike, right):
    """
    Fetch bid/ask/mid for a single option.

    right: "C" or "P"
    Returns dict {"bid": float, "ask": float, "mid": float} or None on failure.
    """
    from order_builder import format_option_symbol

    symbol = format_option_symbol(expiry, strike, right)

    try:
        r = client.get_quotes([symbol])
        if not r or "Quotes" not in r or len(r["Quotes"]) < 1:
            return None

        q = r["Quotes"][0]
        bid = float(q.get("Bid", 0) or 0)
        ask = float(q.get("Ask", 0) or 0)
        mid = round((bid + ask) / 2, 4)

        return {"bid": bid, "ask": ask, "mid": mid}
    except Exception:
        return None


def get_spread_quote(client, expiry, long_strike, short_strike, right):
    """
    Fetch bid/ask/mid for a 2-leg debit vertical spread.

    For BUY long / SELL short:
      spread_bid = long_bid - short_ask
      spread_ask = long_ask - short_bid
      spread_mid = (spread_bid + spread_ask) / 2
    """
    from order_builder import format_option_symbol

    long_sym = format_option_symbol(expiry, long_strike, right)
    short_sym = format_option_symbol(expiry, short_strike, right)

    try:
        r = client.get_quotes([long_sym, short_sym])
        if not r or "Quotes" not in r or len(r["Quotes"]) < 2:
            return None

        long_q = next((q for q in r["Quotes"] if q.get("Symbol", "") == long_sym), None)
        short_q = next((q for q in r["Quotes"] if q.get("Symbol", "") == short_sym), None)

        if not long_q or not short_q:
            return None

        long_bid = float(long_q.get("Bid", 0) or 0)
        long_ask = float(long_q.get("Ask", 0) or 0)
        short_bid = float(short_q.get("Bid", 0) or 0)
        short_ask = float(short_q.get("Ask", 0) or 0)

        spread_bid = round(long_bid - short_ask, 4)
        spread_ask = round(long_ask - short_bid, 4)
        spread_mid = round((spread_bid + spread_ask) / 2, 4)

        return {"bid": spread_bid, "ask": spread_ask, "mid": spread_mid}
    except Exception:
        return None
