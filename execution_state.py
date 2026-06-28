__version__ = "1.1.0"
# Copyright 2026 Gregory Howard  all rights reserved.

from enum import Enum
from datetime import datetime, timedelta

# NEW: Import ORDER_TIMEOUT from config
from config_loader import load_merged_config

_cfg = load_merged_config()
ORDER_TIMEOUT = _cfg.get("ORDER_TIMEOUT", 180)

class State(Enum):
    IDLE = 0
    LONG_WORKING = 1
    CONVERSION_WORKING = 2

class ExecutionState:
    def __init__(self):
        self.state = State.IDLE
        self.order_id = None
        self.deadline = None
        self.short_strike = None
        self.hedge_strike = None
        self.qty = 0
        self.direction = None
        self.entry_price = None
        self.active_positions = []

    def submit_long(self, oid, long_strike, short_strike, qty, direction, price):
        self.state = State.LONG_WORKING
        self.order_id = oid
        self.short_strike = long_strike
        self.hedge_strike = short_strike
        self.qty = qty
        self.direction = direction
        self.entry_price = price
        # NEW: Use ORDER_TIMEOUT from config instead of hard-coded 180
        self.deadline = datetime.now() + timedelta(seconds=ORDER_TIMEOUT)

    def check_long(self, status):
        if status == "FILLED":
            return "FILLED"
        if datetime.now() >= self.deadline:
            return "CANCEL"
        return "WAIT"

    def submit_conversion(self, oid):
        self.state = State.CONVERSION_WORKING
        self.order_id = oid
        # NEW: Use ORDER_TIMEOUT from config instead of hard-coded 180
        self.deadline = datetime.now() + timedelta(seconds=ORDER_TIMEOUT)

    def check_conversion(self, status):
        if status == "FILLED":
            return "DONE"
        return "WAIT"

    def add_position(self, direction, long_strike, short_strike):
        self.active_positions.append({
            "direction": direction,
            "long_strikes": [long_strike],
            "short_strikes": [short_strike],
            "base_short": short_strike
        })

    def count_active(self, direction):
        return sum(1 for p in self.active_positions if p.get("direction") == direction)

    def get_active_positions(self):
        return list(self.active_positions)
