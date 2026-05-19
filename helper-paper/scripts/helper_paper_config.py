#!/usr/bin/env python3
"""Shared path/config resolution for Helper Paper scripts."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG = SKILL_ROOT / "config.local.json"
EXAMPLE_CONFIG = SKILL_ROOT / "config.example.json"
DEFAULT_SECRET_ENVS = (
    "MIMO_API_KEY",
    "XIAOMI_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)
SECRET_LIKE_PATTERNS = (
    re.compile(r"\b(?:sk|tp|ak|xai|sk-or-v1)-[A-Za-z0-9._-]{16,}\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{16,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*[\"']?[A-Za-z0-9._-]{16,}"),
)


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


def windows_user_env(name: str) -> str | None:
    if os.name != "nt":
        return None
    try:
        import winreg  # type: ignore[import-not-found]

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        if isinstance(value, str) and value:
            return value
    except OSError:
        return None
    return None


def env_value(name: str) -> str | None:
    return os.environ.get(name) or windows_user_env(name)


def first_env(names: tuple[str, ...]) -> tuple[str | None, str | None]:
    for name in names:
        value = env_value(name)
        if value:
            return name, value
    return None, None


def collect_secret_values(env_names: tuple[str, ...] = DEFAULT_SECRET_ENVS) -> list[str]:
    values: set[str] = set()
    for name in env_names:
        value = env_value(name)
        if value and len(value) >= 12:
            values.add(value)
    return sorted(values, key=len, reverse=True)


def secret_needles(env_names: tuple[str, ...] = DEFAULT_SECRET_ENVS) -> list[str]:
    needles: set[str] = set()
    for value in collect_secret_values(env_names):
        needles.add(value)
        if len(value) >= 24:
            needles.add(value[:12])
            needles.add(value[-12:])
    return sorted(needles, key=len, reverse=True)


def redact_text(text: str, secrets: list[str] | None = None) -> str:
    redacted = text
    for secret in secrets if secrets is not None else collect_secret_values():
        if secret:
            redacted = redacted.replace(secret, "[REDACTED_SECRET]")
    for pattern in SECRET_LIKE_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def redact_data(value: Any, secrets: list[str] | None = None) -> Any:
    if isinstance(value, str):
        return redact_text(value, secrets)
    if isinstance(value, list):
        return [redact_data(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: redact_data(item, secrets) for key, item in value.items()}
    return value


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


def resolve_codex_skills_dir(explicit: str | None = None) -> Path:
    if explicit:
        return _expand_path(explicit)
    env_value_raw = os.environ.get("HELPER_PAPER_CODEX_SKILLS_DIR")
    if env_value_raw:
        return _expand_path(env_value_raw)
    value = config_value("codex_skills_dir")
    if isinstance(value, str) and value:
        return _expand_path(value)
    return Path.home() / ".codex" / "skills"
