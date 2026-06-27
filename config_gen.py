# config_gen.py
__version__ = "1.0.0"
# Copyright 2026 Gregory Howard  all rights reserved.

# AUTO-GENERATED CONFIG GENERATOR
# Generates a compatibility config.py from admin_config_default.json + config.json
# Writes atomically to avoid partial imports.

from pathlib import Path
import json
from typing import Any, Dict

# Use the project's config_loader to produce the canonical merged config
from config_loader import load_merged_config

BASE_DIR = Path(__file__).parent
TARGET = BASE_DIR / "config.py"


def _render_py(merged: Dict[str, Any]) -> str:
    lines = []
    lines.append("# AUTO-GENERATED — DO NOT EDIT")
    lines.append("from typing import Any, Dict")
    lines.append("")
    # Dump CONFIG as a JSON-like Python literal for readability
    lines.append("CONFIG: Dict[str, Any] = " + json.dumps(merged, indent=4))
    lines.append("")
    # Export flat names for legacy imports
    for k, v in merged.items():
        # Represent value as a Python literal using repr
        lines.append(f"{k} = {repr(v)}")
    lines.append("")
    lines.append("__all__ = ['CONFIG'] + " + repr(list(merged.keys())))
    return "\n".join(lines) + "\n"


def generate_config_py(target_path: Path | None = None) -> None:
    """
    Generate config.py atomically from the merged JSON config.
    """
    if target_path is None:
        target_path = TARGET

    merged = load_merged_config()

    content = _render_py(merged)

    tmp = target_path.with_suffix(".py.tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target_path)
