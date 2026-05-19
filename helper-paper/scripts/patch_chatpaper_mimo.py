#!/usr/bin/env python3
"""Patch local ChatPaper so MiMo-compatible responses without response_ms do not fail."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from helper_paper_config import resolve_chatpaper_root

OLD = "response.response_ms / 1000.0"
NEW = '(getattr(response, "response_ms", 0) or 0) / 1000.0'
TARGET_FILES = ("chat_paper.py", "chat_translate.py")


def patch_file(path: Path, *, apply: bool, backup: bool) -> dict[str, str | bool]:
    if not path.is_file():
        return {"file": str(path), "exists": False, "patched": False, "status": "missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    if OLD not in text:
        status = "already_patched" if NEW in text else "pattern_not_found"
        return {"file": str(path), "exists": True, "patched": False, "status": status}
    if not apply:
        return {"file": str(path), "exists": True, "patched": False, "status": "needs_patch"}
    if backup:
        backup_path = path.with_suffix(path.suffix + ".helper-paper.bak")
        if not backup_path.exists():
            backup_path.write_text(text, encoding="utf-8")
    path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    return {"file": str(path), "exists": True, "patched": True, "status": "patched"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch ChatPaper response_ms handling for MiMo gateways.")
    parser.add_argument("--root", help="Local ChatPaper repository path. Explicit value overrides env/config defaults.")
    parser.add_argument("--check", action="store_true", help="Report whether patch is needed without writing. This is the default.")
    parser.add_argument("--apply", action="store_true", help="Actually patch the local ChatPaper checkout.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .helper-paper.bak files when applying.")
    args = parser.parse_args()

    root = resolve_chatpaper_root(args.root)
    if args.check and args.apply:
        parser.error("Use either --check or --apply, not both.")
    apply_patch = bool(args.apply)
    results = [patch_file(root / filename, apply=apply_patch, backup=not args.no_backup) for filename in TARGET_FILES]
    needs_patch = any(result["status"] == "needs_patch" for result in results)
    missing = any(result["status"] == "missing" for result in results)
    ambiguous = any(result["status"] == "pattern_not_found" for result in results)
    report = {
        "ok": not needs_patch and not missing and not ambiguous,
        "root": str(root),
        "check_only": not apply_patch,
        "applied": apply_patch,
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if missing:
        return 2
    if needs_patch:
        return 1
    if ambiguous:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
