__version__ = "1.0.1"
# Copyright 2026 Gregory Howard  all rights reserved.

from enum import Enum
from datetime import datetime, timedelta

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
        self.qty = 0
        self.direction = None
        self.entry_price = None

    def submit_long(self, oid, strike, qty, direction, price):
        self.state = State.LONG_WORKING
        self.order_id = oid
        self.short_strike = strike
        self.qty = qty
        self.direction = direction
        self.entry_price = price
        self.deadline = datetime.now() + timedelta(seconds=180)

    def check_long(self, status):
        if status == "FILLED":
            return "FILLED"
        if datetime.now() >= self.deadline:
            return "CANCEL"
        return "WAIT"

    def submit_conversion(self, oid):
        self.state = State.CONVERSION_WORKING
        self.order_id = oid
        self.deadline = datetime.now() + timedelta(seconds=180)

    def check_conversion(self, status):
        if status == "FILLED":
            return "DONE"
        return "WAIT"
