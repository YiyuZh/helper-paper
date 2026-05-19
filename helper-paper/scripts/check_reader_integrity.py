#!/usr/bin/env python3
"""Validate a helper-paper bilingual reader without modifying files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from helper_paper_config import secret_needles as configured_secret_needles


DEFAULT_SECRET_ENVS = (
    "MIMO_API_KEY",
    "XIAOMI_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)
REQUIRED_NOTE_FIELDS = (
    "paper_id",
    "provider",
    "model",
    "command",
    "api_status",
    "tool_status",
    "output_status",
    "failures",
    "review_notes",
)
SUCCESS_STATUSES = {"success", "ok", "ready", "completed"}
RELEASE_OUTPUT_STATUSES = {"validated_for_replacement", "final_replaced"}


def read_utf8(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8-sig"), None
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


def has_anchor(block: Any) -> bool:
    return isinstance(block, dict) and (
        bool(block.get("source_anchor"))
        or bool(block.get("page"))
        or bool(block.get("section"))
        or block.get("anchor_unavailable") is True
    )


def extract_notes_json(text: str) -> dict[str, Any] | None:
    match = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    candidate = match.group(1) if match else text
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def paper_original_by_block_id(paper_text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(
        r"## Block\s+\d+\s+`(?P<block_id>[^`]+)`.*?"
        r"\*\*Original:\*\*\s*(?P<original>.*?)(?=\n\s*\*\*中文翻译:\*\*)",
        flags=re.DOTALL,
    )
    for match in pattern.finditer(paper_text):
        result[match.group("block_id")] = normalize_text(match.group("original"))
    return result


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


def check_release_tool_status(notes: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    output_status = notes.get("output_status")
    if output_status not in RELEASE_OUTPUT_STATUSES:
        return issues
    tool_status = notes.get("tool_status")
    if not isinstance(tool_status, dict):
        return ["translation_notes.md tool_status must be an object"]

    required_tools = ("source_extraction", "gpt_academic", "chatpaper")
    for tool in required_tools:
        entry = tool_status.get(tool)
        if not isinstance(entry, dict):
            issues.append(f"translation_notes.md release tool missing object: {tool}")
            continue
        status = str(entry.get("status") or "").lower()
        if status not in SUCCESS_STATUSES:
            issues.append(f"translation_notes.md release tool not successful: {tool}")
        command = entry.get("command")
        if not isinstance(command, str) or not command.strip():
            issues.append(f"translation_notes.md release tool missing command: {tool}")
        if tool in {"gpt_academic", "chatpaper"}:
            revision = entry.get("upstream_revision") or entry.get("revision")
            if not isinstance(revision, str) or not revision.strip() or revision.strip().lower() == "unknown":
                issues.append(f"translation_notes.md release tool missing upstream revision: {tool}")
    return issues


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
        missing_anchors = sum(1 for block in blocks if not has_anchor(block))
        if missing_anchors:
            issues.append(f"source_blocks_missing_anchor_or_anchor_unavailable: {missing_anchors}")
        if paper_text:
            originals_by_id = paper_original_by_block_id(paper_text)
            missing_in_paper = [value for value in ids if value and value not in paper_text]
            if missing_in_paper:
                issues.append(f"source_block_ids_missing_from_paper_md: {len(missing_in_paper)}")
            hash_mismatches = 0
            missing_originals = 0
            for block in blocks:
                bid = block_id(block)
                if not bid:
                    continue
                expected_hash = block.get("sha256_16") if isinstance(block, dict) else None
                if not isinstance(expected_hash, str) or not expected_hash:
                    issues.append(f"source_block_missing_sha256_16: {bid}")
                    continue
                original_text = originals_by_id.get(bid)
                if original_text is None:
                    missing_originals += 1
                    continue
                actual_hash = hashlib.sha256(original_text.encode("utf-8")).hexdigest()[:16]
                if actual_hash != expected_hash:
                    hash_mismatches += 1
            if missing_originals:
                issues.append(f"source_block_original_text_missing_from_paper_md: {missing_originals}")
            if hash_mismatches:
                issues.append(f"source_block_hash_mismatch: {hash_mismatches}")

    if translation_notes.is_file():
        notes_text, error = read_utf8(translation_notes)
        if error:
            issues.append(f"translation_notes.md:{error}")
        else:
            notes = extract_notes_json(notes_text or "")
            if notes is None:
                issues.append("translation_notes.md missing parseable JSON audit block")
            else:
                missing = [field for field in REQUIRED_NOTE_FIELDS if field not in notes]
                if missing:
                    issues.append("translation_notes.md missing audit fields: " + ", ".join(missing))
                if not isinstance(notes.get("api_status"), dict):
                    issues.append("translation_notes.md api_status must be an object")
                if not isinstance(notes.get("tool_status"), dict):
                    issues.append("translation_notes.md tool_status must be an object")
                if not isinstance(notes.get("failures"), list):
                    issues.append("translation_notes.md failures must be a list")
                if not isinstance(notes.get("review_notes"), list):
                    issues.append("translation_notes.md review_notes must be a list")
                if notes.get("partial") is True and notes.get("output_status") not in {"partial_staging_generated", "partial"}:
                    issues.append("translation_notes.md partial output_status mismatch")
                issues.extend(check_release_tool_status(notes))

    if assets_dir.exists() and not assets_dir.is_dir():
        issues.append("assets exists but is not a directory")

    env_names = list(DEFAULT_SECRET_ENVS) + args.secret_env
    leaks = scan_secret_leaks(collect_text_files(reader), configured_secret_needles(tuple(env_names)))
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
