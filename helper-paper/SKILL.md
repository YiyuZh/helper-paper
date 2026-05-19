---
name: helper-paper
description: "Daily academic paper-reading workflow for helper paper, start my day, \u6bcf\u65e5\u8bba\u6587\u9605\u8bfb, candidate paper screening, PDF download, bilingual full-paper readers, GPT Academic and ChatPaper assisted translation, mentor-led reading, understanding correction, venue/date/quality checks, Reviewer Coach teaching, WARN learning memory, and source-grounded reader outputs for the user's Obsidian paper vault."
---

# Helper Paper

## Core Rule

Operate the user's paper-reading vault as the source of truth.

Resolve the vault root in this order:

1. An explicitly provided `--root` value or paper-vault path in the current user request
2. `HELPER_PAPER_VAULT_ROOT`
3. `helper-paper/config.local.json` if the user created one
4. `helper-paper/config.example.json`

At the start of every task, read the vault controller first when it exists:

`paper_daily_orchestration_memory.md`

Then read only the files needed for the task. For a normal daily start, read the start-here note, carry-over todo, system README when needed, the daily/deep-reading templates, and the Reviewer Coach memory files.

## Workflow

1. Identify the user intent: daily start, candidate search, bilingual reader generation, mentor-led reading, understanding check/correction, deep read, PDF download, Reviewer Coach update, WARN archiving, or full-reader preparation.
2. Run `scripts/check_paper_vault.py --root "<paper-vault-root>"` when the vault structure is uncertain. Use `--profile author-demo` only for the original local demonstration vault.
3. For daily starts and carry-over updates, follow `references/orchestration.md`.
4. If the user reports unfinished reading, update carry-over memory and the start-here dashboard.
5. If the user reports a completed paper, update memory only after user reading notes and Codex correction are complete.
6. If the selected paper PDF is missing, download it from the verified official/arXiv/ACL source into `00_inbox/pdfs/`.
7. For English papers the user needs to read, create or use a bilingual reader under `04_full_readers/<paper-short-name>/`.
8. Before any external translation run, read `references/translation-failure-playbook.md` and run provider/tool preflight. Current production provider is DeepSeek Pro; MiMo token-plan is fallback.
9. Keep full-reader source text separate from the user's understanding notes. User understanding and mentor corrections belong in the matching `03_notes/` paper note.
10. For candidate and metadata decisions, follow `references/quality-rules.md`.
11. For Reviewer Coach teaching and WARN memory, follow `references/reviewer-coach.md`.
12. Write Chinese notes by default, while preserving English titles, abstracts, venue names, DOI/arXiv/ACL links, and quoted identifiers.

## Skill Routing

- Use `cs-paper-checklist` for reviewer-style writing advice and submission-readiness teaching when that companion skill is available; otherwise provide a concise built-in reviewer checklist and state that the companion skill is missing.
- Use `nature-academic-search` when metadata, publication status, DOI, Crossref, arXiv, ACL, or reference authenticity matters and the skill is available; otherwise use primary web sources and clearly label any unverified metadata.
- Use `citation-relevance-auditor` when deciding whether a paper actually supports a claim and the skill is available; otherwise do a conservative claim-vs-source check and mark uncertain claims.
- Use `gpt-academic` as the primary external translation engine for English academic PDFs after provider preflight passes.
- Use `chatpaper` after `gpt-academic` for summary, contribution/method/limitation extraction, and reading-question support.
- Use `nature-reader` for source-grounded final reader structure, stable block IDs, figure/table placement, and fallback assembly when the skill is available; otherwise use `scripts/run_translation_pipeline.py` with source-grounded intermediate files.
- Provider strategy is `auto` by default: use DeepSeek Pro when `DEEPSEEK_API_KEY` passes smoke test; use Xiaomi MiMo token-plan only as fallback when DeepSeek is unavailable.
- DeepSeek production model is `deepseek-v4-pro` for quality-first translation, review, and mentor-led reading. Use `deepseek-v4-flash` only when speed or cost matters more than quality. `deepseek-chat` and `deepseek-reasoner` are legacy fallbacks only and are scheduled to stop on 2026-07-24.
- Xiaomi MiMo token-plan fallback base URL is `https://token-plan-cn.xiaomimimo.com/v1`; the Anthropic-compatible backup base is `https://token-plan-cn.xiaomimimo.com/anthropic`. Official console keys may need a different base, so set `MIMO_API_BASE_URL` explicitly when needed. Default fallback model is `mimo-v2.5-pro`.

## Non-Negotiables

- Do not guess venue, date, DOI, peer-review status, or quality level from a title.
- Do not treat arXiv-only papers as high-quality core references unless later acceptance or strong external evidence is verified.
- Do not write user-perception studies as system effectiveness proof.
- Do not generalize technical-interview papers to all hiring or job evaluation scenarios.
- Do not treat LLM scores as human scores or gold labels.
- Do not repeat WARN items already archived in `paper_real_learn_for_warn.md`.
- Do not create full-paper readers unless the user asks for full-text alignment or bilingual reading.
- Do not replace an existing reader if `gpt-academic` or `chatpaper` fails, if no provider is `ready`, or if output cannot be traced to source blocks.
- Do not run whole-paper translation before the translation failure playbook has been applied: provider smoke test, GPT Academic smoke test, ChatPaper smoke test, UTF-8 setup, staging output, reader integrity check, and key leakage scan.
- Do not write DeepSeek, Xiaomi, OpenAI, Anthropic, or other API keys into GitHub files, SKILL.md, README, Obsidian notes, vault memory, or translation outputs.
- Do not present external-tool output as finished unless `translation_notes.md` records tool name, upstream revision, command, API status, output status, and any failure.
- Do not create topic MOC files by default. The Obsidian graph should show paper-to-paper relationships from `paper/03_notes/` only unless the user explicitly asks for topic maps.
- Do not treat an AI-generated guide note or bilingual full reader as user-completed reading.
- Do not mark a paper as complete until the user has written understanding notes and Codex has checked/corrected them.
- Do not increment WARN memory unless the user explicitly says or checks the stable WARN ID.

## Current Defaults

Current vault state is dynamic and must be verified from the vault files.

- Do not assume P1/P4/P5 exist in a public user's vault.
- If a vault was created from the generic initializer, start from the start-here dashboard file and `paper_daily_orchestration_memory.md`.
- If the user is working with the original author demo vault, verify that explicitly with `scripts/check_paper_vault.py --profile author-demo`.
- If the user asks to remake any translation, generate into `_staging` first. Back up and replace the official reader only after `scripts/check_reader_integrity.py` passes.
