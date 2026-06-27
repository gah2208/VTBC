__version__ = "1.1.1"
# copyright (c) Gregory Howard   all rights reserved


# ============================================================
# NEW IMPLEMENTATION (ACTIVE CODE)
# ============================================================

from datetime import datetime, timedelta
import math
from ema_constants import EMA20_SECONDS, EMA5_SECONDS, EMA3_SECONDS


def get_cross_day_minute_prices(client, expiry):
    """
    Fetch enough 1-minute SPX bars to satisfy a full 60-minute EMA20 window.

    Strategy:
        - Pull yesterday's bars from 15:11 → 16:00 (49 bars)
        - Pull today's bars from 09:30 → now
        - Combine until we have ≥ 60 bars
    """

    prices = []

    # ===== 1. Yesterday 15:11 → 16:00 =====
    # Broker API does not support timestamped queries, so we repeatedly poll
    # until we accumulate the required number of bars.
    #
    # We only need 49 bars from yesterday.
    #
    # NOTE: This assumes the broker returns the last known SPX price on each call.
    #       This is consistent with the existing get_minute_prices_for_rebuild().
    #
    import time

    while len(prices) < 49:
        spx_data = client.get_spx_price()
        if spx_data:
            prices.append(float(spx_data["Quotes"][0]["Last"]))
        time.sleep(60)

    # ===== 2. Today 09:30 → now =====
    # Continue collecting until we have at least 60 total bars.
    #
    while len(prices) < 60:
        spx_data = client.get_spx_price()
        if spx_data:
            prices.append(float(spx_data["Quotes"][0]["Last"]))
        time.sleep(60)

    return prices[-60:]  # ensure exactly 60 bars


def rebuild_emas(ema_engine, minute_prices):
    """
    Rebuild EMA state using 1-minute price series.

    Window rules:
        EMA20 = last 60 minutes
        EMA5  = last 15 minutes
        EMA3  = last 9 minutes
    """

    if len(minute_prices) < 60:
        raise Exception("Not enough data to rebuild EMA (need at least 60 minutes)")

    now = datetime.now()

    timestamps = []
    for i in range(len(minute_prices)):
        ts = now - timedelta(minutes=(len(minute_prices) - i))
        timestamps.append(ts)

    # ===== EMA20 — last 60 minutes =====
    ema_engine.values[EMA20_SECONDS] = None
    start_20 = max(0, len(minute_prices) - 60)

    for i in range(start_20, len(minute_prices)):
        _update_single(ema_engine, EMA20_SECONDS, minute_prices[i], timestamps[i])

    # ===== EMA5 — last 15 minutes =====
    ema_engine.values[EMA5_SECONDS] = None
    start_5 = max(0, len(minute_prices) - 15)

    for i in range(start_5, len(minute_prices)):
        _update_single(ema_engine, EMA5_SECONDS, minute_prices[i], timestamps[i])

    # ===== EMA3 — last 9 minutes =====
    ema_engine.values[EMA3_SECONDS] = None
    start_3 = max(0, len(minute_prices) - 9)

    for i in range(start_3, len(minute_prices)):
        _update_single(ema_engine, EMA3_SECONDS, minute_prices[i], timestamps[i])


def _update_single(ema_engine, period, price, timestamp):
    """
    Update a single EMA without touching others.
    """

    if ema_engine.last_timestamp is None:
        ema_engine.values[period] = price
        ema_engine.last_timestamp = timestamp
        ema_engine.timestamp_history.append(timestamp.timestamp())
    else:
        prev = ema_engine.values[period]

        if prev is None:
            ema_engine.values[period] = price
        else:
            dt = (timestamp - ema_engine.last_timestamp).total_seconds()

            if dt <= 0:
                return

            tau = ema_engine.taus[period]
            alpha = 1.0 - math.exp(-dt / tau)

            ema_engine.values[period] = prev + alpha * (price - prev)

        # NEW: Cap history arrays at 1800 to prevent unbounded growth
        ema_engine.history[period].append(ema_engine.values[period])
        if len(ema_engine.history[period]) > 1800:
            ema_engine.history[period].pop(0)

        ema_engine.last_timestamp = timestamp
        ema_engine.timestamp_history.append(timestamp.timestamp())
        # NEW: Cap timestamp history at 1800 to match other history arrays
        if len(ema_engine.timestamp_history) > 1800:
            ema_engine.timestamp_history.pop(0)
