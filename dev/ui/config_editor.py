__version__ = "1.2.0"

import tkinter as tk
from tkinter import ttk, messagebox
import re
import sys
import os
import shutil

# ===== EXE SAFE PATH =====
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.py")
DEFAULT_CONFIG_FILE = os.path.join(BASE_DIR, "config_default.py")

ADMIN_MODE = "--admin" in sys.argv

FONT = ("Segoe UI", 14)
TAB_FONT = ("Segoe UI", 14, "bold")

# ===== FIELD DEFINITIONS =====
FIELDS = {
    "ACCOUNTS": [
        ("ACCOUNT_CAPITAL", "ACCOUNT_CAPITAL", False, "Total account size"),
        ("BROKER_ACCOUNT_ID", "ACCOUNT_ID", False, "Broker account"),
        ("BROKER_API_KEY", "API_KEY", False, "API key"),
        ("BROKER_REFRESH_TOKEN", "REFRESH_TOKEN", False, "Refresh token"),
        ("ENABLE_TRADING", "ENABLE_TRADING", False, "Enable trading"),
        ("PUSHOVER_USER_KEY", "PUSHOVER_USER_KEY", False, "User key"),
        ("PUSHOVER_API_TOKEN", "PUSHOVER_API_TOKEN", False, "API token"),
        ("ADMIN_PUSHOVER_USER_KEY", "ADMIN_PUSHOVER_USER_KEY", True, "Admin key"),
        ("ADMIN_PUSHOVER_API_TOKEN", "ADMIN_PUSHOVER_API_TOKEN", True, "Admin token"),
        ("PUSHOVER_ENABLED", "PUSHOVER_ENABLED", False, "Notifications"),
        ("WINDOWS_ALERT_ENABLED", "WINDOWS_ALERT_ENABLED", False, "Popup alerts"),
    ],

    "ORDERS": [
        ("POSITIONS", "POSITIONS", False, "≥1 = contracts | <1 = % capital (e.g. 0.05 = 5%)"),
        ("MIN_EXPECTED_MOVE", "MIN_EM", False, ""),
        ("MAX_PREMIUM", "MAX_PREMIUM", False, ""),
        ("PROFIT_MULTIPLIER", "PROFIT_MULTIPLIER", False, ""),
        ("SPREAD_WIDTH", "CONVERSION_WIDTH", False, ""),
        ("SLIPPAGE", "SLIPPAGE", False, ""),
        ("BID_ASK_SPREAD", "BID_ASK_SPREAD", False, ""),
        ("STRIKE_STEP", "STRIKE_STEP", True, ""),
        ("STRIKE_RANGE", "STRIKE_RANGE", True, ""),
        ("MAX_CALLS_ACTIVE", "MAX_CALLS_ACTIVE", True, ""),
        ("MAX_PUTS_ACTIVE", "MAX_PUTS_ACTIVE", True, ""),
    ],

    "TIMING": [
        ("MARKET_OPEN_TIME", "MARKET_OPEN_TIME", False, ""),
        ("TRADE_START_TIME", "TRADE_START_TIME", False, ""),
        ("STOP_NEW_ENTRIES", "STOP_NEW_ENTRIES", False, ""),
        ("FORCE_EXIT_TIME", "FORCE_EXIT_TIME", False, ""),
        ("FORCE_EXIT_ENABLED", "FORCE_EXIT_ENABLED", False, ""),
        ("ORDER_TIMEOUT_SECONDS", "ORDER_TIMEOUT_SECONDS", True, ""),
        ("LOOP_SLEEP_SECONDS", "LOOP_SLEEP_SECONDS", False, ""),
        ("HEARTBEAT_INTERVAL_SECONDS", "HEARTBEAT_INTERVAL_SECONDS", True, ""),
    ],

    "EMA": [
        ("EMA3_SECONDS", "EMA3_SECONDS", False, ""),
        ("EMA5_SECONDS", "EMA5_SECONDS", False, ""),
        ("EMA20_SECONDS", "EMA20_SECONDS", False, ""),
        ("NOISE_3_5", "NOISE_3_5", False, ""),
        ("NOISE_5_20", "NOISE_5_20", False, ""),
        ("EMA_SLOPE_LOOKBACK_SECONDS", "EMA_SLOPE_LOOKBACK_SECONDS", True, ""),
        ("EMA20_ADJUSTMENT", "EMA20_ADJUSTMENT", True, ""),
        ("EMA_MAX_STALENESS_DAYS", "EMA_MAX_STALENESS_DAYS", True, ""),
        ("EMA_FILE", "EMA_FILE", True, ""),
    ],

    "RETRIES": [
        ("ORDER_RETRY_ATTEMPTS", "ORDER_RETRY_ATTEMPTS", False, ""),
        ("TOKEN_REFRESH_DELAY", "TOKEN_REFRESH_DELAY", False, ""),
        ("DATA_RETRY_ATTEMPTS", "DATA_RETRY_ATTEMPTS", False, ""),
        ("DATA_RETRY_DELAY", "DATA_RETRY_DELAY", False, ""),
        ("MAX_API_FAILURES", "MAX_API_FAILURES", False, ""),
    ]
}

