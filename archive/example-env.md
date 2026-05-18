# Example Environment Variables Archive

This archive keeps copy-paste environment examples out of the main README.
Do not commit real API keys. Replace every placeholder before using a command.

## DeepSeek Pro

PowerShell session-only example:

```powershell
$env:DEEPSEEK_API_KEY="your DeepSeek key"
$env:DEEPSEEK_API_BASE_URL="https://api.deepseek.com"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
```

DeepSeek is the default quality-first provider for full-paper translation,
review, and guided reading. Use `deepseek-v4-flash` only when speed or cost is
more important than translation quality.

## Xiaomi MiMo Token-Plan

PowerShell session-only example:

```powershell
$env:MIMO_API_KEY="your Xiaomi MiMo key"
$env:MIMO_API_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
$env:MIMO_ANTHROPIC_BASE_URL="https://token-plan-cn.xiaomimimo.com/anthropic"
$env:MIMO_MODEL="mimo-v2.5-pro"
```

If you use an official console key instead of a token-plan subscription key,
replace `MIMO_API_BASE_URL` with the base URL from that provider.

## GPT Academic Through MiMo Token-Plan

PowerShell session-only example:

```powershell
$env:CUSTOM_API_KEY_PATTERN="^tp-[a-zA-Z0-9]+$"
$env:LLM_MODEL="one-api-mimo-v2.5-pro(max_token=8192)"
$env:AVAIL_LLM_MODELS='["one-api-mimo-v2.5-pro(max_token=8192)"]'
$env:API_URL_REDIRECT='{"https://api.openai.com/v1/chat/completions":"https://token-plan-cn.xiaomimimo.com/v1/chat/completions"}'
```

## Provider Check

After setting provider variables, verify the local environment:

```powershell
python C:\Users\<your-user>\.codex\skills\helper-paper\scripts\check_translation_providers.py --provider auto
```

If no API key is available, or the smoke test fails, `helper-paper` should only
finish installation and checks. It must not replace an existing reader or
pretend translation completed.
