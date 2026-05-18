# Daily Orchestration

Use this reference for "每日论文阅读", "start my day", "helper paper", bilingual reader generation, mentor-led reading, understanding checks, or any request to continue the daily paper-reading workflow.

## Daily Start

1. Read `paper_daily_orchestration_memory.md`.
2. Read `000_开始这里.md`.
3. Read `02_daily/carry_over_todo.md`.
4. Read `98_system/README_paper_system.md` only when system rules or directory purpose are needed.
5. Read `99_templates/每日启动模板.md`.
6. Read `99_templates/精读一篇模板.md`.
7. Read `05_reviewer_coach/reviewer_learning_memory.md`.
8. Read `05_reviewer_coach/paper_real_learn_for_warn.md`.
9. If carry-over has an unfinished paper, continue that paper before choosing a new one.
10. Create or update `02_daily/YYYY-MM-DD_start-my-day.md`.
11. Choose the paper for today. If the user does not specify one and no carry-over exists, prefer the next recommendation in the vault controller.
12. Verify metadata before writing quality claims.
13. If the selected paper PDF is missing, download it from the verified official/arXiv/ACL source into `00_inbox/pdfs/`.
14. For English selected papers, create or open the bilingual reader under `04_full_readers/论文短名/` before asking the user to read. Default generation route: `gpt-academic` primary translation, `chatpaper` summary/review, and `nature-reader`-style final assembly with source anchors.
15. Create or update a guide/deep-reading note in `03_notes/`; this is where the user's understanding notes and mentor corrections belong.
16. For mentor-led reading, guide the user through four blocks: title/abstract/introduction, method/experiment, results/limits, citable points/writing warnings.
17. After each block, ask the user to write their understanding in the paper note, then check/correct it before marking the block done.
18. Add Reviewer Coach teaching. Update WARN memory only after explicit user confirmation.
19. End with an acceptance check.

## Carry-Over Updates

When the user says a paper is unfinished, such as `P1 今天只读到方法部分，请记录未完成，明天 start my day 继续。`:

- Update `02_daily/carry_over_todo.md` with the paper, stopping point, next start action, date, and status.
- Update `000_开始这里.md` under `未完成事项` so the next opening clearly shows where to resume.
- Do not select a new paper on the next daily start until the carry-over item is resolved.

When the user says a paper is finished, use the stricter completion phrase, such as `P1 我已完成全文阅读和理解检查，请更新记忆并安排下一篇。`:

- Update the daily note, deep-reading note, Reviewer Coach memory, and paper relationships as needed.
- Clear the paper from `carry_over_todo.md`.
- Update `000_开始这里.md` with the next recommended paper.

Do not mark a paper complete just because Codex generated a guide note or bilingual reader. Completion requires: user reading, user understanding notes, Codex correction/斧正, and an explicit user statement.

## Required Daily Outputs

- A daily note in `02_daily/`, unless the user only asks for a status report.
- A candidate update in `01_candidates/` when new papers are searched or metadata changes.
- A deep-reading note in `03_notes/` when a paper is read.
- A bilingual reader in `04_full_readers/` when an English paper needs reading support.
- Reviewer Coach memory updates in `05_reviewer_coach/` when WARN confirmations or new WARN items appear.
- Carry-over updates in `02_daily/carry_over_todo.md` when the user reports unfinished reading.
- Do not create topic MOC files during normal daily reading. Paper relationships should be written in the deep-reading note's `相关论文` section.

## Deep Reading Note Requirements

Every deep-reading note must include:

- Quality card: venue/status, venue name, publication date, whether within 3 years, peer-review status, topic fit, quality judgment, priority reason, metadata sources.
- Related papers: only link to other notes in `03_notes/`; leave it as "暂无" until the related paper has been read.
- Basic paper information.
- Research question and claimed contribution.
- Method, design, data, experiment, user study, metrics, baseline, and ethics/IRB when relevant.
- Key findings.
- At least 3 citable points with cautious wording.
- Claims that cannot be exaggerated.
- Relationship to the user's thesis chapters.
- User understanding notes and mentor correction records.
- Reviewer Coach section with stable WARN IDs.
- Next-step decision: formal literature pool, related work, citation chain, full reader, or do not use.

## Mentor-Led Reading

Default role: 论文阅读导师 + 中英对照阅读助手 + 审稿人教练.

For P1 and later papers, guide the user in small blocks:

1. Title, abstract, introduction: what problem is being defined, what gap is claimed, what scope is limited.
2. Method and experiment: what was built, who participated, what data or ratings were collected, what is reproducible.
3. Results and limits: what the evidence supports, what it does not support.
4. Citable points and writing warnings: where this paper can be cited in the user's thesis and what cannot be exaggerated.

The user's default prompt is:

`导师带我读 P1，从摘要和引言开始。`

If the user reports a stopping point, record it in carry-over and resume there on the next daily start.

For English papers, the reading order is:

1. Open the bilingual reader in `04_full_readers/`.
2. Read one block.
3. Write personal understanding in the matching `03_notes/` paper note.
4. Ask Codex to check/correct the understanding.
5. Only after correction can that block be considered complete.

