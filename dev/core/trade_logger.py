__version__ = "1.0.0"
# Copyright 2026 Gregory Howard  all rights reserved.

import csv
import os
from datetime import datetime
from build_manifest import BUILD_VERSION

FILE_NAME = "trade_log.csv"

HEADERS = [
    "timestamp",
    "event",
    "build",
    "spx_price",
    "direction",
    "K",
    "spread_width",
    "entry_price",
    "conversion_price",
    "order_id",
    "details"
]

def _ensure_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def log_event(event, spx_price, direction, K, W,
              entry_price=None, conversion_price=None,
              order_id=None, details=""):

    _ensure_file()

    row = [
        datetime.now().strftime("%H:%M:%S"),
        event,
        BUILD_VERSION,
        round(spx_price, 2) if spx_price else "",
        direction,
        K,
        W,
        entry_price if entry_price else "",
        conversion_price if conversion_price else "",
        order_id,
        details
    ]

    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)