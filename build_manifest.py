__version__ = "1.0.10"
# ✅ Copyright 2026 Gregory Howard. All rights reserved.



# ============================================================
# NEW IMPLEMENTATION (ACTIVE CODE)
# ============================================================

from build_manifest import BUILD_VERSION, FILES
import re
import sys
import os


def extract_version(file_path):
    if not os.path.exists(file_path):
        return None, f"❌ MISSING FILE: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)

    if not match:
        return None, f"❌ VERSION NOT FOUND: {file_path}"

    return match.group(1), None


def run_build_check():
    print(f"✅ Expected Build Version: {BUILD_VERSION}")
    print()

    failures = []

    for name, data in FILES.items():
        file_path = data["path"]
        expected_version = data["version"]

        actual_version, error = extract_version(file_path)

        if error:
            print(error)
            failures.append(name)
            continue

        if actual_version != expected_version:
            print(f"❌ VERSION MISMATCH: {name}")
            print(f"   Expected: {expected_version}, Found: {actual_version}")
            failures.append(name)
        else:
            print(f"✅ {name}: {actual_version}")

    print()

    if failures:
        print("❌ BUILD FAILED")
        print(f"   Issues found in: {', '.join(failures)}")
        sys.exit(1)

    print("✅ BUILD VERIFIED")


if __name__ == "__main__":
    run_build_check()
