__version__ = "1.0.3"

# copyright (c) Gregory Howard  2026  all rights reserved

# ============================================================
#  ORIGINAL CODE (PRESERVED AND COMMENTED OUT)
# ============================================================

# import json, os
# from datetime import datetime
# from config import *
#
# def save_ema_state(ema_engine):
#     data = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d"),
#         "ema3": ema_engine.get(EMA3_SECONDS),
#         "ema5": ema_engine.get(EMA5_SECONDS),
#         "ema20": ema_engine.get(EMA20_SECONDS)
#     }
#     with open(EMA_FILE, "w") as f:
#         json.dump(data, f)
#
#
# def load_ema_state():
#     if not os.path.exists(EMA_FILE):
#         return None
#     with open(EMA_FILE, "r") as f:
#         return json.load(f)
#
#
# def is_stale(state):
#     d = datetime.strptime(state["timestamp"], "%Y-%m-%d").date()
#     return (datetime.now().date() - d).days > EMA_MAX_STALENESS_DAYS


# ============================================================
#  NEW IMPLEMENTATION (ACTIVE CODE)
# ============================================================

import json
import os
from datetime import datetime

# NEW CONSTANTS IMPORT
from ema_constants import EMA3_SECONDS, EMA5_SECONDS, EMA20_SECONDS

# NEW: Import from config_loader instead of config module
from config_loader import load_merged_config

_cfg = load_merged_config()
EMA_FILE = _cfg.get("EMA_FILE", "ema_state.json")
EMA_MAX_STALENESS_DAYS = _cfg.get("EMA_MAX_STALENESS_DAYS", 1)

# OLD CONFIG IMPORT (COMMENTED OUT)
# from config import EMA_FILE, EMA_MAX_STALENESS_DAYS


def save_ema_state(ema_engine):
    """
    Save EMA3/EMA5/EMA20 values to disk.

    Timestamp is date-only because EMAs are anchored at the start of each day.
    """

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "ema3": ema_engine.get(EMA3_SECONDS),
        "ema5": ema_engine.get(EMA5_SECONDS),
        "ema20": ema_engine.get(EMA20_SECONDS)
    }

    with open(EMA_FILE, "w") as f:
        json.dump(data, f)


def load_ema_state():
    """
    Load EMA state from disk if it exists.
    """

    if not os.path.exists(EMA_FILE):
        return None

    with open(EMA_FILE, "r") as f:
        return json.load(f)


def is_stale(state):
    """
    Determine if the saved EMA state is too old to use.

    EMA_MAX_STALENESS_DAYS is still config-driven.
    """

    saved_date = datetime.strptime(state["timestamp"], "%Y-%m-%d").date()
    age_days = (datetime.now().date() - saved_date).days

    return age_days > EMA_MAX_STALENESS_DAYS
