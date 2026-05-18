#!/usr/bin/env python3
"""Validate or initialize a Helper Paper Obsidian paper vault.

Default mode is generic and portable: it checks the directory structure and
system files needed by helper-paper without requiring the author's P1/P4 data.
Use ``--profile author-demo`` only for the original local demonstration vault.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


DEFAULT_ROOT = os.environ.get("HELPER_PAPER_VAULT_ROOT", "paper")

REQUIRED_DIRS = [
    "00_inbox",
    "00_inbox/pdfs",
    "01_candidates",
    "02_daily",
    "03_notes",
    "04_full_readers",
    "05_reviewer_coach",
    "98_system",
    "99_templates",
]

GENERIC_FILES: dict[str, str] = {
    "000_开始这里.md": """---
type: system
graph_exclude: true
---

# 开始这里

## 今天先看

- 对 Codex 说：`$helper-paper start my day`
- 如果有未完成事项，先继续未完成论文。
- 如果没有未完成事项，从候选清单选择今日论文。

## 读完对 Codex 说什么

- `我写完这一段理解了，请检查我的理解。`
- `今天没读完，请记录未完成，明天继续。`
- `我已完成全文阅读和理解检查，请更新记忆并安排下一篇。`
""",
    "paper_daily_orchestration_memory.md": """---
type: system
graph_exclude: true
---

# paper daily orchestration memory

- 默认流程：候选筛选 -> PDF/reader -> 精读笔记 -> 理解检查 -> Reviewer Coach -> WARN 记忆。
- 完成阅读必须包含：用户理解笔记 + Codex 检查/斧正 + 用户明确完成确认。
- 英文论文 reader 与个人理解笔记分开保存。
""",
    "02_daily/carry_over_todo.md": """---
type: daily-paper-carry-over
graph_exclude: true
---

# carry over todo

当前未完成：暂无。
""",
    "98_system/README_paper_system.md": "# Paper System\n\n系统说明文件，不进入论文关系图谱。\n",
    "98_system/README_inbox.md": "# Inbox\n\n`00_inbox/` 保存 PDF、链接和临时材料。\n",
    "98_system/README_reviewer_coach.md": "# Reviewer Coach\n\n保存审稿人教练记忆和 WARN 归档。\n",
    "99_templates/每日启动模板.md": "# 每日启动模板\n\n- 日期：\n- 今日论文：\n- 未完成事项：\n- 今日产物：\n",
    "99_templates/精读一篇模板.md": """# 精读一篇模板

## 含金量卡

## 研究问题

## 方法与实验

## 关键发现

## 我的阅读理解与导师斧正

## 审稿人教练