# ===== LOAD CONFIG (WITH VALIDATION) =====
def load_config():

    if not os.path.exists(DEFAULT_CONFIG_FILE):
        messagebox.showerror("Error", "config_default.py not found")
        sys.exit(1)

    defaults = {}
    with open(DEFAULT_CONFIG_FILE) as f:
        for line in f:
            m = re.match(r"(\w+)\s*=\s*(.+)", line)
            if m:
                defaults[m.group(1)] = m.group(2).strip()

    if not os.path.exists(CONFIG_FILE):
        shutil.copyfile(DEFAULT_CONFIG_FILE, CONFIG_FILE)

    current = {}

    with open(CONFIG_FILE) as f:
        for line in f:
            m = re.match(r"(\w+)\s*=\s*(.+)", line)
            if m:
                current[m.group(1)] = m.group(2).strip()

    updated = False

    for key, default_val in defaults.items():

        if key not in current:
            current[key] = default_val
            updated = True
            continue

        val = current[key]

        try:
            # POSITIONS special handling
            if key == "POSITIONS":
                num = float(val.strip('"'))
                if num <= 0:
                    raise Exception()
                if num >= 1 and not num.is_integer():
                    raise Exception()

            elif key.endswith("_TIME"):
                if not re.match(r"^\d{2}:\d{2}:\d{2}$", val.strip('"')):
                    raise Exception()

            elif val in ["True", "False"]:
                pass

            elif re.match(r"^-?\d+(\.\d+)?$", val.strip('"')):
                pass

        except:
            current[key] = default_val
            updated = True

    if updated:
        with open(CONFIG_FILE, "w") as f:
            for k, v in current.items():
                f.write(f"{k} = {v}\n")

    values = {}
    for k, v in current.items():
        val = v.strip()
        if (val.startswith('"') and val.endswith('"')):
            val = val[1:-1]
        values[k] = val

    return values


# ===== SAVE =====
def save_config(values):

    with open(CONFIG_FILE, "w") as f:
        for k, v in values.items():
            if v.lower() in ["true", "false"]:
                f.write(f"{k} = {v.capitalize()}\n")
            elif re.match(r"^-?\d+(\.\d+)?$", v):
                f.write(f"{k} = {v}\n")
            else:
                f.write(f'{k} = "{v}"\n')


class ConfigEditor:

    def __init__(self, root):

        self.root = root
        self.root.state("zoomed")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook.Tab", font=TAB_FONT,
            background="black", foreground="white")

        self.values = load_config()
        self.entries = {}

        nb = ttk.Notebook(root)
        nb.pack(expand=True, fill="both")

        for tab, fields in FIELDS.items():

            frame = ttk.Frame(nb)
            nb.add(frame, text=tab)

            row = 0

            for display, key, admin, desc in fields:

                if admin and not ADMIN_MODE:
                    continue

                tk.Label(frame, text=display, font=FONT)\
                    .grid(row=row, column=0, padx=10, pady=5, sticky="w")

                entry = tk.Entry(frame, font=FONT)
                entry.insert(0, self.values.get(key, ""))
                entry.grid(row=row, column=1, padx=10)

                tk.Label(frame, text=desc, font=FONT, fg="gray")\
                    .grid(row=row, column=2, padx=10, sticky="w")

                # ✅ POSITIONS UI enhancement
                if key == "POSITIONS":

                    hint = tk.Label(frame,
                        text="Example: 2 (contracts) or 0.05 (5% capital)",
                        font=("Segoe UI", 11),
                        fg="gray"
                    )
                    hint.grid(row=row, column=3, padx=10, sticky="w")

                    def validate_positions(e):
                        val = e.widget.get()
                        try:
                            num = float(val)
                            if num <= 0 or (num >= 1 and not num.is_integer()):
                                raise Exception()
                            e.widget.config(bg="white")
                        except:
                            e.widget.config(bg="#ffecec")

                    entry.bind("<KeyRelease>", validate_positions)

                self.entries[key] = entry
                row += 1

            tk.Button(frame, text="SAVE", font=FONT,
                      command=self.save).grid(row=row, column=0, pady=15)

            tk.Button(frame, text="CANCEL", font=FONT,
                      command=self.root.destroy).grid(row=row, column=1)

            tk.Button(frame, text="RESTORE DEFAULTS", font=FONT,
                      command=self.restore_defaults).grid(row=row, column=2)


    def save(self):

        vals = {k: e.get() for k, e in self.entries.items()}
        save_config(vals)
        messagebox.showinfo("Saved", "Config updated.")


    def restore_defaults(self):

        current = {}
        with open(CONFIG_FILE) as f:
            for line in f:
                m = re.match(r"(\w+)\s*=\s*(.+)", line)
                if m:
                    current[m.group(1)] = m.group(2)

        defaults = {}
        with open(DEFAULT_CONFIG_FILE) as f:
            for line in f:
                m = re.match(r"(\w+)\s*=\s*(.+)", line)
                if m:
                    defaults[m.group(1)] = m.group(2)

        protected = {
            "ACCOUNT_ID","API_KEY","REFRESH_TOKEN",
            "PUSHOVER_USER_KEY","PUSHOVER_API_TOKEN",
            "ADMIN_PUSHOVER_USER_KEY","ADMIN_PUSHOVER_API_TOKEN"
        }

        final = {}

        for k in defaults:
            final[k] = current[k] if k in protected and k in current else defaults[k]

        with open(CONFIG_FILE, "w") as f:
            for k,v in final.items():
                f.write(f"{k} = {v}\n")

        messagebox.showinfo("Restored",
            "Defaults restored (credentials preserved)")

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ConfigEditor(root)
    root.mainloop()