__version__ = "1.0.1"

import json, os
from datetime import datetime
from config import *


def save_ema_state(ema_engine):
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "ema3": ema_engine.get(EMA3_SECONDS),
        "ema5": ema_engine.get(EMA5_SECONDS),
        "ema20": ema_engine.get(EMA20_SECONDS)
    }
    with open(EMA_FILE, "w") as f:
        json.dump(data, f)


def load_ema_state():
    if not os.path.exists(EMA_FILE):
        return None
    with open(EMA_FILE, "r") as f:
        return json.load(f)


def is_stale(state):
    d = datetime.strptime(state["timestamp"], "%Y-%m-%d").date()
    return (datetime.now().date() - d).days > EMA_MAX_STALENESS_DAYS
