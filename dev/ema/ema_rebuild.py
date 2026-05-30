__version__ = "1.0.1"

from config import *
from datetime import datetime, timedelta
import math


def rebuild_emas(ema_engine, minute_prices):
    """
    Rebuild EMA state using 1-minute price series.

    minute_prices: list of floats ordered oldest → newest
    """

    if len(minute_prices) < 120:
        raise Exception("Not enough data to rebuild EMA")

    # ===== EMA20 (use full 120 minutes)
    ema_engine.values[EMA20_SECONDS] = None

    now = datetime.now()

    timestamps = []
    for i in range(len(minute_prices)):
        ts = now - timedelta(minutes=(len(minute_prices) - i))
        timestamps.append(ts)

    for i in range(len(minute_prices)):
        _update_single(ema_engine, EMA20_SECONDS, minute_prices[i], timestamps[i])

    # ===== EMA5 (last 15 minutes)
    ema_engine.values[EMA5_SECONDS] = None
    for i in range(len(minute_prices) - 15, len(minute_prices)):
        _update_single(ema_engine, EMA5_SECONDS, minute_prices[i], timestamps[i])

    # ===== EMA3 (last 9 minutes)
    ema_engine.values[EMA3_SECONDS] = None
    for i in range(len(minute_prices) - 9, len(minute_prices)):
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

        ema_engine.history[period].append(ema_engine.values[period])

        ema_engine.last_timestamp = timestamp
        ema_engine.timestamp_history.append(timestamp.timestamp())