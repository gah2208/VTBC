__version__ = "1.0.0"
# Copyright 2026 Gregory Howard

import time


# ============================================================
# NEW IMPLEMENTATION (ACTIVE CODE)
# ============================================================

def get_historical_minute_bars(client, minutes_needed):
    """
    Fetch historical 1-minute SPX bars.

    If the broker supports historical queries, use them.
    If not, fallback to repeated polling (same behavior as old rebuild).
    """

    # Attempt historical endpoint (if supported)
    try:
        r = client._req(
            method=client._headers,  # placeholder — broker may not support historical
            url=f"{client.base_url}/marketdata/barcharts/SPX?interval=1&barsback={minutes_needed}"
        )
        if r and "Bars" in r:
            bars = r["Bars"]
            prices = [float(b["Close"]) for b in bars][-minutes_needed:]
            if len(prices) == minutes_needed:
                return prices
    except:
        pass

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
