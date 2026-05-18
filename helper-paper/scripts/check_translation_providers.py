#!/usr/bin/env python3
"""Read-only checks for helper-paper translation providers.

The script never prints API keys and never writes configuration files.
It treats empty model output as a failed smoke test because MiMo reasoning
models can return HTTP 200 with empty final content when token budgets are
too small.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from typing import Any


DEEPSEEK_MODEL_DEPRECATION_DATE = date(2026, 7, 24)


@dataclass(frozen=True)
class Provider:
    name: str
    key_envs: tuple[str, ...]
    base_envs: tuple[str, ...]
    default_base_url: str | None
    model_envs: tuple[str, ...]
    default_model: str
    anthropic_base_envs: tuple[str, ...] = ()
    default_anthropic_base_url: str | None = None
    notes: tuple[str, ...] = ()


PROVIDERS = {
    "deepseek": Provider(
        name="deepseek",
        key_envs=("DEEPSEEK_API_KEY",),
        base_envs=("DEEPSEEK_API_BASE_URL", "DEEPSEEK_BASE_URL"),
        default_base_url="https://api.deepseek.com",
        model_envs=("DEEPSEEK_MODEL",),
        default_model="deepseek-v4-pro",
        notes=(
            "Supported OpenAI-compatible provider.",
            "Production default provider for helper-paper.",
            "Default current model is deepseek-v4-pro for quality-first translation and review.",
            "Use deepseek-v4-flash only when speed or cost matters more than quality.",
            "Legacy deepseek-chat/deepseek-reasoner retire on 2026-07-24; do not use them as new defaults.",
        ),
    ),
    "mimo": Provider(
        name="mimo",
        key_envs=("MIMO_API_KEY", "XIAOMI_API_KEY"),
        base_envs=("MIMO_API_BASE_URL", "XIAOMI_API_BASE_URL"),
        default_base_url="https://token-plan-cn.xiaomimimo.com/v1",
        model_envs=("MIMO_MODEL", "XIAOMI_MODEL"),
        default_model="mimo-v2.5-pro",
        anthropic_base_envs=("MIMO_ANTHROPIC_BASE_URL", "XIAOMI_ANTHROPIC_BASE_URL"),
        default_anthropic_base_url="https://token-plan-cn.xiaomimimo.com/anthropic",
        notes=(
            "Production provider for token-plan/subscription MiMo keys in helper-paper.",
            "Token-plan OpenAI-compatible base URL is https://token-plan-cn.xiaomimimo.com/v1.",
            "Official console keys may require a different official base URL; set MIMO_API_BASE_URL explicitly.",
            "Never let legacy OpenAI model names such as gpt-3.5-turbo-16k reach MiMo.",
        ),
    ),
}


def windows_user_env(name: str) -> str | None:
    if os.name != "nt":
        return None
    try:
        import winreg  # type: ignore[import-not-found]

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        if isinstance(value, str) and value:
            return value
    except OSError:
        return None
    return None


def first_env(names: tuple[str, ...]) -> tuple[str | None, str | None]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return name, value
        value = windows_user_env(name)
        if value:
            return name, value
    return None, None


def chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def anthropic_messages_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/anthropic"):
        return f"{base}/v1/messages"
    if base.endswith("/anthropic/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def parse_openai_content(parsed: dict[str, Any]) -> str:
    try:
        content = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                value = item.get("text") or item.get("content")
                if isinstance(value, str):
                    parts.append(value)
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts).strip()
    return str(content).strip()


def parse_anthropic_content(parsed: dict[str, Any]) -> str:
    content = parsed.get("content")
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                value = item.get("text")
                if isinstance(value, str):
                    parts.append(value)
        return "".join(parts).strip()
    if isinstance(content, str):
        return content.strip()
    return ""


def http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:800]
        return {
            "ok": False,
            "error_type": "http_error",
            "status_code": exc.code,
            "message": body,
        }
    except Exception as exc:  # noqa: BLE001 - exact provider errors are useful here.
        return {
            "ok": False,
            "error_type": exc.__class__.__name__,
            "message": str(exc),
        }
    return {"ok": True, "status_code": 200, "parsed": parsed}


def smoke_openai_compatible(provider: Provider, key: str, base_url: str, model: str, timeout: int) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Return only this exact final answer: ok. Do not explain."},
        ],
        "temperature": 0,
        "stream": False,
    }
    if provider.name in {"mimo", "deepseek"}:
        payload["max_completion_tokens"] = 512
    else:
        payload["max_tokens"] = 8

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "helper-paper-provider-check/2.0",
        "Authorization": f"Bearer {key}",
    }
    if provider.name == "mimo":
        headers["api-key"] = key

    result = http_post_json(chat_url(base_url), payload, headers, timeout)
    if not result.get("ok"):
        return result

    parsed = result.get("parsed")
    if not isinstance(parsed, dict):
        return {"ok": False, "error_type": "unexpected_response", "message": "response is not a JSON object"}

    content = parse_openai_content(parsed)
    if not content:
        return {
            "ok": False,
            "error_type": "empty_content",
            "message": "provider returned HTTP 200 but no final message content",
        }

    return {
        "ok": True,
        "status_code": 200,
        "sample": content[:120],
    }


def smoke_anthropic_compatible(key: str, base_url: str, model: str, timeout: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "max_tokens": 512,
        "temperature": 0,
        "messages": [
            {"role": "user", "content": "Return only this exact final answer: ok. Do not explain."},
        ],
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "helper-paper-provider-check/2.0",
        "x-api-key": key,
        "api-key": key,
        "anthropic-version": "2023-06-01",
    }
    result = http_post_json(anthropic_messages_url(base_url), payload, headers, timeout)
    if not result.get("ok"):
        return result

    parsed = result.get("parsed")
    if not isinstance(parsed, dict):
        return {"ok": False, "error_type": "unexpected_response", "message": "response is not a JSON object"}

    content = parse_anthropic_content(parsed)
    if not content:
        return {
            "ok": False,
            "error_type": "empty_content",
            "message": "provider returned HTTP 200 but no final message content",
        }

    return {
        "ok": True,
        "status_code": 200,
        "sample": content[:120],
    }


def check_provider(provider: Provider, *, smoke: bool, check_anthropic: bool, timeout: int) -> dict[str, Any]:
    key_env, key = first_env(provider.key_envs)
    base_env, base = first_env(provider.base_envs)
    model_env, model = first_env(provider.model_envs)
    anthropic_base_env, anthropic_base = first_env(provider.anthropic_base_envs)

    result: dict[str, Any] = {
        "provider": provider.name,
        "configured": bool(key),
        "key_env": key_env,
        "base_url_env": base_env,
        "base_url_configured": bool(base or provider.default_base_url),
        "model_env": model_env,
        "model": model or provider.default_model,
        "notes": list(provider.notes),
    }

    if provider.name == "deepseek" and date.today() >= DEEPSEEK_MODEL_DEPRECATION_DATE:
        result["warning"] = "Legacy deepseek-chat/deepseek-reasoner retirement date has passed; use deepseek-v4-flash or deepseek-v4-pro."

    if not key:
        result["status"] = "not_configured"
        return result

    final_base = base or provider.default_base_url
    if not final_base:
        result["status"] = "missing_base_url"
        result["error"] = f"Set one of: {', '.join(provider.base_envs)}"
        return result

    result["status"] = "configured"
    result["base_url"] = final_base

    if not smoke:
        result["smoke"] = "skipped"
    else:
        smoke_result = smoke_openai_compatible(provider, key, final_base, result["model"], timeout)
        result["smoke"] = smoke_result
        result["status"] = "ready" if smoke_result.get("ok") else "smoke_failed"

    if check_anthropic and provider.name == "mimo":
        final_anthropic_base = anthropic_base or provider.default_anthropic_base_url
        result["anthropic_base_url_env"] = anthropic_base_env
        result["anthropic_base_url"] = final_anthropic_base
        if not smoke:
            result["anthropic_smoke"] = "skipped"
        elif final_anthropic_base:
            result["anthropic_smoke"] = smoke_anthropic_compatible(key, final_anthropic_base, result["model"], timeout)
        else:
            result["anthropic_smoke"] = {
                "ok": False,
                "error_type": "missing_anthropic_base_url",
                "message": "Set MIMO_ANTHROPIC_BASE_URL or XIAOMI_ANTHROPIC_BASE_URL",
            }

    return result


def select_auto(results: list[dict[str, Any]]) -> str | None:
    # Prefer DeepSeek Pro as the production route; keep MiMo as fallback.
    for preferred in ("deepseek", "mimo"):
        for result in results:
            if result["provider"] == preferred and result["status"] in {"ready", "configured"}:
                return preferred
    return None


def result_failed(result: dict[str, Any], *, check_anthropic: bool) -> bool:
    if result.get("status") == "smoke_failed":
        return True
    if check_anthropic and result.get("provider") == "mimo":
        anthropic = result.get("anthropic_smoke")
        if isinstance(anthropic, dict) and not anthropic.get("ok"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Check helper-paper translation providers without writing files.")
    parser.add_argument("--provider", choices=("auto", "deepseek", "mimo"), default="auto")
    parser.add_argument("--no-smoke", action="store_true", help="Only inspect environment variables; do not call APIs.")
    parser.add_argument("--check-anthropic", action="store_true", help="Also smoke-test MiMo's Anthropic-compatible endpoint.")
    parser.add_argument("--require-ready", action="store_true", help="Exit non-zero if no provider is ready/configured.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    names = ("deepseek", "mimo") if args.provider == "auto" else (args.provider,)
    results = [
        check_provider(PROVIDERS[name], smoke=not args.no_smoke, check_anthropic=args.check_anthropic, timeout=args.timeout)
        for name in names
    ]
    selected = select_auto(results) if args.provider == "auto" else (
        results[0]["provider"] if results and results[0]["status"] in {"ready", "configured"} else None
    )

    report = {
        "provider_strategy": args.provider,
        "selected_provider": selected,
        "results": results,
        "secrets_printed": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if any(result_failed(result, check_anthropic=args.check_anthropic) for result in results):
        return 1
    if args.require_ready and selected is None:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