## Current Reading State

As of 2026-05-16:

- P1 has an AI guide note and a bilingual reader, but the user has not completed personal reading or understanding checks.
- P1 is the current default reading object. Start from the bilingual reader with the title, abstract, and introduction.
- P4 is the default next paper after P1 because it is ACL Findings / NAACL 2024 and supports groundedness, hallucination, and evidence alignment.
- P5 is the next strong option for LLM evaluator reliability and human scoring.
- P2 and P3 are useful but should be treated cautiously as arXiv-only or technical-report materials until formal venue status is verified.

## End-of-Day Acceptance Check

Confirm:

- Today's note exists or the reason for not creating it is explicit.
- Source links are real.
- Publication date, venue/status, quality level, and timeliness are sourced.
- Citable points are separated from non-exaggeration warnings.
- Reviewer Coach produced 1-3 teaching points.
- WARN counts were updated only when the user explicitly wrote or checked `我注意到了 WARN-XXX`.
- Any WARN reaching `5/5` was moved to `paper_real_learn_for_warn.md`.
- Any unfinished reading was written to `carry_over_todo.md` and reflected in `000_开始这里.md`.
- Full-reader output exists for English papers being actively read, and is kept separate from user understanding notes.

## External Translation Route

Use this route whenever the user asks to remake an English paper reader or says the existing bilingual translation is hard to understand.

1. Verify the PDF exists in `00_inbox/pdfs/`.
2. Verify `gpt-academic` exists at `C:\Users\lenovo\.codex\skills\gpt-academic\SKILL.md` and the upstream tool exists at `E:\skills\external-tools\gpt_academic`.
3. Verify `chatpaper` exists at `C:\Users\lenovo\.codex\skills\chatpaper\SKILL.md` and the upstream tool exists at `E:\skills\external-tools\ChatPaper`.
4. Read `references/translation-failure-playbook.md` before running any translation command.
5. Check provider readiness with `scripts/check_translation_providers.py --provider auto`. For MiMo dual-endpoint checks, add `--provider mimo --check-anthropic`.
6. If no provider key is configured or every configured provider fails smoke test, stop before translation. Report that tools are installed but generation is blocked. Do not back up or replace the existing reader.
7. Run short GPT Academic and ChatPaper smoke tests against the selected provider. For MiMo token-plan, require `mimo-v2.5-pro`, `CUSTOM_API_KEY_PATTERN=^tp-[a-zA-Z0-9]+$`, and the token-plan redirect to `/v1/chat/completions`.
8. Generate into `04_full_readers/_staging/论文短名_YYYYMMDD-HHmmss/`, never directly into the official reader directory.
9. Run `gpt-academic` first for the primary translation.
10. Run `chatpaper` second for summary, contribution, method, limitation, and Q&A review, using a temporary working directory and BOM-less UTF-8 config when needed.
11. Merge outputs in staging with clear labels: `Original`, `中文翻译`, `ChatPaper 摘要/复核`, and `导师阅读提示`.
12. Preserve or regenerate `source_map.json` with stable block IDs and page/section anchors.
13. Write `translation_notes.md` with upstream revisions, commands, Python versions, API status, success/failure status, and manual review notes.
14. Validate staging with `scripts/check_reader_integrity.py --reader "staging目录"`.
15. Scan staging, the skill package, and vault output for API key leakage.
16. Only after validation passes, back up the existing reader directory or `paper.md` under `04_full_readers/_backup/论文短名_YYYYMMDD-HHmmss/`, then replace the official reader path.
17. If either external tool fails, keep the old reader unchanged or mark staging partial only. Do not claim that a complete new reader was generated.

## Translation Provider Policy

Default provider strategy: `auto`.

- `auto`: use DeepSeek Pro when configured and smoke-tested; use Xiaomi MiMo token-plan only as fallback when DeepSeek is unavailable.
- `deepseek`: use `DEEPSEEK_API_KEY`; default base URL `https://api.deepseek.com`; default production model `deepseek-v4-pro` for quality-first translation and review. Use `deepseek-v4-flash` only for speed/cost-sensitive tasks. Keep `deepseek-chat` and `deepseek-reasoner` only as legacy fallbacks until their 2026-07-24 retirement.
- `mimo`: prefer `MIMO_API_KEY`; fallback `XIAOMI_API_KEY` is accepted for older local configs. For token-plan/subscription keys, default base URL is `https://token-plan-cn.xiaomimimo.com/v1`; Anthropic-compatible backup is `https://token-plan-cn.xiaomimimo.com/anthropic`. Official console keys may need a different base, so set `MIMO_API_BASE_URL` explicitly. Default model is `mimo-v2.5-pro`. Run an OpenAI-compatible smoke test before full-paper translation.
- Never write provider keys into GitHub docs, SKILL.md files, Obsidian vault files, or translation outputs.
- Whole-paper translation can start only after a short smoke test succeeds. If smoke test fails, leave the old reader untouched and record the failure.
