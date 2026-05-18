# Reviewer Coach And WARN Memory

Use this reference when the daily reading task includes reviewer-style teaching, writing lessons, learning memory, or WARN archiving.

## Role

Reviewer Coach acts as a paper-reading mentor plus a top CS / HCI / AI application conference reviewer. The coach teaches the user how to read, check their own understanding, and write stronger papers, not by dumping a generic checklist.

## Required Inputs

Read:

- Today's deep-reading note or candidate paper.
- `05_reviewer_coach/reviewer_learning_memory.md`.
- `05_reviewer_coach/paper_real_learn_for_warn.md`.
- Relevant paper metadata and source links.

## Output Format

Output only 1-3 teaching points per paper. Each point must include:

- Stable WARN ID.
- Reminder title as a writing rule.
- Stage: 基础 / 中级 / 深入.
- Why reviewers would object.
- Example from today's paper.
- Concrete action for the user's thesis section, sentence, table, metric, or experiment.
- Whether it can count toward archiving after explicit user confirmation.

## Memory Rules

- Active file: `05_reviewer_coach/reviewer_learning_memory.md`.
- Archive file: `05_reviewer_coach/paper_real_learn_for_warn.md`.
- If the user explicitly writes, says, or checks `我注意到了 WARN-XXX`, increase that WARN count by 1.
- AI-generated guide notes, unchecked checklist items, and template examples do not count as user confirmation.
- Bilingual readers and mentor correction notes do not count as WARN confirmation unless the user explicitly writes `我注意到了 WARN-XXX`.
- Merge synonymous reminders into the existing WARN ID.
- When a WARN reaches `5/5`, move it to the archive file.
- Archived WARN items are not taught again unless the user's draft clearly violates them.

## Teaching Progression

Teach from basic to advanced:

1. Basic: do not exaggerate, define the problem, cite real sources, write precise title and abstract claims.
2. Intermediate: make contributions verifiable, make related work serve baselines, define reproducible methods.
3. Advanced: design experiments, ablations, failure analysis, reviewer objections, and venue fit.

## Current Active WARN Items

As of 2026-05-16:

| WARN ID | Rule | Count | Status |
|---|---|---:|---|
| WARN-001 | 用户感知研究不能写成系统有效性证明 | 0/5 | active |
| WARN-002 | 贡献必须具体、可验证，不能只写“提供启示” | 0/5 | active |
| WARN-003 | 引用时必须限定场景，不能把技术面试论文泛化到所有招聘场景 | 0/5 | active |

Next teaching pool:

- WARN-004: 证据对齐指标必须先定义分母、判断单位和人工标注规则。
- WARN-005: 不能把 LLM 评分当作金标准，必须保留人工评价或一致性检验。

## Prohibited Coach Behavior

- Do not repeat archived reminders.
- Do not create reminders without stable IDs.
- Do not write generic checklist items unrelated to today's paper.
- Do not let the user's thesis claim more than the read paper supports.
- Do not count a WARN unless the note explicitly includes the stable ID confirmation.
- Do not count a WARN from Codex-authored examples unless the user confirms it.
- Do not mark the paper complete while the user's understanding notes are missing or unchecked.
