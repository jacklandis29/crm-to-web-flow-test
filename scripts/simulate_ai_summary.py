#!/usr/bin/env python3
"""Create demo AI copy from validated pipeline JSON.

This is intentionally a local stand-in for a cloud coding agent. In GitHub,
Claude Code Action can replace this file update by reading the same
site/data/pipeline.json facts and writing site/data/ai-summary.json.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SOURCE_KEYS = {
    "goal": ["metrics.closedWon", "metrics.closedWonGoal", "metrics.closedWonDelta", "metrics.closedWonAttainment"],
    "pipeline": ["metrics.totalRecords", "metrics.pipelineValue", "metrics.weightedPipeline"],
    "region": ["summaries.byRegion[0].name", "summaries.byRegion[0].amount", "summaries.byRegion[0].count"],
    "followup": ["metrics.staleOpenCount", "metadata.staleThresholdDays"],
}


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def build_summary(pipeline: dict[str, Any], mode: str) -> dict[str, Any]:
    metrics = pipeline["metrics"]
    metadata = pipeline["metadata"]
    by_region = pipeline["summaries"]["byRegion"]
    top_region = by_region[0] if by_region else {"name": "N/A", "amount": 0, "count": 0}

    closed_won = metrics["closedWon"]
    goal = metrics["closedWonGoal"]
    delta = metrics["closedWonDelta"]
    attainment = metrics["closedWonAttainment"]
    ahead = delta >= 0
    status = "ahead of goal" if ahead else "behind goal"
    delta_text = money(abs(delta))
    verb = "beat" if ahead else "missed"
    preposition = "by" if ahead else "by"

    if ahead:
        headline = f"Closed-won revenue is ahead of goal by {delta_text}"
        lead = (
            f"The latest CRM refresh shows {money(closed_won)} in closed-won sales "
            f"against a {money(goal)} goal, putting the team at {percent(attainment)} of target."
        )
    else:
        headline = f"Closed-won revenue is behind goal by {delta_text}"
        lead = (
            f"The latest CRM refresh shows {money(closed_won)} in closed-won sales "
            f"against a {money(goal)} goal, leaving the team at {percent(attainment)} of target."
        )

    return {
        "metadata": {
            "generatedBy": mode,
            "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "sourceFile": "site/data/pipeline.json",
            "sourceSha256": metadata["sourceSha256"],
            "dataAsOf": metadata["dataAsOf"],
            "guardrail": "AI copy is generated from validated metrics and does not modify numeric source data.",
        },
        "hero": {
            "headline": headline,
            "body": lead,
            "sources": SOURCE_KEYS["goal"],
        },
        "cards": [
            {
                "title": "Goal status changed",
                "body": (
                    f"Closed-won sales {verb} the {money(goal)} goal {preposition} {delta_text}. "
                    f"The website copy changed because the CRM-derived metric changed."
                ),
                "sources": SOURCE_KEYS["goal"],
            },
            {
                "title": "Pipeline context",
                "body": (
                    f"The validated export contains {metrics['totalRecords']} opportunities totaling "
                    f"{money(metrics['pipelineValue'])}, with {money(metrics['weightedPipeline'])} in weighted pipeline."
                ),
                "sources": SOURCE_KEYS["pipeline"],
            },
            {
                "title": "Regional concentration",
                "body": (
                    f"{top_region['name']} is the largest region in this refresh at "
                    f"{money(top_region['amount'])} across {top_region['count']} opportunities."
                ),
                "sources": SOURCE_KEYS["region"],
            },
            {
                "title": "Follow-up queue",
                "body": (
                    f"{metrics['staleOpenCount']} open opportunities have not been updated in "
                    f"{metadata['staleThresholdDays']}+ days, so they stay visible for review."
                ),
                "sources": SOURCE_KEYS["followup"],
            },
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def stable(payload: dict[str, Any]) -> dict[str, Any]:
    copy_payload = copy.deepcopy(payload)
    copy_payload.get("metadata", {}).pop("generatedAt", None)
    return copy_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate demo AI copy from validated pipeline JSON.")
    parser.add_argument("--pipeline", default="site/data/pipeline.json", help="Path to validated pipeline JSON.")
    parser.add_argument("--output", default="site/data/ai-summary.json", help="Path to generated AI copy JSON.")
    parser.add_argument("--mode", default="local-simulated-ai", help="Value recorded in metadata.generatedBy.")
    parser.add_argument("--check", action="store_true", help="Fail if the generated AI summary is stale.")
    args = parser.parse_args()

    pipeline_path = Path(args.pipeline)
    output_path = Path(args.output)

    try:
        pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
        summary = build_summary(pipeline, args.mode)
        if args.check:
            if not output_path.exists():
                raise ValueError("AI summary is missing. Run `npm run ai:local` first.")
            existing = json.loads(output_path.read_text(encoding="utf-8"))
            if stable(summary) != stable(existing):
                raise ValueError("AI summary is stale. Run `npm run ai:local` and commit the result.")
        else:
            write_json(output_path, summary)
        action = "Validated" if args.check else "Generated"
        print(f"{action} AI summary: {summary['hero']['headline']}")
        return 0
    except Exception as exc:
        print(f"AI summary generation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
