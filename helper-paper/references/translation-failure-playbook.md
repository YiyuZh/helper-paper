# Translation Failure Playbook

Use this reference before any helper-paper task that remakes a bilingual full-paper reader with GPT Academic, ChatPaper, MiMo, DeepSeek, OpenAI-compatible gateways, or temporary translation scripts.

The goal is to prevent failures observed during prior bilingual-reader rebuilds. Treat these rules as guardrails, not optional notes.

## Mandatory Preflight

Before whole-paper translation:

1. Run `scripts/check_translation_providers.py --provider auto`.
2. If using MiMo, run `scripts/check_translation_providers.py --provider mimo --check-anthropic` when the Anthropic-compatible endpoint is relevant.
3. Confirm GPT Academic and ChatPaper each have a short tool-specific smoke test.
4. Set PowerShell UTF-8 before any script containing Chinese literals:

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
```

5. Generate into `04_full_readers/_staging/<paper>_<timestamp>/`.
6. Validate the staging reader with `scripts/check_reader_integrity.py --reader "<staging-reader-dir>"`.
7. Scan the staging output for configured secret values or long secret fragments.
8. Only after validation passes, back up the old reader and replace the official reader path.

If any step fails, keep the existing reader unchanged and record the failure in `translation_notes.md`.

## Known Failure Points And Fixed Rules

| Failure | Symptom | Cause | Fixed rule |
| --- | --- | --- | --- |
| Wrong MiMo base URL | 401 `Invalid API Key` | Subscription/token-plan key was sent to the official default API host | Token-plan keys must use `https://token-plan-cn.xiaomimimo.com/v1`; official console keys may use a different official base. |
| Legacy model fallback | 400 `Not supported model` | GPT Academic or ChatPaper defaulted to `gpt-3.5-turbo-16k` | Override model to `mimo-v2.5-pro`; never let old OpenAI model names reach MiMo. |
| GPT Academic rejects `tp-...` key | Key validation fails before request | GPT Academic default key regex does not accept token-plan keys | Set `CUSTOM_API_KEY_PATTERN=^tp-[a-zA-Z0-9]+$`. |
| Empty MiMo smoke-test content | HTTP 200 but no useful answer | Too few completion tokens; reasoning consumed the budget | Use short "Return only ok" prompts and at least `max_completion_tokens=512`. Treat empty content as failure. |
| Empty DeepSeek V4 smoke-test content | HTTP 200 but final content is empty | `deepseek-v4-pro` / `deepseek-v4-flash` can spend most completion tokens on reasoning | Use `max_tokens=512` for DeepSeek smoke tests. Treat empty content as failure. |
| ChatPaper reads wrong config | Requests go to OpenAI official API or wrong base | Running from ChatPaper repo root picked up upstream `apikey.ini` | Run ChatPaper from a temporary working directory with temporary config only. |
| ChatPaper BOM config failure | `MissingSectionHeaderError` with `\ufeff[OpenAI]` | PowerShell `Set-Content -Encoding UTF8` wrote BOM | Write temp `apikey.ini` with BOM-less UTF-8. |
| ChatPaper `response_ms` crash | Successful MiMo response retried and final output empty | MiMo-compatible response had `response_ms=None` | Run `patch_chatpaper_mimo.py --check`; if needed, use explicit `--apply` so a backup is created. |
| PowerShell Chinese corruption | Static Chinese labels become `?` | Inline script was sent through non-UTF-8 console encoding | Set UTF-8 first, or keep temporary scripts ASCII-only and use external UTF-8 files. |
| Invalid model JSON | `zh` field becomes an object or model returns prose instead of JSON | Model did not follow strict schema | Normalize non-string JSON values; fall back to plain translation; cache after each block. |
| References over-translated | Reference list becomes noisy and less useful | Bibliography was translated line by line | Preserve English references and add one Chinese note; do not translate every citation. |
| Reader overwritten after partial failure | User loses previous usable reader | Generation wrote directly into official reader path | Always stage, validate, then backup and replace. |
| Compatibility marker mismatch | Vault checker fails despite usable reader | Reader used `中文翻译` while checker expected legacy `中文` | Checkers must accept both legacy and current markers. |
| Secret leakage risk | API key fragments appear in logs or temp configs | Tool logs or temp files persisted | Never write keys into repo/vault; delete temp dirs; run leakage scan before completion. |

## DeepSeek Pro Runtime Contract

Use this contract for the default production route:

```powershell
$env:DEEPSEEK_API_BASE_URL = "https://api.deepseek.com"
$env:DEEPSEEK_MODEL = "deepseek-v4-pro"
$env:LLM_MODEL = "deepseek-v4-pro"
$env:AVAIL_LLM_MODELS = '["deepseek-v4-pro","deepseek-v4-flash"]'
```

Do not write the API key into these files. Set `DEEPSEEK_API_KEY` only in the runtime environment or Windows user environment. Use `deepseek-v4-flash` only when speed or cost matters more than translation quality.

## MiMo Token-Plan Runtime Contract

Use this contract for subscription/token-plan keys:

```powershell
$env:MIMO_API_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
$env:MIMO_ANTHROPIC_BASE_URL = "https://token-plan-cn.xiaomimimo.com/anthropic"
$env:MIMO_MODEL = "mimo-v2.5-pro"
$env:CUSTOM_API_KEY_PATTERN = "^tp-[a-zA-Z0-9]+$"
$env:LLM_MODEL = "one-api-mimo-v2.5-pro(max_token=8192)"
$env:AVAIL_LLM_MODELS = '["one-api-mimo-v2.5-pro(max_token=8192)"]'
$env:API_URL_REDIRECT = '{"https://api.openai.com/v1/chat/completions":"https://token-plan-cn.xiaomimimo.com/v1/chat/completions"}'
```

Do not write the API key into these files. Set `MIMO_API_KEY` only in the runtime environment.

## ChatPaper Temporary Config Rule

If ChatPaper requires an `apikey.ini`, create it only in a temporary working directory. The file may contain provider metadata, but the actual key should come from `OPENAI_KEY` or another runtime environment variable whenever possible.

When a temporary file is unavoidable, write it with BOM-less UTF-8 and delete the directory after the run. Never run ChatPaper from the upstream repository root when using custom provider config; use a temporary working directory and point it at the resolved `<external-tools-root>\ChatPaper` checkout.

## Output Acceptance Gate

A rebuilt reader can replace the official reader path only when:

- `paper.md` is UTF-8, non-empty, and contains `Original` plus `中文翻译` or legacy `中文`.
- `source_map.json` parses and contains stable block IDs.
- `translation_notes.md` records provider, model, external tool status, command summary, failures, and manual review notes.
- There are no obvious corrupted Chinese markers such as repeated `???` labels.
- No configured API key or long key fragment appears in reader outputs, skill files, GitHub package files, or vault notes.
- The old reader has been backed up under `04_full_readers/_backup/`.
