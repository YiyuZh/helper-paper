#!/usr/bin/env python3
"""Build a Helper Paper reader through staging, validation, and safe replacement.

This v1 pipeline assembles source-grounded intermediate files. It does not run
GPT Academic or ChatPaper by itself; wrapper skills or a human operator must
produce the source, translation, and ChatPaper markdown inputs first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SAFE_PAPER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
ANCHOR_RE = re.compile(r"^\s*\[(?:anchor|source_anchor):\s*([^\]]+)\]\s*", re.IGNORECASE)
SUCCESS_STATUSES = {"success", "ok", "ready", "completed"}
REQUIRED_RELEASE_TOOLS = ("source_extraction", "gpt_academic", "chatpaper")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def blockify(text: str, *, limit: int | None = None) -> list[str]:
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    if not chunks:
        chunks = [line.strip() for line in text.splitlines() if line.strip()]
    return chunks[:limit] if limit is not None else chunks


def split_anchor(block: str) -> tuple[str | None, str]:
    match = ANCHOR_RE.match(block)
    if not match:
        return None, block.strip()
    return match.group(1).strip(), block[match.end() :].strip()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def validate_paper_id(paper_id: str) -> str:
    if not SAFE_PAPER_ID.fullmatch(paper_id) or ".." in paper_id:
        raise SystemExit(
            "Invalid --paper-id. Use only letters, numbers, dot, underscore, and hyphen; "
            "do not use path separators or traversal segments."
        )
    return paper_id


def ensure_under(child: Path, parent: Path) -> None:
    child_resolved = child.resolve()
    parent_resolved = parent.resolve()
    if parent_resolved not in child_resolved.parents and child_resolved != parent_resolved:
        raise SystemExit(f"Refusing path outside expected root: {child}")


def ensure_provider_ready(provider: str) -> dict[str, Any]:
    checker = Path(__file__).with_name("check_translation_providers.py")
    cmd = [sys.executable, str(checker), "--provider", provider, "--require-ready"]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.stdout or proc.stderr or f"Provider check failed: {provider}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw_output": proc.stdout, "status": "ready_unparsed"}


def fake_inputs(max_blocks: int | None) -> tuple[list[str], list[str], str, bool]:
    source = blockify(
        "[anchor: fixture-page-1] This is a fake source block for helper-paper pipeline testing.\n\n"
        "[anchor: fixture-page-2] The second fake block checks source map generation and integrity.",
        limit=max_blocks or 20,
    )
    translation = blockify(
        "这是用于 helper-paper 管线测试的伪翻译。\n\n"
        "第二个伪块用于检查 source map。",
        limit=max_blocks or 20,
    )
    chatpaper = "Fake ChatPaper summary: contribution, method, limitation, and Q&A are available."
    return source, translation, chatpaper, False


def production_inputs(args: argparse.Namespace) -> tuple[list[str], list[str], str, bool]:
    missing = [
        name
        for name, value in {
            "--pdf": args.pdf,
            "--source-md": args.source_md,
            "--translation-md": args.translation_md,
            "--chatpaper-md": args.chatpaper_md,
        }.items()
        if value is None
    ]
    if missing:
        raise SystemExit("Production assembly requires " + ", ".join(missing) + ".")

    for path in (args.pdf, args.source_md, args.translation_md, args.chatpaper_md):
        if not path.is_file():
            raise SystemExit(f"Required input not found: {path}")
    if args.pdf.stat().st_size == 0:
        raise SystemExit(f"PDF is empty: {args.pdf}")
    if args.max_blocks is not None and not args.allow_partial:
        raise SystemExit("--max-blocks is only allowed with --allow-partial in production mode.")

    source_blocks = blockify(read_text(args.source_md))
    translation_blocks = blockify(read_text(args.translation_md))
    if not source_blocks:
        raise SystemExit("--source-md did not contain any source blocks.")
    if not translation_blocks:
        raise SystemExit("--translation-md did not contain any translation blocks.")

    partial = False
    if len(source_blocks) != len(translation_blocks):
        if not args.allow_partial:
            raise SystemExit(
                "Source and translation block counts must match unless --allow-partial is set. "
                f"source={len(source_blocks)} translation={len(translation_blocks)}"
            )
        partial = True

    if args.allow_partial:
        limit = min(len(source_blocks), len(translation_blocks))
        if args.max_blocks is not None:
            limit = min(limit, args.max_blocks)
        source_blocks = source_blocks[:limit]
        translation_blocks = translation_blocks[:limit]
        partial = True

    chatpaper_text = read_text(args.chatpaper_md).strip()
    if args.replace and len(chatpaper_text) < 40:
        raise SystemExit("--replace requires non-empty ChatPaper review output with at least 40 characters.")

    return source_blocks, translation_blocks, chatpaper_text, partial


def load_tool_manifest(path: Path | None, *, require_release: bool) -> dict[str, Any] | None:
    if path is None:
        if require_release:
            raise SystemExit("--replace requires --tool-manifest with successful source_extraction, gpt_academic, and chatpaper runs.")
        return None
    if not path.is_file():
        raise SystemExit(f"Tool manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Tool manifest is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Tool manifest must be a JSON object.")

    if require_release:
        for tool in REQUIRED_RELEASE_TOOLS:
            entry = data.get(tool)
            if not isinstance(entry, dict):
                raise SystemExit(f"--tool-manifest missing object: {tool}")
            status = str(entry.get("status") or "").lower()
            if status not in SUCCESS_STATUSES:
                raise SystemExit(f"--tool-manifest marks {tool} as not successful: {status or 'missing'}")
            command = entry.get("command")
            if not isinstance(command, str) or not command.strip():
                raise SystemExit(f"--tool-manifest missing command for {tool}")
            if tool in {"gpt_academic", "chatpaper"}:
                revision = entry.get("upstream_revision") or entry.get("revision")
                if not isinstance(revision, str) or not revision.strip() or revision.strip().lower() == "unknown":
                    raise SystemExit(f"--tool-manifest missing upstream revision for {tool}")
        failures = data.get("failures", [])
        if failures:
            raise SystemExit("--tool-manifest contains failures; refusing --replace.")

    return data


def tool_status_from_args(args: argparse.Namespace, manifest: dict[str, Any] | None) -> dict[str, Any]:
    if manifest is not None:
        return {
            "source_extraction": manifest.get("source_extraction"),
            "gpt_academic": manifest.get("gpt_academic"),
            "chatpaper": manifest.get("chatpaper"),
            "manifest": str(args.tool_manifest),
            "failures": manifest.get("failures", []),
        }
    return {
        "gpt_academic": {
            "input": str(args.translation_md) if args.translation_md else None,
            "status": "provided_intermediate" if args.translation_md else "fixture",
            "command": None,
            "upstream_revision": args.gpt_academic_revision or "unknown",
        },
        "chatpaper": {
            "input": str(args.chatpaper_md) if args.chatpaper_md else None,
            "status": "provided_intermediate" if args.chatpaper_md else "fixture",
            "command": None,
            "upstream_revision": args.chatpaper_revision or "unknown",
        },
        "source_extraction": {
            "input": str(args.source_md) if args.source_md else None,
            "status": "provided_intermediate" if args.source_md else "fixture",
            "command": None,
        },
        "pdf": str(args.pdf) if args.pdf else None,
    }


def build_staging(
    args: argparse.Namespace,
    staging: Path,
    *,
    provider_report: dict[str, Any] | None,
) -> tuple[int, bool]:
    staging.mkdir(parents=True, exist_ok=False)
    (staging / "assets").mkdir(exist_ok=True)
    manifest = load_tool_manifest(args.tool_manifest, require_release=args.replace and not args.fake)

    if args.fake:
        source_blocks, translation_blocks, chatpaper_text, partial = fake_inputs(args.max_blocks)
    else:
        source_blocks, translation_blocks, chatpaper_text, partial = production_inputs(args)

    source_map: dict[str, Any] = {
        "paper_id": args.paper_id,
        "source_file": str(args.source_md) if args.source_md else None,
        "pdf": str(args.pdf) if args.pdf else None,
        "partial": partial,
        "blocks": [],
    }
    lines = [
        f"# {args.paper_id}",
        "",
        f"Provider: `{args.provider}`",
        "",
        "See `source_map.json` for source anchors.",
        "",
    ]
    for index, original_raw in enumerate(source_blocks, start=1):
        source_anchor, original = split_anchor(original_raw)
        block_id = f"{args.paper_id}-B{index:04d}"
        digest = hashlib.sha256(original.encode("utf-8")).hexdigest()[:16]
        block_record: dict[str, Any] = {
            "block_id": block_id,
            "index": index,
            "sha256_16": digest,
            "original_text": original,
        }
        if source_anchor:
            block_record["source_anchor"] = source_anchor
        else:
            block_record["anchor_unavailable"] = True
        source_map["blocks"].append(block_record)
        lines.extend(
            [
                f"## Block {index} `{block_id}`",
                "",
                f"**block_id:** `{block_id}`",
                "",
                f"**Original:** {original}",
                "",
                f"**中文翻译:** {translation_blocks[index - 1]}",
                "",
                "**导师阅读提示:** 读完这一块后，用自己的话写研究问题、方法、证据和不确定点。",
                "",
            ]
        )
    lines.extend(["## ChatPaper 摘要/复核", "", chatpaper_text.strip(), ""])

    (staging / "paper.md").write_text("\n".join(lines), encoding="utf-8")
    (staging / "source_map.json").write_text(json.dumps(source_map, ensure_ascii=False, indent=2), encoding="utf-8")
    notes = {
        "paper_id": args.paper_id,
        "provider": args.provider,
        "model": args.model or "from provider environment",
        "fake": args.fake,
        "partial": partial,
        "command": " ".join(sys.argv),
        "api_status": provider_report or {"status": "skipped_for_fake_fixture"},
        "tool_status": tool_status_from_args(args, manifest),
        "output_status": (
            "partial_staging_generated"
            if partial
            else ("validated_for_replacement" if args.replace else "staging_generated")
        ),
        "failures": manifest.get("failures", []) if manifest else [],
        "review_notes": [
            "Reader assembled in staging before replacement.",
            "Original blocks come from --source-md, not from translation output.",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (staging / "translation_notes.md").write_text(
        "# translation notes\n\n```json\n" + json.dumps(notes, ensure_ascii=False, indent=2) + "\n```\n",
        encoding="utf-8",
    )
    return len(source_blocks), partial


def validate_reader(staging: Path, min_blocks: int) -> None:
    checker = Path(__file__).with_name("check_reader_integrity.py")
    cmd = [sys.executable, str(checker), "--reader", str(staging), "--min-blocks", str(min_blocks)]
    subprocess.run(cmd, check=True)


def replace_final(staging: Path, final: Path, backup_root: Path) -> Path | None:
    final.parent.mkdir(parents=True, exist_ok=True)
    incoming = final.parent / f".{final.name}.incoming-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    backup: Path | None = None
    final_existed = final.exists()
    backup_made = False
    if incoming.exists():
        shutil.rmtree(incoming)

    shutil.copytree(staging, incoming)
    try:
        if final_existed:
            backup_root.mkdir(parents=True, exist_ok=True)
            backup = backup_root / f"{final.name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            shutil.move(str(final), str(backup))
            backup_made = True
        incoming.rename(final)
        return backup
    except Exception:
        if ((not final_existed) or backup_made) and final.exists():
            shutil.rmtree(final, ignore_errors=True)
        if backup_made and backup and backup.exists():
            shutil.move(str(backup), str(final))
        if incoming.exists():
            shutil.rmtree(incoming, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Helper Paper reader through staging.")
    parser.add_argument("--vault-root", required=True)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--provider", choices=("auto", "deepseek", "mimo"), default="auto")
    parser.add_argument("--model", help="Model used by the external tool, for metadata only.")
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--source-md", type=Path, help="Source-grounded original text blocks extracted from the PDF.")
    parser.add_argument("--translation-md", type=Path, help="Chinese translation blocks aligned to --source-md.")
    parser.add_argument("--chatpaper-md", type=Path, help="ChatPaper summary/review output.")
    parser.add_argument("--gpt-academic-revision", help="Upstream gpt_academic git revision used to produce --translation-md.")
    parser.add_argument("--chatpaper-revision", help="Upstream ChatPaper git revision used to produce --chatpaper-md.")
    parser.add_argument("--tool-manifest", type=Path, help="JSON manifest proving upstream source extraction, gpt_academic, and ChatPaper success. Required with --replace.")
    parser.add_argument("--fake", action="store_true", help="Generate deterministic fixture content for tests.")
    parser.add_argument("--max-blocks", type=int, help="Only for --fake, or production --allow-partial staging.")
    parser.add_argument("--allow-partial", action="store_true", help="Allow partial staging output. Partial output cannot replace final reader.")
    parser.add_argument("--replace", action="store_true", help="Replace the official reader after validation.")
    parser.add_argument("--skip-provider-check", action="store_true", help="Skip provider readiness check. Intended only for fake tests.")
    args = parser.parse_args()

    args.paper_id = validate_paper_id(args.paper_id)
    if args.skip_provider_check and not args.fake:
        raise SystemExit("--skip-provider-check is allowed only with --fake.")
    if args.replace and (args.fake or args.skip_provider_check or args.allow_partial):
        raise SystemExit("--replace is disabled for fake, provider-skipped, or partial runs.")

    vault = Path(args.vault_root).resolve()
    reader_root = vault / "04_full_readers"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    staging = reader_root / "_staging" / f"{args.paper_id}_{timestamp}"
    final = reader_root / args.paper_id
    backup_root = reader_root / "_backup"
    for path in (staging, final, backup_root):
        ensure_under(path, reader_root)

    provider_report = None
    if not args.fake and not args.skip_provider_check:
        provider_report = ensure_provider_ready(args.provider)

    block_count, partial = build_staging(args, staging, provider_report=provider_report)
    min_blocks = 20 if args.replace else block_count
    validate_reader(staging, min_blocks=min_blocks)

    report = {"ok": True, "staging": str(staging), "final": str(final), "replaced": False, "backup": None, "partial": partial}
    if args.replace:
        backup = replace_final(staging, final, backup_root)
        report["replaced"] = True
        report["backup"] = str(backup) if backup else None
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
