---
name: chatpaper
description: Wrapper for a local kaixindelele/ChatPaper repository. Use when Codex needs ChatPaper as an external academic PDF summarization, translation review, or question-answering companion, especially as the secondary summary and verification backend for helper-paper readers.
---

# ChatPaper Wrapper

## Local Tool

- Resolve the external tools root from `HELPER_PAPER_EXTERNAL_TOOLS_ROOT`; if unset, use the user's `helper-paper/config.local.json`; if still unset, use `%USERPROFILE%\helper-paper-external-tools`.
- Repository: `<external-tools-root>\ChatPaper`
- Python environment: `<external-tools-root>\ChatPaper\.venv`
- Preferred Python executable: `<external-tools-root>\ChatPaper\.venv\python.exe`
- Upstream: `https://github.com/kaixindelele/ChatPaper`

This is a wrapper skill. Do not copy the upstream project into this skill folder.

## When To Use

Use this skill when a task needs ChatPaper for:

- summarizing a paper after primary translation;
- extracting contribution, method, limitation, and Q&A style reading aids;
- second-pass checking of a bilingual reader generated with GPT Academic;
- supporting `$helper-paper` mentor-led paper reading.

## Operating Rules

1. Check that the repository and Python executable exist before running anything.
2. Check API configuration before attempting summary or translation generation. For non-OpenAI providers, require an OpenAI-compatible base URL smoke test first.
3. Never write API keys into this skill, the upstream repository, GitHub docs, or the user's paper vault.
4. Treat ChatPaper as a secondary summary/review source, not the sole source of the full bilingual reader.
5. DeepSeek Pro is the current helper-paper production route when configured. Run a short OpenAI-compatible smoke test before any full PDF work.
6. MiMo token-plan remains a fallback route, but run a short OpenAI-compatible smoke test before any full PDF work.
7. Xiaomi MiMo works with ChatPaper's old OpenAI SDK after a smoke test. Some MiMo responses do not include `response_ms`, so local ChatPaper must treat that field as optional instead of retrying a successful response.
8. If ChatPaper needs `apikey.ini`, create it in a temporary working directory with BOM-less UTF-8. Do not run from the upstream repo root when using custom provider config.
9. If no API key is configured, stop before generation and report that installation is ready but generation is blocked.
10. If a run fails, record the command, error summary, and missing dependency/API condition in the target paper's `translation_notes.md`; do not silently mark the reader as updated.

## Useful Commands

```powershell
$ExternalToolsRoot = if ($env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT) { $env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT } else { Join-Path $env:USERPROFILE "helper-paper-external-tools" }
$ChatPaper = Join-Path $ExternalToolsRoot "ChatPaper"
cd $ChatPaper
.\.venv\python.exe --version
.\.venv\python.exe -m pip check
.\.venv\python.exe -c "import gradio, fitz, openai, requests; print('ChatPaper imports ok')"
```

DeepSeek smoke-test inputs for ChatPaper-style OpenAI compatibility:

```powershell
$env:DEEPSEEK_API_KEY="your key"
$env:CHATPAPER_API_BASE="https://api.deepseek.com"
$env:CHATPAPER_MODEL="deepseek-v4-pro"
```

MiMo smoke-test inputs:

```powershell
$env:MIMO_API_KEY="your key"
$env:MIMO_API_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
$env:MIMO_MODEL="mimo-v2.5-pro"
```

For MiMo, run `helper-paper\scripts\patch_chatpaper_mimo.py --check` before production use. If it reports `needs_patch`, run `helper-paper\scripts\patch_chatpaper_mimo.py --apply` once; the script creates `.helper-paper.bak` files by default. Temp `apikey.ini` files must be written without a UTF-8 BOM; PowerShell `Set-Content -Encoding UTF8` is unsafe for this case.

Update the external tool with:

```powershell
$ExternalToolsRoot = if ($env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT) { $env:HELPER_PAPER_EXTERNAL_TOOLS_ROOT } else { Join-Path $env:USERPROFILE "helper-paper-external-tools" }
$ChatPaper = Join-Path $ExternalToolsRoot "ChatPaper"
cd $ChatPaper
git pull
.\.venv\python.exe -m pip install --prefer-binary -r requirements.txt
.\.venv\python.exe -m pip install "setuptools<81"
```

## Output Contract For helper-paper

When used from `helper-paper`, ChatPaper output should be merged as a clearly labeled companion layer:

- paper summary;
- method/contribution/limitation notes;
- key Q&A for the mentor-led reading session;
- disagreement or uncertainty notes compared with the GPT Academic translation.
