#!/usr/bin/env python3
"""Validate a helper-paper bilingual reader without modifying files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_SECRET_ENVS = (
    "MIMO_API_KEY",
    "XIAOMI_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def read_utf8(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"not_utf8: {exc}"
    except OSError as exc:
        return None, f"unreadable: {exc}"


def source_blocks(source_map: Any) -> list[Any]:
    if isinstance(source_map, list):
        return source_map
    if isinstance(source_map, dict):
        for key in ("blocks", "source_blocks", "items", "segments"):
            value = source_map.get(key)
            if isinstance(value, list):
                return value
    return []


def block_id(block: Any) -> str | None:
    if not isinstance(block, dict):
        return None
    for key in ("block_id", "id", "source_id", "sid"):
        value = block.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def secret_needles(env_names: list[str]) -> list[str]:
    needles: set[str] = set()
    for name in env_names:
        value = os.environ.get(name)
        if not value or len(value) < 12:
            continue
        needles.add(value)
        if len(value) >= 24:
            needles.add(value[:12])
            needles.add(value[-12:])
    return sorted(needles, key=len, reverse=True)


def scan_secret_leaks(paths: list[Path], needles: list[str]) -> list[str]:
    leaks: list[str] = []
    if not needles:
        return leaks
    for path in paths:
        try:
            data = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for needle in needles:
            if needle and needle in data:
                digest = hashlib.sha256(needle.encode("utf-8")).hexdigest()[:12]
                leaks.append(f"{path.name}: secret-like value detected sha256:{digest}")
    return leaks


def collect_text_files(reader: Path) -> list[Path]:
    allowed = {".md", ".json", ".txt", ".log", ".ini"}
    return [path for path in reader.rglob("*") if path.is_file() and path.suffix.lower() in allowed]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check helper-paper reader integrity.")
    parser.add_argument("--reader", required=True, help="Reader directory containing paper.md and source_map.json.")
    parser.add_argument("--min-blocks", type=int, default=20, help="Minimum expected source blocks.")
    parser.add_argument(
        "--secret-env",
        action="append",
        default=[],
        help="Environment variable whose value must not appear in outputs. Can be repeated.",
    )
    args = parser.parse_args()

    reader = Path(args.reader)
    issues: list[str] = []
    warnings: list[str] = []

    if not reader.is_dir():
        print(json.dumps({"ok": False, "issues": [f"reader_not_directory: {reader}"]}, ensure_ascii=False, indent=2))
        return 1

    paper_md = reader / "paper.md"
    source_map_path = reader / "source_map.json"
    translation_notes = reader / "translation_notes.md"
    assets_dir = reader / "assets"

    for required in (paper_md, source_map_path, translation_notes):
        if not required.is_file():
            issues.append(f"missing_required_file: {required.name}")
        elif required.stat().st_size == 0:
            issues.append(f"empty_required_file: {required.name}")

    paper_text = ""
    if paper_md.is_file():
        paper_text, error = read_utf8(paper_md)
        if error:
            issues.append(f"paper.md:{error}")
            paper_text = ""

    if paper_text:
        if "Original" not in paper_text:
            issues.append("paper.md missing Original marker")
        if "中文翻译" not in paper_text and re.search(r"\*\*中文[:：]", paper_text) is None:
            issues.append("paper.md missing Chinese translation marker")
        if "source_map.json" not in paper_text:
            warnings.append("paper.md does not mention source_map.json")
        if "\ufffd" in paper_text:
            issues.append("paper.md contains replacement characters")
        if re.search(r"(^|\n)\s*\?{3,}\s*[:：]", paper_text):
            issues.append("paper.md contains corrupted ??? labels")
        original_count = len(re.findall(r"\bOriginal\b", paper_text))
        zh_count = paper_text.count("中文翻译") + len(re.findall(r"\*\*中文[:：]", paper_text))
        if original_count < args.min_blocks:
            issues.append(f"too_few_original_blocks: {original_count} < {args.min_blocks}")
        if zh_count < args.min_blocks:
            issues.append(f"too_few_chinese_blocks: {zh_count} < {args.min_blocks}")

    source_map: Any = None
    blocks: list[Any] = []
    if source_map_path.is_file():
        text, error = read_utf8(source_map_path)
        if error:
            issues.append(f"source_map.json:{error}")
        else:
            try:
                source_map = json.loads(text or "")
                blocks = source_blocks(source_map)
            except json.JSONDecodeError as exc:
                issues.append(f"source_map.json invalid_json: {exc}")

    if source_map is not None:
        if len(blocks) < args.min_blocks:
            issues.append(f"too_few_source_blocks: {len(blocks)} < {args.min_blocks}")
        ids = [block_id(block) for block in blocks]
        missing_ids = sum(1 for value in ids if not value)
        if missing_ids:
            issues.append(f"source_blocks_missing_ids: {missing_ids}")
        duplicate_ids = len([value for value in ids if value]) - len(set(value for value in ids if value))
        if duplicate_ids:
            issues.append(f"duplicate_source_block_ids: {duplicate_ids}")

    if translation_notes.is_file():
        notes, error = read_utf8(translation_notes)
        if error:
            issues.append(f"translation_notes.md:{error}")
        else:
            required_note_tokens = (
                "provider",
                "model",
                "command",
                "api_status",
                "tool_status",
                "failures",
                "review_notes",
            )
            missing_note_tokens = [token for token in required_note_tokens if token not in notes]
            if missing_note_tokens:
                issues.append("translation_notes.md missing audit fields: " + ", ".join(missing_note_tokens))
            if not any(token in notes for token in ("MiMo", "DeepSeek", "GPT Academic", "ChatPaper", "Translation", "deepseek", "mimo")):
                warnings.append("translation_notes.md lacks provider/tool status markers")

    if assets_dir.exists() and not assets_dir.is_dir():
        issues.append("assets exists but is not a directory")

    env_names = list(DEFAULT_SECRET_ENVS) + args.secret_env
    leaks = scan_secret_leaks(collect_text_files(reader), secret_needles(env_names))
    issues.extend(f"secret_leak: {item}" for item in leaks)

    report = {
        "ok": not issues,
        "reader": str(reader),
        "source_blocks": len(blocks),
        "issues": issues,
        "warnings": warnings,
        "secrets_printed": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
