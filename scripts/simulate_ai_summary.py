#!/usr/bin/env python3
"""Author demo website copy from validated pipeline JSON.

This is a deterministic, offline stand-in for the cloud AI authoring step so
the live demo flip is 100% repeatable. In the cloud, a Claude Routine reads the
exact same site/data/pipeline.json facts and writes site/data/ai-summary.json
under the identical contract: it may shape the language, it may not invent a
number, and every substantive claim must cite a source key that resolves into
the validated pipeline snapshot.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def plural(count: int, singular: str, many: str | None = None) -> str:
    word = singular if count == 1 else (many or singular + "s")
    return f"{count} {word}"


def stage_index(by_stage: list[dict[str, Any]], name: str) -> int | None:
    for index, row in enumerate(by_stage):
        if row["name"] == name:
            return index
    return None


def largest_closed_won(opportunities: list[dict[str, Any]]) -> tuple[int, dict[str, Any]] | None:
    """Return (index, record) for the biggest Closed Won deal, by amount."""
    won = [(index, opp) for index, opp in enumerate(opportunities) if opp["stage"] == "Closed Won"]
    if not won:
        return None
    return max(won, key=lambda pair: pair[1]["amount"])


def build_summary(pipeline: dict[str, Any], mode: str) -> dict[str, Any]:
    metrics = pipeline["metrics"]
    metadata = pipeline["metadata"]
    summaries = pipeline["summaries"]
    opportunities = pipeline["opportunities"]
    by_stage = summaries["byStage"]
    by_region = summaries["byRegion"]
    by_owner = summaries["byOwner"]

    closed_won = metrics["closedWon"]
    goal = metrics["closedWonGoal"]
    delta = metrics["closedWonDelta"]
    attainment = metrics["closedWonAttainment"]
    ahead = delta >= 0
    gap_text = money(abs(delta))

    top_region = by_region[0] if by_region else {"name": "N/A", "amount": 0, "count": 0}
    top_owner = by_owner[0] if by_owner else {"name": "N/A", "amount": 0, "count": 0}

    # ---- Goal status (hero + first card) -------------------------------------
    goal_sources = [
        "metrics.closedWon",
        "metrics.closedWonGoal",
        "metrics.closedWonDelta",
        "metrics.closedWonAttainment",
    ]

    if ahead:
        headline = f"Closed-won sales are ahead of goal by {gap_text}"
    else:
        headline = f"Closed-won sales are behind goal by {gap_text}"

    # ---- "What's driving it": name the actual deal ---------------------------
    top_won = largest_closed_won(opportunities)
    won_count = stage_count(by_stage, "Closed Won")

    if top_won is not None:
        won_index, won_deal = top_won
        deal_prefix = f"opportunities[{won_index}]"
        deal_sources = [f"{deal_prefix}.account", f"{deal_prefix}.amount", f"{deal_prefix}.owner", f"{deal_prefix}.region"]
        if ahead:
            driver_body = (
                f"{won_deal['account']} closed at {money(won_deal['amount'])} "
                f"— booked by {won_deal['owner']} in the {won_deal['region']} region, "
                f"the deal that carried the team past goal."
            )
        else:
            driver_body = (
                f"The biggest win on the board so far is {won_deal['account']} at "
                f"{money(won_deal['amount'])}, booked by {won_deal['owner']} in the "
                f"{won_deal['region']} region. It is not yet enough to clear the target."
            )
    else:
        deal_sources = ["metrics.closedWon", "metrics.totalRecords"]
        driver_body = (
            f"No opportunities have closed won yet this period, leaving the full "
            f"{money(goal)} target still to play for."
        )

    # ---- Hero lead -----------------------------------------------------------
    open_pipeline = metrics["openPipeline"]
    hero_sources = list(goal_sources)
    if ahead:
        lead = (
            f"The latest CRM refresh books {money(closed_won)} in closed-won sales against the "
            f"{money(goal)} goal — {percent(attainment)} of target. "
        )
        if top_won is not None:
            won_index, won_deal = top_won
            lead += f"{won_deal['account']}'s {money(won_deal['amount'])} close pushed the team over the line, "
            hero_sources += [f"opportunities[{won_index}].account", f"opportunities[{won_index}].amount"]
        lead += f"with {money(open_pipeline)} still open across the pipeline."
        hero_sources.append("metrics.openPipeline")
    else:
        lead = (
            f"The latest CRM refresh shows {money(closed_won)} in closed-won sales against the "
            f"{money(goal)} goal — {percent(attainment)} of target, a {gap_text} gap to close. "
            f"{money(open_pipeline)} of pipeline is still open and working to close it."
        )
        hero_sources.append("metrics.openPipeline")

    # ---- Pipeline coverage card ----------------------------------------------
    coverage_sources = [
        "metrics.openPipeline",
        "metrics.weightedPipeline",
        "summaries.byOwner[0].name",
        "summaries.byOwner[0].amount",
    ]
    coverage_body = (
        f"{money(metrics['openPipeline'])} of pipeline is still open. Weighted by win "
        f"probability, the full book forecasts to {money(metrics['weightedPipeline'])}. "
        f"{top_owner['name']} is carrying the most at {money(top_owner['amount'])}."
    )

    # ---- Needs-attention card ------------------------------------------------
    stale = metrics["staleOpenCount"]
    threshold = metadata["staleThresholdDays"]
    attention_sources = ["metrics.staleOpenCount", "metadata.staleThresholdDays"]
    attention_body = (
        f"{plural(stale, 'open opportunity', 'open opportunities')} have gone untouched for "
        f"{threshold}+ days and stay flagged for follow-up."
    )
    neg_index = stage_index(by_stage, "Negotiation")
    if neg_index is not None:
        neg = by_stage[neg_index]
        attention_sources += [f"summaries.byStage[{neg_index}].count", f"summaries.byStage[{neg_index}].amount"]
        attention_body += (
            f" Closest to landing: {plural(neg['count'], 'deal')} worth "
            f"{money(neg['amount'])} sitting in Negotiation."
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
            "sources": hero_sources,
        },
        "cards": [
            {
                "title": "Goal status",
                "body": (
                    f"Closed-won revenue {'beat' if ahead else 'missed'} the {money(goal)} target "
                    f"by {gap_text}, landing at {percent(attainment)} attainment."
                ),
                "sources": goal_sources,
            },
            {
                "title": "What's driving it",
                "body": driver_body,
                "sources": deal_sources,
            },
            {
                "title": "Pipeline coverage",
                "body": coverage_body,
                "sources": coverage_sources,
            },
            {
                "title": "Needs attention",
                "body": attention_body,
                "sources": attention_sources,
            },
        ],
    }


def stage_count(by_stage: list[dict[str, Any]], name: str) -> int:
    index = stage_index(by_stage, name)
    return by_stage[index]["count"] if index is not None else 0


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
