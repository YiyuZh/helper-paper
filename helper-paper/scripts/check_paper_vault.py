#!/usr/bin/env python3
"""Validate or initialize a generic Helper Paper Obsidian paper vault."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from helper_paper_config import resolve_vault_root


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

## 今天先做什么

1. 如果 `02_daily/carry_over_todo.md` 有未完成项，先继续那篇论文。
2. 如果你已有 PDF，把它放进 `00_inbox/pdfs/`，然后对 Codex 说：`请把这个 PDF 加入候选并生成阅读任务。`
3. 如果你还没有论文，对 Codex 说：`请围绕我的研究主题搜索 5 篇高质量候选论文。`
4. 如果你只想启动每日流程，对 Codex 说：`$helper-paper start my day`。

## 我需要告诉 Codex 什么

- 研究主题：例如 `我的研究主题是 <topic>，请生成候选论文池。`
- 已有 PDF：例如 `我已放入一个 PDF，请检查并安排阅读。`
- 没读完：例如 `<paper-id> 今天读到方法部分，请记录未完成，明天继续。`
- 已完成：例如 `<paper-id> 我已完成全文阅读和理解检查，请更新记忆并安排下一篇。`
""",
    "paper_daily_orchestration_memory.md": """---
type: system
graph_exclude: true
---

# paper daily orchestration memory

- Generic public vault: no default paper, topic, or WARN state is assumed.
- Daily flow: carry-over todo -> candidate intake -> PDF/reader -> deep note -> understanding check -> Reviewer Coach -> WARN memory.
- Reading completion requires user notes plus Codex correction plus explicit user completion confirmation.
- Bilingual reader source text and user understanding notes must remain separate.
""",
    "01_candidates/candidate_intake.md": """---
type: paper-candidate-intake
graph_exclude: true
---

# candidate intake

## How to start

- Add one or more PDFs to `00_inbox/pdfs/`, or
- Write your research topic below, then ask Codex to search candidates.

## Research topic

未填写。

## Candidate queue

暂无候选论文。
""",
    "02_daily/carry_over_todo.md": """---
type: daily-paper-carry-over
graph_exclude: true
---

# carry over todo

当前未完成：暂无。
""",
    "98_system/README_paper_system.md": "# Paper System\n\nSystem files are operational notes and should stay out of the main paper graph.\n",
    "98_system/README_inbox.md": "# Inbox\n\n`00_inbox/` stores PDFs, links, and temporary paper materials.\n",
    "98_system/README_reviewer_coach.md": "# Reviewer Coach\n\nStores reviewer-coach memory and WARN archive state.\n",
    "99_templates/每日启动模板.md": "# 每日启动模板\n\n- 日期：\n- 今日论文：\n- 未完成事项：\n- 今日产物：\n- 今日未完成，明天继续：\n- 对 Codex 说什么：\n",
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
    "05_reviewer_coach/reviewer_coach_agent_prompt.md": "# reviewer coach agent prompt\n\n每天最多输出 1-3 条写作提醒。只在用户明确确认 WARN ID 后计数。\n",
}

GENERIC_MARKERS = {
    "000_开始这里.md": ["已有 PDF", "研究主题", "$helper-paper start my day", "<paper-id>"],
    "paper_daily_orchestration_memory.md": ["Generic public vault", "candidate intake", "WARN memory"],
    "01_candidates/candidate_intake.md": ["Research topic", "Candidate queue"],
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
            text = target.read_text(encoding="utf-8")
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
    parser.add_argument("--root", help="Paper vault root. Explicit value overrides env/config defaults.")
    parser.add_argument("--profile", choices=("generic", "author-demo"), default="generic")
    parser.add_argument("--init", action="store_true", help="Create the generic vault structure and starter files.")
    parser.add_argument("--force", action="store_true", help="When used with --init, overwrite starter files.")
    args = parser.parse_args()

    root = resolve_vault_root(args.root)

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
