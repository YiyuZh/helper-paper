#!/usr/bin/env python3
"""Release gate checks for the helper-paper GitHub package."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


TEXT_EXTS = {".md", ".txt", ".py", ".ps1", ".json", ".yaml", ".yml"}
TEXT_NAMES = {".gitignore", ".gitattributes"}
FORBIDDEN_NAMES = {".env", "apikey.ini", "translation_cache.json", "config.local.json"}
FORBIDDEN_EXTS = {".pdf", ".docx", ".pptx", ".xlsx"}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{24,}"),
    re.compile(r"tp-[A-Za-z0-9]{24,}"),
    re.compile(r"ghp_[A-Za-z0-9]{24,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"anthropic-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*[\"']?[A-Za-z0-9._-]{24,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{24,}"),
]
PERSONAL_PATH_PATTERNS = [
    re.compile(r"(?i)\b[A-Z]:\\Users\\[A-Za-z0-9._-]+\\"),
    re.compile(r"(?i)\b[A-Z]:\\sci\\commercial science\\commercialscience\\paper\b"),
]


def gitlink_issues(root: Path) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--stage"],
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception as exc:  # noqa: BLE001
        return [f"git ls-files failed: {exc}"]
    issues: list[str] = []
    for line in proc.stdout.splitlines():
        if line.startswith("160000 "):
            issues.append(f"gitlink detected: {line}")
    return issues


def git_tree_gitlink_issues(root: Path) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception:
        return []
    return [f"HEAD gitlink detected: {line}" for line in proc.stdout.splitlines() if line.startswith("160000 ")]


def git_status_issues(root: Path, *, allow_dirty: bool) -> list[str]:
    if allow_dirty:
        return []
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "-uall"],
            check=True,
            text=True,
            capture_output=True,
        )
    except Exception as exc:  # noqa: BLE001
        return [f"git status failed: {exc}"]
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if lines:
        preview = "; ".join(lines[:10])
        extra = f"; ... {len(lines) - 10} more" if len(lines) > 10 else ""
        return [f"working tree is not clean: {preview}{extra}"]
    return []


def tracked_file_issues(root: Path, rel_paths: list[str]) -> list[str]:
    issues: list[str] = []
    for rel in rel_paths:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", rel],
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            issues.append(f"required file is not tracked: {rel}")
    return issues


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS or path.name in TEXT_NAMES


def text_checks(root: Path) -> list[str]:
    issues: list[str] = []
    for path in root.rglob("*"):
        if ".git" in path.relative_to(root).parts:
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_EXTS:
            issues.append(f"forbidden packaged file: {rel}")
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in {"paper", "00_inbox", "03_notes", "04_full_readers"} for part in rel_parts):
            issues.append(f"possible vault data path: {rel}")
        if not is_text_file(path):
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            issues.append(f"NUL bytes: {rel}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(f"not UTF-8: {rel}: {exc}")
            continue
        if "\ufffd" in text:
            issues.append(f"replacement characters: {rel}")
        bad_fence = "`" * 5
        if bad_fence in text:
            issues.append(f"bad code fence: {rel}")
        if path.suffix.lower() == ".md" and text.count("```") % 2:
            issues.append(f"unbalanced code fences: {rel}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(f"secret-like value: {rel}")
                break
        for pattern in PERSONAL_PATH_PATTERNS:
            if pattern.search(text):
                issues.append(f"personal path pattern: {rel}: {pattern.pattern}")
    return issues


def required_file_list() -> list[str]:
    return [
        "README.md",
        "install.ps1",
        ".gitignore",
        ".gitattributes",
        "archive/example-env.md",
        "helper-paper/SKILL.md",
        "helper-paper/config.example.json",
        "helper-paper/agents/openai.yaml",
        "helper-paper/scripts/check_paper_vault.py",
        "helper-paper/scripts/init_paper_vault.py",
        "helper-paper/scripts/check_translation_providers.py",
        "helper-paper/scripts/run_translation_pipeline.py",
        "helper-paper/scripts/check_reader_integrity.py",
        "helper-paper/scripts/check_release_package.py",
        "helper-paper/scripts/helper_paper_config.py",
        "helper-paper/scripts/patch_chatpaper_mimo.py",
        "helper-paper/references/orchestration.md",
        "helper-paper/references/quality-rules.md",
        "helper-paper/references/reviewer-coach.md",
        "helper-paper/references/translation-failure-playbook.md",
        "wrapper-skills/gpt-academic/SKILL.md",
        "wrapper-skills/gpt-academic/agents/openai.yaml",
        "wrapper-skills/gpt-academic/references/usage.md",
        "wrapper-skills/chatpaper/SKILL.md",
        "wrapper-skills/chatpaper/agents/openai.yaml",
        "wrapper-skills/chatpaper/references/usage.md",
    ]


def required_files(root: Path) -> list[str]:
    required = required_file_list()
    return [rel for rel in required if not (root / rel).is_file()]


def installed_consistency_issues(root: Path, installed_skills_dir: str | None) -> list[str]:
    if not installed_skills_dir:
        return []
    installed = Path(installed_skills_dir)
    pairs = [
        ("helper-paper/SKILL.md", installed / "helper-paper" / "SKILL.md"),
        ("wrapper-skills/gpt-academic/SKILL.md", installed / "gpt-academic" / "SKILL.md"),
        ("wrapper-skills/chatpaper/SKILL.md", installed / "chatpaper" / "SKILL.md"),
    ]
    issues: list[str] = []
    for rel, installed_path in pairs:
        repo_path = root / rel
        if not installed_path.is_file():
            issues.append(f"installed skill missing: {installed_path}")
            continue
        if repo_path.read_bytes() != installed_path.read_bytes():
            issues.append(f"installed SKILL.md differs from repo: {installed_path}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check helper-paper release package.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--allow-dirty", action="store_true", help="Skip clean working tree and tracked-file checks for local development.")
    parser.add_argument("--installed-skills-dir", help="Optional Codex skills directory for installed SKILL.md consistency checks.")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    issues = []
    issues.extend(f"missing required file: {rel}" for rel in required_files(root))
    issues.extend(gitlink_issues(root))
    if not args.allow_dirty:
        issues.extend(git_tree_gitlink_issues(root))
    issues.extend(git_status_issues(root, allow_dirty=args.allow_dirty))
    if not args.allow_dirty:
        issues.extend(tracked_file_issues(root, required_file_list()))
    issues.extend(installed_consistency_issues(root, args.installed_skills_dir))
    issues.extend(text_checks(root))

    report = {"ok": not issues, "root": str(root), "issues": issues}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
