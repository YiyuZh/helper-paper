#!/usr/bin/env python3
"""Patch local ChatPaper so MiMo-compatible responses without response_ms do not fail."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_CHATPAPER_ROOT = r"E:\skills\external-tools\ChatPaper"
OLD = "response.response_ms / 1000.0"
NEW = '(getattr(response, "response_ms", 0) or 0) / 1000.0'
TARGET_FILES = ("chat_paper.py", "chat_translate.py")


def patch_file(path: Path, *, check: bool) -> dict[str, str | bool]:
    if not path.is_file():
        return {"file": str(path), "exists": False, "patched": False, "status": "missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    if OLD not in text:
        status = "already_patched" if NEW in text else "pattern_not_found"
        return {"file": str(path), "exists": True, "patched": False, "status": status}
    if check:
        return {"file": str(path), "exists": True, "patched": False, "status": "needs_patch"}
    path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    return {"file": str(path), "exists": True, "patched": True, "status": "patched"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch ChatPaper response_ms handling for MiMo gateways.")
    parser.add_argument("--root", default=DEFAULT_CHATPAPER_ROOT, help="Local ChatPaper repository path.")
    parser.add_argument("--check", action="store_true", help="Report whether patch is needed without writing.")
    args = parser.parse_args()

    root = Path(args.root)
    results = [patch_file(root / filename, check=args.check) for filename in TARGET_FILES]
    needs_patch = any(result["status"] == "needs_patch" for result in results)
    missing = any(result["status"] == "missing" for result in results)
    report = {
        "ok": not needs_patch and not missing,
        "root": str(root),
        "check_only": args.check,
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if missing:
        return 2
    if needs_patch:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

