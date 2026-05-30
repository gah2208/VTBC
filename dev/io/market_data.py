__version__ = "1.0.1"
# Copyright 2026 Gregory Howard  all rights reserved.

from order_builder import format_option_symbol
from config import STRIKE_STEP, STRIKE_RANGE, CONVERSION_WIDTH


def get_atm_surface(client, expiry, spx_price):

    atm = round(spx_price / STRIKE_STEP) * STRIKE_STEP

    strikes = [atm + i * STRIKE_STEP for i in range(-STRIKE_RANGE, STRIKE_RANGE + 1)]

    symbols = []

    for s in strikes:
        symbols.append(format_option_symbol(expiry, s, "C"))
        symbols.append(format_option_symbol(expiry, s, "P"))

    data = client.get_quotes(symbols)

    surface = []

    for q in data["Quotes"]:
        surface.append({
            "symbol": q["Symbol"],
            "bid": float(q.get("Bid", 0)),
            "ask": float(q.get("Ask", 0)),
            "last": float(q.get("Last", 0))
        })

    return {"atm": atm, "surface": surface}


def get_k_surface(client, expiry, K):

    W = CONVERSION_WIDTH

    strikes = [K + i * W for i in range(-STRIKE_RANGE, STRIKE_RANGE + 1)]

    symbols = []

    for s in strikes:
        symbols.append(format_option_symbol(expiry, s, "C"))
        symbols.append(format_option_symbol(expiry, s, "P"))

    data = client.get_quotes(symbols)

    surface = []

    for q in data["Quotes"]:
        surface.append({
            "symbol": q["Symbol"],
            "bid": float(q.get("Bid", 0)),
            "ask": float(q.get("Ask", 0)),
            "last": float(q.get("Last", 0))
        })

    return {"K": K, "surface": surface}


def get_minute_prices_for_rebuild(client, expiry):

    import time

    minute_prices = []

    while len(minute_prices) < 120:

        spx_data = client.get_spx_price()

        if not spx_data:
            time.sleep(1)
            continue

        spx_price = float(spx_data["Quotes"][0]["Last"])

        minute_prices.append(spx_price)

        time.sleep(60)

    return minute_prices