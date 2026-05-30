__version__ = "1.2.0"
# Copyright 2026 Gregory Howard  all rights reserved.

from config import EMA_SLOPE_LOOKBACK_SECONDS, NOISE_3_5, NOISE_5_20


def compute_time_slope(values, timestamps, lookback_seconds):
    """
    Time-based slope:
    slope = (value_now - value_past) / time_delta
    """

    if len(values) < 2 or len(timestamps) < 2:
        return 0.0

    now_time = timestamps[-1]
    target_time = now_time - lookback_seconds

    idx = 0
    for i in range(len(timestamps) - 1, -1, -1):
        if timestamps[i] <= target_time:
            idx = i
            break

    dt = now_time - timestamps[idx]

    if dt <= 0:
        return 0.0

    return (values[-1] - values[idx]) / dt


def compute_time_normalized_noise(series_a, series_b, timestamps, lookback_seconds):
    """
    Noise = absolute difference of EMAs normalized per unit time
    """

    if len(series_a) < 2 or len(series_b) < 2:
        return 0.0

    now_time = timestamps[-1]
    target_time = now_time - lookback_seconds

    idx = 0
    for i in range(len(timestamps) - 1, -1, -1):
        if timestamps[i] <= target_time:
            idx = i
            break

    dt = now_time - timestamps[idx]

    if dt <= 0:
        return 0.0

    diff_now = abs(series_a[-1] - series_b[-1])
    diff_past = abs(series_a[idx] - series_b[idx])

    # rate of change of spread (noise per second)
    return abs(diff_now - diff_past) / dt


def evaluate_trade(spx_price, surface, ema_engine):

    keys = list(ema_engine.get_all().keys())

    if len(keys) < 3:
        return None

    k3, k5, k20 = keys[0], keys[1], keys[2]

    ema3 = ema_engine.get(k3)
    ema5 = ema_engine.get(k5)
    ema20 = ema_engine.get(k20)

    if ema3 is None or ema5 is None or ema20 is None:
        return None

    history3 = ema_engine.history[k3]
    history5 = ema_engine.history[k5]
    history20 = ema_engine.history[k20]

    timestamps = ema_engine.timestamp_history

    # ✅ TIME-BASED SLOPES
    slope3 = compute_time_slope(history3, timestamps, EMA_SLOPE_LOOKBACK_SECONDS)
    slope5 = compute_time_slope(history5, timestamps, EMA_SLOPE_LOOKBACK_SECONDS)
    slope20 = compute_time_slope(history20, timestamps, EMA_SLOPE_LOOKBACK_SECONDS)

    # ✅ TIME-NORMALIZED NOISE FILTERS
    noise_3_5 = compute_time_normalized_noise(
        history3, history5, timestamps, EMA_SLOPE_LOOKBACK_SECONDS
    )

    noise_5_20 = compute_time_normalized_noise(
        history5, history20, timestamps, EMA_SLOPE_LOOKBACK_SECONDS
    )

    # ===== CALL CONDITIONS =====
    if ema3 > ema5 and ema5 > ema20:
        if slope3 > 0 and slope5 > 0:
            if noise_3_5 < NOISE_3_5 and noise_5_20 < NOISE_5_20:
                return {"direction": "C"}

    # ===== PUT CONDITIONS =====
    if ema3 < ema5 and ema5 < ema20:
        if slope3 < 0 and slope5 < 0:
            if noise_3_5 < NOISE_3_5 and noise_5_20 < NOISE_5_20:
                return {"direction": "P"}

    return None