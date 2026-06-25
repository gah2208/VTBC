__version__ = "1.4.0"

# Copyright 2026 Gregory Howard  all rights reserved.

from config import NOISE_3_5, NOISE_5_20


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

    if len(history3) < 3:
        return None

    ema3_prev = history3[-3]  # EMA3(t-2)

    # ===== CALL CONDITIONS =====
    if ema3 > ema5 > ema20:
        if ema3 > ema3_prev:
            if (ema3 - ema5) > NOISE_3_5 and (ema5 - ema20) > NOISE_5_20:
                return {"direction": "C"}

    # ===== PUT CONDITIONS =====
    if ema3 < ema5 < ema20:
        if ema3 < ema3_prev:
            if (ema5 - ema3) > NOISE_3_5 and (ema20 - ema5) > NOISE_5_20:
                return {"direction": "P"}

    return None