## 相关论文
""",
    "05_reviewer_coach/reviewer_learning_memory.md": "# reviewer learning memory\n\n暂无 active WARN。\n",
    "05_reviewer_coach/paper_real_learn_for_warn.md": "# paper real learn for warn\n\n暂无已归档 WARN。\n",
    "05_reviewer_coach/reviewer_coach_agent_prompt.md": "# reviewer coach agent prompt\n\n每天最多输出 1-3 条写作提醒。\n",
}

GENERIC_MARKERS = {
    "000_开始这里.md": ["开始这里", "$helper-paper start my day", "未完成"],
    "paper_daily_orchestration_memory.md": ["候选筛选", "理解检查", "WARN"],
    "99_templates/精读一篇模板.md": ["含金量卡", "我的阅读理解与导师斧正", "审稿人教练", "相关论文"],
}

AUTHOR_DEMO_FILES = [
    r"00_inbox\pdfs\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud.pdf",
    r"00_inbox\pdfs\P4_2024_NAACL_Groundedness_in_RAG_Long-form_Generation.pdf",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\paper.md",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\source_map.json",
    r"04_full_readers\P1_2025_VLHCC_Conversational_AI_Technical_Interview_Think_Aloud\translation_notes.md",
]

AUTHOR_DEMO_MARKERS = {
    "paper_daily_orchestration_memory.md": ["P1", "P4", "WARN-001"],
    r"03_notes\2026-05-16_P1_Conversational-AI-Technical-Interview-Think-Aloud.md": [
        "我的阅读理解与导师斧正",
        "导师检查状态",
    ],
}


def write_if_missing(path: Path, text: str, *, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def init_vault(root: Path, *, force: bool) -> list[str]:
    created: list[str] = []
    for rel in REQUIRED_DIRS:
        target = root / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(rel)
    for rel, text in GENERIC_FILES.items():
        target = root / rel
        if write_if_missing(target, text, force=force):
            created.append(rel)
    return created


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_files(root: Path, *, profile: str) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    missing_dirs: list[str] = []
    missing_files: list[str] = []
    missing_text: list[str] = []
    empty_files: list[str] = []
    unreadable: list[str] = []

    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            missing_dirs.append(rel)

    required_files = list(GENERIC_FILES)
    markers = dict(GENERIC_MARKERS)

    if profile == "author-demo":
        required_files.extend(AUTHOR_DEMO_FILES)
        markers.update(AUTHOR_DEMO_MARKERS)

    for rel in required_files:
        target = root / rel
        if not target.is_file():
            missing_files.append(rel)
            continue
        if target.stat().st_size == 0:
            empty_files.append(rel)
        if target.suffix.lower() == ".pdf":
            try:
                with target.open("rb") as handle:
                    if handle.read(5) != b"%PDF-":
                        unreadable.append(f"{rel}: invalid PDF header")
            except OSError as exc:
                unreadable.append(f"{rel}: {exc}")

    for rel, needles in markers.items():
        target = root / rel
        if not target.is_file():
            continue
        try:
            text = read_text(target)
        except UnicodeDecodeError as exc:
            unreadable.append(f"{rel}: not UTF-8: {exc}")
            continue
        for needle in needles:
            if needle not in text:
                missing_text.append(f"{rel}: {needle}")

    return missing_dirs, missing_files, missing_text, empty_files, unreadable


def print_list(title: str, items: list[str]) -> None:
    if not items:
        return
    print(f"\n{title}:")
    for item in items:
        print(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or initialize a Helper Paper vault.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Paper vault root path. Defaults to HELPER_PAPER_VAULT_ROOT or ./paper.")
    parser.add_argument("--profile", choices=("generic", "author-demo"), default="generic")
    parser.add_argument("--init", action="store_true", help="Create the generic vault structure and starter files.")
    parser.add_argument("--force", action="store_true", help="When used with --init, overwrite starter files.")
    args = parser.parse_args()

    root = Path(args.root)

    if args.init:
        created = init_vault(root, force=args.force)
        print(f"[OK] Initialized Helper Paper vault: {root}")
        print(f"[OK] Created/updated items: {len(created)}")
        for item in created:
            print(f"  - {item}")

    if not root.exists():
        print(f"[FAIL] Vault root does not exist: {root}")
        print("Hint: run with --init to create a generic Helper Paper vault.")
        return 1
    if not root.is_dir():
        print(f"[FAIL] Vault root is not a directory: {root}")
        return 1

    missing_dirs, missing_files, missing_text, empty_files, unreadable = check_files(root, profile=args.profile)

    if not (missing_dirs or missing_files or missing_text or empty_files or unreadable):
        print(f"[OK] Helper Paper vault is ready: {root}")
        print(f"[OK] Profile: {args.profile}")
        return 0

    print(f"[FAIL] Helper Paper vault check failed: {root}")
    print(f"[INFO] Profile: {args.profile}")
    print_list("Missing directories", missing_dirs)
    print_list("Missing files", missing_files)
    print_list("Unreadable or invalid files", unreadable)
    print_list("Empty files", empty_files)
    print_list("Missing expected text markers", missing_text)
    if args.profile == "generic":
        print("\nHint: run with --init to create the generic structure.")
    else:
        print("\nHint: author-demo checks are only for the original P1/P4 demonstration vault.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
