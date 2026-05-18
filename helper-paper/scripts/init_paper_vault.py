#!/usr/bin/env python3
"""Initialize a generic Helper Paper Obsidian paper vault."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("check_paper_vault.py")
    cmd = [sys.executable, str(script), "--init", *sys.argv[1:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
