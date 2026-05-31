# ✅ __version__ = "1.0.0"
# ✅ Copyright 2026 Gregory Howard. All rights reserved.


def restore_defaults(self):

    if not os.path.exists(DEFAULT_CONFIG_FILE):
        messagebox.showerror("Error", "config_default.py not found")
        return

    try:
        # ✅ load current config
        current = {}
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                m = re.match(r"(\w+)\s*=\s*(.+)", line)
                if m:
                    current[m.group(1)] = m.group(2).strip()

        # ✅ load default config
        defaults = {}
        with open(DEFAULT_CONFIG_FILE, "r") as f:
            for line in f:
                m = re.match(r"(\w+)\s*=\s*(.+)", line)
                if m:
                    defaults[m.group(1)] = m.group(2).strip()

        # ✅ PROTECTED KEYS (DO NOT OVERWRITE)
        protected = {
            "ACCOUNT_ID",
            "API_KEY",
            "REFRESH_TOKEN",
            "PUSHOVER_USER_KEY",
            "PUSHOVER_API_TOKEN",
            "ADMIN_PUSHOVER_USER_KEY",
            "ADMIN_PUSHOVER_API_TOKEN",
        }

        # ✅ merge logic
        final = {}

        for key in defaults:
            if key in protected and key in current:
                final[key] = current[key]
            else:
                final[key] = defaults[key]

        # ✅ write new config
        with open(CONFIG_FILE, "w") as f:
            for key, val in final.items():
                f.write(f"{key} = {val}\n")

        messagebox.showinfo(
            "Restored",
            "Defaults restored.\nCredentials preserved."
        )

        self.root.destroy()

    except Exception as e:
        messagebox.showerror("Error", str(e))