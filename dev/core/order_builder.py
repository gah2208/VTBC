__version__ = "1.0.1"
# Copyright 2026 Gregory Howard  all rights reserved.

def format_option_symbol(expiry, strike, right):
    strike_str = str(int(strike * 1000)).zfill(8)
    return f"SPXW {expiry}{right}{strike_str}"