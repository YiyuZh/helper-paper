# ChatPaper Usage Notes

Resolve the upstream repository from:

1. `HELPER_PAPER_EXTERNAL_TOOLS_ROOT`
2. `helper-paper/config.local.json`
3. `%USERPROFILE%\helper-paper-external-tools`

The expected repository path is `<external-tools-root>\ChatPaper`.

The local Python environment is a conda-created environment stored in `.venv` and currently targets Python 3.10 for compatibility with pinned packages such as `PyMuPDF==1.22.3` and `gradio==3.20.1`.

For paper translation inside `helper-paper`, run GPT Academic first and then ChatPaper. ChatPaper should provide summary, contribution, method, limitation, and Q&A material. If ChatPaper cannot run, keep the reader marked as partially generated and record the problem in `translation_notes.md`.

Provider default:

- DeepSeek Pro is the current helper-paper production route. Use `DEEPSEEK_API_KEY`, `https://api.deepseek.com`, and `deepseek-v4-pro` for the short smoke test and quality-first review. Use `deepseek-v4-flash` only when speed or cost matters more than quality.
- MiMo token-plan is a fallback provider. Prefer `MIMO_API_KEY`, `https://token-plan-cn.xiaomimimo.com/v1`, and `mimo-v2.5-pro`; treat `response.response_ms` as optional because MiMo-compatible responses may omit it.
- If either provider fails compatibility checks with the old OpenAI SDK, keep ChatPaper disabled for that provider and let helper-paper record the failure.
- Run ChatPaper from a temporary working directory when using custom provider config. If an `apikey.ini` is required, write it as BOM-less UTF-8 and delete it after the run.
