---
name: gpt-academic
description: Wrapper for a local binary-husky/gpt_academic repository. Use when Codex needs GPT Academic as an external paper translation or PDF/Arxiv reading engine, especially as the primary translation backend for helper-paper bilingual full-paper readers.
---

# GPT Academic Wrapper

## Local Tool

- Resolve the external tools root from `HELPER_PAPER_EXTERNAL_TOOLS_ROOT`; if unset, use the user's `helper-paper/config.local.json`; if still unset, use `%USERPROFILE%\helper-paper-external-tools`.
- Repository: `<external-tools-root>\gpt_academic`
- Python environment: `<external-tools-root>\gpt_academic\.venv`
- Preferred Python executable: `<external-tools-root>\gpt_academic\.venv\python.exe`
- Upstream: `https://github.com/binary-husky/gpt_academic`

This is a wrapper skill. Do not copy the upstream project into this skill folder.

For detailed setup, provider notes, and failure handling, read `references/usage.md` when preparing or debugging an actual GPT Academic run.

## When To Use

Use this skill when a task needs `gpt_academic` for:

- translating an English academic PDF into Chinese reading material;
- creating a primary bilingual draft for a paper reader;
- checking or running the local `gpt_academic` installation;
- supporting `$helper-paper` full-paper translation.

## Operating Rules

1. Check that the repository and Python executable exist before running anything.
2. Check API configuration before attempting translation. Prefer environment variables such as `MIMO_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, or the upstream project's supported config mechanism.
3. Never write API keys into this skill, the upstream repository, GitHub docs, or the user's paper vault.
4. If no API key is configured, stop before translation and report that installation is ready but generation is blocked.
5. Treat `gpt_academic` as the primary translation source, but keep `helper-paper` responsible for source maps, Obsidian paths, mentor prompts, and final Markdown assembly.
6. DeepSeek Pro is the current helper-paper production route when configured: use `deepseek-v4-pro` for quality-first translation and review.
7. MiMo token-plan remains a fallback provider: use `mimo-v2.5-pro`, token-plan `/v1/chat/completions`, and the `one-api-*` route only when DeepSeek is unavailable or explicitly requested.
8. Token-plan keys require `CUSTOM_API_KEY_PATTERN=^tp-[a-zA-Z0-9]+$` so gpt_academic accepts the key format. Without this, valid `tp-...` keys are rejected locally before the API call.
9. If a run fails, record the command, error summary, and missing dependency/API condition in the target paper's `translation_notes.md`; do not silently fall back to a vague summary.

## Useful Commands

```powershell
$ExternalToolsRoot = if ($env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT) { $env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT } else { Join-Path $env:USERPROFILE "helper-paper-external-tools" }
$GptAcademic = Join-Path $ExternalToolsRoot "gpt_academic"
cd $GptAcademic
.\.venv\python.exe --version
.\.venv\python.exe -m pip check
.\.venv\python.exe -c "import gradio, fitz, openai, requests, spacy; print('gpt_academic imports ok')"
```

DeepSeek environment example:

```powershell
$env:DEEPSEEK_API_KEY="your key"
$env:DEEPSEEK_API_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-pro"
$env:AVAIL_LLM_MODELS='["deepseek-v4-pro","deepseek-v4-flash"]'
```

MiMo token-plan environment example:

```powershell
$env:MIMO_API_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
$env:MIMO_MODEL="mimo-v2.5-pro"
$env:CUSTOM_API_KEY_PATTERN="^tp-[a-zA-Z0-9]+$"
$env:LLM_MODEL="one-api-mimo-v2.5-pro(max_token=8192)"
$env:AVAIL_LLM_MODELS='["one-api-mimo-v2.5-pro(max_token=8192)"]'
$env:API_URL_REDIRECT='{"https://api.openai.com/v1/chat/completions":"https://token-plan-cn.xiaomimimo.com/v1/chat/completions"}'
```

Do not use legacy model names such as `gpt-3.5-turbo-16k` with MiMo; the gateway rejects them. For smoke tests, require non-empty final content because reasoning-capable models can return HTTP 200 with empty content when token limits are too small.

Update the external tool with:

```powershell
$ExternalToolsRoot = if ($env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT) { $env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT } else { Join-Path $env:USERPROFILE "helper-paper-external-tools" }
$GptAcademic = Join-Path $ExternalToolsRoot "gpt_academic"
cd $GptAcademic
git pull
.\.venv\python.exe -m pip install --prefer-binary -r requirements.txt
.\.venv\python.exe -m pip install "setuptools<81"
```

## Output Contract For helper-paper

When used from `helper-paper`, output should be converted into the vault reader layout:

- `paper.md`: original block, Chinese translation, and reading prompts;
- `source_map.json`: stable block IDs with page/section anchors;
- `translation_notes.md`: upstream revision, command, API status, dependency status, errors, and manual review notes;
- `assets/`: only figures/tables that were actually extracted for the reader.
