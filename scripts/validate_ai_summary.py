#!/usr/bin/env python3
"""Validate that AI-authored copy is tied to the current pipeline facts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def resolve_key(payload: Any, source: str) -> bool:
    cursor = payload
    for part in source.split("."):
        if part.endswith("[]"):
            key = part[:-2]
            if not isinstance(cursor, dict) or key not in cursor or not isinstance(cursor[key], list):
                return False
            cursor = cursor[key][0] if cursor[key] else {}
            continue
        if "[" in part and part.endswith("]"):
            key, raw_index = part[:-1].split("[", 1)
            if not raw_index.isdigit():
                return False
            index = int(raw_index)
            if not isinstance(cursor, dict) or key not in cursor or not isinstance(cursor[key], list):
                return False
            if index >= len(cursor[key]):
                return False
            cursor = cursor[key][index]
            continue
        if not isinstance(cursor, dict) or part not in cursor:
            return False
        cursor = cursor[part]
    return True


def validate_card(card: dict[str, Any], pipeline: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    title = card.get("title") or card.get("headline")
    body = card.get("body")
    sources = card.get("sources")
    if not isinstance(title, str) or len(title.strip()) < 4:
        errors.append(f"card {index}: missing title/headline")
    if not isinstance(body, str) or len(body.strip()) < 20:
        errors.append(f"card {index}: body is missing or too short")
    if not isinstance(sources, list) or not sources:
        errors.append(f"card {index}: sources must be a non-empty list")
    else:
        for source in sources:
            if not isinstance(source, str) or not resolve_key(pipeline, source):
                errors.append(f"card {index}: source key does not resolve: {source}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated AI website copy.")
    parser.add_argument("--pipeline", default="site/data/pipeline.json")
    parser.add_argument("--summary", default="site/data/ai-summary.json")
    args = parser.parse_args()

    try:
        pipeline = json.loads(Path(args.pipeline).read_text(encoding="utf-8"))
        summary = json.loads(Path(args.summary).read_text(encoding="utf-8"))

        errors: list[str] = []
        metadata = summary.get("metadata", {})
        if metadata.get("sourceSha256") != pipeline["metadata"]["sourceSha256"]:
            errors.append("metadata.sourceSha256 does not match pipeline.metadata.sourceSha256")
        if metadata.get("dataAsOf") != pipeline["metadata"]["dataAsOf"]:
            errors.append("metadata.dataAsOf does not match pipeline.metadata.dataAsOf")
        if metadata.get("sourceFile") != "site/data/pipeline.json":
            errors.append("metadata.sourceFile must be site/data/pipeline.json")

        hero = summary.get("hero")
        if not isinstance(hero, dict):
            errors.append("hero must be an object")
        else:
            errors.extend(validate_card(hero, pipeline, 0))

        cards = summary.get("cards")
        if not isinstance(cards, list) or len(cards) < 3:
            errors.append("cards must contain at least 3 cards")
        else:
            for index, card in enumerate(cards, start=1):
                if not isinstance(card, dict):
                    errors.append(f"card {index}: must be an object")
                else:
                    errors.extend(validate_card(card, pipeline, index))

        summary_text = json.dumps(summary)
        if "TODO" in summary_text or "lorem" in summary_text.lower():
            errors.append("summary contains placeholder text")

        if errors:
            raise ValueError("; ".join(errors))

        print(
            "Validated AI summary against pipeline "
            f"{pipeline['metadata']['sourceSha256'][:12]} with {len(cards or [])} cards."
        )
        return 0
    except Exception as exc:
        print(f"AI summary validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
