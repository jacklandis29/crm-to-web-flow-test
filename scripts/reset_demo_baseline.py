#!/usr/bin/env python3
"""Reset the mock CRM demo to the behind-goal baseline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Any

from mock_crm_store import DEFAULT_CRM_PATH, FORECAST_BY_STAGE, load_database, save_database, utc_now, validated_records
from mock_crm_update import ensure_clean_worktree, pull_latest, push_with_rebase_retry, run


BASELINE_OPPORTUNITY_ID = "OPP-2026-002"
BASELINE_FIELDS: dict[str, Any] = {
    "stage": "Proposal",
    "forecastCategory": FORECAST_BY_STAGE["Proposal"],
    "amount": 920000,
    "probability": 0.64,
}


def reset_crm(actor: str) -> bool:
    database = load_database(DEFAULT_CRM_PATH)
    match = next(
        (record for record in database["opportunities"] if record["opportunityId"] == BASELINE_OPPORTUNITY_ID),
        None,
    )
    if match is None:
        raise ValueError(f"Opportunity not found: {BASELINE_OPPORTUNITY_ID}")

    changes: dict[str, Any] = {}
    for key, value in BASELINE_FIELDS.items():
        current = match.get(key)
        changed = float(current) != float(value) if isinstance(value, (int, float)) else current != value
        if changed:
            changes[key] = {"from": current, "to": value}
            match[key] = value

    if not changes:
        print("Mock CRM is already at the behind-goal baseline.")
        return False

    now = utc_now()
    match["lastUpdated"] = now[:10]
    metadata = database.setdefault("metadata", {})
    metadata["revision"] = int(metadata.get("revision", 0)) + 1
    metadata["updatedAt"] = now
    metadata["changedBy"] = actor
    database.setdefault("events", []).append(
        {
            "id": f"evt-{now.replace(':', '').replace('-', '').replace('T', '-')}",
            "type": "demo.baseline_reset",
            "opportunityId": BASELINE_OPPORTUNITY_ID,
            "createdAt": now,
            "actor": actor,
            "changes": changes,
        }
    )
    validated_records(database)
    save_database(database, DEFAULT_CRM_PATH)
    print(f"Reset mock CRM baseline: {BASELINE_OPPORTUNITY_ID}")
    return True


def has_staged_changes() -> bool:
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], text=True)
    return result.returncode == 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset the mock CRM demo to a clean behind-goal baseline.")
    parser.add_argument("--actor", default="demo.reset.user")
    parser.add_argument("--commit", action="store_true", help="Commit CRM and generated website baseline files.")
    parser.add_argument("--push", action="store_true", help="Push committed baseline files to origin/main.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()

    try:
        if args.commit or args.push:
            ensure_clean_worktree()
        if args.push:
            pull_latest(args.remote, args.branch)

        reset_crm(args.actor)
        run(["npm", "run", "generate"])

        if args.commit:
            run(
                [
                    "git",
                    "add",
                    "data/mock-crm.json",
                    "site/data/pipeline.json",
                    "site/data/audit-log.json",
                    "site/data/ai-summary.json",
                ]
            )
            if has_staged_changes():
                run(
                    [
                        "git",
                        "commit",
                        "-m",
                        "Reset mock CRM demo baseline",
                        "--",
                        "data/mock-crm.json",
                        "site/data/pipeline.json",
                        "site/data/audit-log.json",
                        "site/data/ai-summary.json",
                    ]
                )
            else:
                print("Generated baseline already matches the current commit.")

        if args.push:
            push_with_rebase_retry(args.remote, args.branch)
        return 0
    except Exception as exc:
        print(f"Demo baseline reset failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
