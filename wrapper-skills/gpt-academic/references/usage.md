# GPT Academic Usage Notes

Resolve the upstream repository from:

1. `HELPER_PAPER_EXTERNAL_TOOLS_ROOT`
2. `helper-paper/config.local.json`
3. `%USERPROFILE%\helper-paper-external-tools`

The expected repository path is `<external-tools-root>\gpt_academic`.

The local Python environment is a conda-created environment stored in `.venv` and currently targets Python 3.10 for compatibility with pinned packages such as `spacy==3.7.4`.

For paper translation inside `helper-paper`, run GPT Academic first, then use ChatPaper as a second-pass summary/review source. If GPT Academic cannot run, keep the existing reader unchanged and write the failure into `translation_notes.md`.

Provider default:

- DeepSeek Pro is the current helper-paper production route. Use `DEEPSEEK_API_KEY`, `https://api.deepseek.com`, and `deepseek-v4-pro` for quality-first translation and review. Use `deepseek-v4-flash` only when speed or cost matters more than quality.
- MiMo token-plan is a fallback route. Use `MIMO_API_KEY`, `https://token-plan-cn.xiaomimimo.com/v1`, `mimo-v2.5-pro`, `CUSTOM_API_KEY_PATTERN=^tp-[a-zA-Z0-9]+$`, `LLM_MODEL=one-api-mimo-v2.5-pro(max_token=8192)`, and `API_URL_REDIRECT` to the token-plan `/v1/chat/completions` endpoint.
- `deepseek-chat` and `deepseek-reasoner` are legacy fallbacks only and are scheduled for retirement on 2026-07-24.
- Do not allow GPT Academic to fall back to `gpt-3.5-turbo-16k` when using MiMo; it is rejected by the gateway. Treat HTTP 200 with empty content as a failed smoke test.
