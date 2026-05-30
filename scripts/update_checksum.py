# ✅ __version__ = "1.1.2"
# ✅ Copyright 2026 Gregory Howard. All rights reserved.
# ✅ VTBC CHECKSUM UPDATE SCRIPT

import hashlib
import os
import re
import sys

# ---------------------------
# PATHS (RELATIVE TO REPO ROOT)
# ---------------------------
EXE_PATH = os.path.join("dist", "main.exe")
CHECKSUM_FILE = os.path.join("dev", "checksum.py")


# ---------------------------
# CALCULATE SHA256
# ---------------------------
def calculate_sha256(path):
    if not os.path.exists(path):
        print(f"❌ ERROR: File not found: {path}")
        sys.exit(1)

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# ---------------------------
# UPDATE checksum.py
# ---------------------------
def update_checksum_file(new_hash):
    if not os.path.exists(CHECKSUM_FILE):
        print(f"❌ ERROR: checksum file not found: {CHECKSUM_FILE}")
        sys.exit(1)

    with open(CHECKSUM_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace ONLY the expected checksum line
    pattern = r'EXPECTED_CHECKSUM\s*=\s*"[a-fA-F0-9]+"'

    if not re.search(pattern, content):
        print("❌ ERROR: EXPECTED_CHECKSUM not found in checksum.py")
        sys.exit(1)

    updated = re.sub(
        pattern,
        f'EXPECTED_CHECKSUM = "{new_hash}"',
        content
    )

    with open(CHECKSUM_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

    print("✅ checksum.py updated with new hash:")
    print(f"   {new_hash}")


# ---------------------------
# MAIN ENTRY
# ---------------------------
def main():
    print("Computing checksum...")

    new_hash = calculate_sha256(EXE_PATH)

    print("Updating checksum.py...")
    update_checksum_file(new_hash)

    print("✅ Checksum update complete.")


if __name__ == "__main__":
    main()