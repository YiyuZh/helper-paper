#!/usr/bin/env python3
"""Read-only validator for the Helper Paper Obsidian vault."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


DEFAULT_ROOT = r"E:\sci\commercial science\commercialscience\paper"

REQUIRED_DIRS = [
    "00_inbox",
    "01_candidates",
    "02_daily",
    "03_notes",
    "04_full_readers",
    "05_reviewer_coach",
    "98_system",
    "99_templates",
]

REQUIRED_FILES = [
    "000_开始这里.md",
    "paper_daily_orchestration_memory.md",
    r"02_daily\carry_over_todo.md",
    r"98_system\README_paper_system.md",
    r"98_system\README_inbox.md",
    r"98_system\README_reviewer_coach.md",
    r"99_templates\每日启动模板.md",
    r"99_templates\精读一篇模板.md",
    r"05_reviewer_coach\reviewer_learning_memory.md",
    r"05_reviewer_coach\paper_real_learn_for_warn.md",
    r"05_reviewer_coach\reviewer_coach_agent_prompt.md",
    r"00_inbox\pdfs\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud.pdf",
    r"00_inbox\pdfs\P4_2024_NAACL_Groundedness_in_RAG_Long-form_Generation.pdf",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\paper.md",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\source_map.json",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\translation_notes.md",
]

REQUIRED_TEXT = {
    "paper_daily_orchestration_memory.md": [
        "P1 已生成第一轮 AI 导读",
        "P1 中英对照 reader",
        "用户个人阅读状态：未完成",
        "P4",
        "WARN-001",
        "WARN-004",
        "paper_real_learn_for_warn.md",
    ],
    "000_开始这里.md": [
        "开始这里",
        "今天先读：P1",
        "P1 中英对照 reader",
        "请检查我的理解",
        "图谱只显示 `paper/03_notes/`",
        "读完对我说什么",
        "没读完对我说什么",
        "未完成事项",
    ],
    r"02_daily\carry_over_todo.md": [
        "未完成事项",
        "当前未完成",
        "中英对照 reader",
        "读到哪里",
    ],
    r"03_notes\2026-05-16_P1_Conversational-AI-Technical-Interview-Think-Aloud.md": [
        "我的阅读理解与导师斧正",
        "导师检查状态：未检查",
        "P1 我已完成全文阅读和理解检查",
    ],
    r"05_reviewer_coach\reviewer_learning_memory.md": [
        "WARN-001",
        "WARN-002",
        "WARN-003",
        "0/5",
    ],
    r"99_templates\精读一篇模板.md": [
        "含金量卡",
        "我的阅读理解与导师斧正",
        "导师斧正记录",
        "审稿人教练",
        "我注意到了",
    ],
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\paper.md": [
        "**Original:**",
        "source_map.json",
    ],
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\translation_notes.md": [
        "Translation",
        "Personal notes",
    ],
}

ALTERNATIVE_TEXT = {
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\paper.md": [
        ["**中文:**", "**中文翻译:**", "**中文翻译：**", "**中文：**"],
    ],
}

REQUIRED_NONEMPTY_FILES = [
    r"00_inbox\pdfs\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud.pdf",
    r"00_inbox\pdfs\P4_2024_NAACL_Groundedness_in_RAG_Long-form_Generation.pdf",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\paper.md",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\source_map.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Helper Paper vault structure without modifying files."
    )
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Paper vault root path.")
    args = parser.parse_args()

    root = Path(args.root)
    missing_dirs: list[str] = []
    missing_files: list[str] = []
    missing_text: list[str] = []
    empty_files: list[str] = []
    invalid_pdfs: list[str] = []
    unreadable: list[str] = []

    if not root.exists():
        print(f"[FAIL] Vault root does not exist: {root}")
        return 1
    if not root.is_dir():
        print(f"[FAIL] Vault root is not a directory: {root}")
        return 1

    for rel in REQUIRED_DIRS:
        target = root / rel
        if not target.is_dir():
            missing_dirs.append(rel)

    for rel in REQUIRED_FILES:
        target = root / rel
        if not target.is_file():
            missing_files.append(rel)

    for rel in REQUIRED_NONEMPTY_FILES:
        target = root / rel
        if not target.is_file():
            continue
        if target.stat().st_size == 0:
            empty_files.append(rel)
            continue
        if target.suffix.lower() == ".pdf":
            try:
                with target.open("rb") as handle:
                    if handle.read(5) != b"%PDF-":
                        invalid_pdfs.append(rel)
            except OSError:
                unreadable.append(rel)

    for rel, needles in REQUIRED_TEXT.items():
        target = root / rel
        if not target.is_file():
            continue
        try:
            text = read_text(target)
        except UnicodeDecodeError:
            unreadable.append(rel)
            continue
        for needle in needles:
            if needle not in text:
                missing_text.append(f"{rel}: {needle}")
        for alternatives in ALTERNATIVE_TEXT.get(rel, []):
            if not any(needle in text for needle in alternatives):
                missing_text.append(f"{rel}: one of {alternatives}")

    if not (missing_dirs or missing_files or missing_text or empty_files or invalid_pdfs or unreadable):
        print(f"[OK] Helper Paper vault is ready: {root}")
        print(f"[OK] Required directories: {len(REQUIRED_DIRS)}")
        print(f"[OK] Required files: {len(REQUIRED_FILES)}")
        print("[OK] Key memory markers found.")
        return 0

    print(f"[FAIL] Helper Paper vault check failed: {root}")
    if missing_dirs:
        print("\nMissing directories:")
        for item in missing_dirs:
            print(f"  - {item}")
    if missing_files:
        print("\nMissing files:")
        for item in missing_files:
            print(f"  - {item}")
    if unreadable:
        print("\nUnreadable UTF-8 files:")
        for item in unreadable:
            print(f"  - {item}")
    if empty_files:
        print("\nEmpty required files:")
        for item in empty_files:
            print(f"  - {item}")
    if invalid_pdfs:
        print("\nInvalid PDF headers:")
        for item in invalid_pdfs:
            print(f"  - {item}")
    if missing_text:
        print("\nMissing expected text markers:")
        for item in missing_text:
            print(f"  - {item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
