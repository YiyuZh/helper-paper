#!/usr/bin/env python3
"""Shared path/config resolution for Helper Paper scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG = SKILL_ROOT / "config.local.json"
EXAMPLE_CONFIG = SKILL_ROOT / "config.example.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _expand_path(value: str) -> Path:
    return Path(os.path.expandvars(value)).expanduser()


def config_value(key: str) -> Any:
    for path in (LOCAL_CONFIG, EXAMPLE_CONFIG):
        data = _read_json(path)
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def resolve_vault_root(explicit: str | None = None) -> Path:
    if explicit:
        return _expand_path(explicit)
    env_value = os.environ.get("HELPER_PAPER_VAULT_ROOT")
    if env_value:
        return _expand_path(env_value)
    value = config_value("vault_root")
    if isinstance(value, str) and value:
        return _expand_path(value)
    return Path("paper")


def resolve_external_tools_root(explicit: str | None = None) -> Path:
    if explicit:
        return _expand_path(explicit)
    env_value = os.environ.get("HELPER_PAPER_EXTERNAL_TOOLS_ROOT")
    if env_value:
        return _expand_path(env_value)
    value = config_value("external_tools_root")
    if isinstance(value, str) and value:
        return _expand_path(value)
    return Path.home() / "helper-paper-external-tools"


def resolve_chatpaper_root(explicit: str | None = None) -> Path:
    return resolve_external_tools_root(explicit=None) / "ChatPaper" if not explicit else _expand_path(explicit)
