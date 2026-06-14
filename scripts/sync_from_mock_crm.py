#!/usr/bin/env python3
"""Generate public website data from the mock CRM store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mock_crm_store import (
    build_audit,
    build_change_report,
    build_pipeline,
    load_database,
    previous_published_pipeline,
    stable_payload,
    write_json,
    write_site_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync mock CRM data into website JSON artifacts.")
    parser.add_argument("--source", default="data/mock-crm.json", help="Mock CRM JSON database.")
    parser.add_argument("--out-dir", default="site/data", help="Generated website data directory.")
    parser.add_argument("--check", action="store_true", help="Fail if generated website data is stale.")
    args = parser.parse_args()

    source_path = Path(args.source)
    out_dir = Path(args.out_dir)

    try:
        database = load_database(source_path)
        pipeline = build_pipeline(database, source_path)
        audit = build_audit(pipeline, database)

        pipeline_path = out_dir / "pipeline.json"
        audit_path = out_dir / "audit-log.json"
        if args.check:
            if not pipeline_path.exists() or not audit_path.exists():
                raise ValueError("Generated CRM site data is missing. Run `npm run crm:sync` first.")
            existing_pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
            existing_audit = json.loads(audit_path.read_text(encoding="utf-8"))
            if stable_payload(pipeline) != stable_payload(existing_pipeline):
                raise ValueError("site/data/pipeline.json is stale for data/mock-crm.json.")
            if stable_payload(audit) != stable_payload(existing_audit):
                raise ValueError("site/data/audit-log.json is stale for data/mock-crm.json.")
        else:
            pipeline["changeReport"] = build_change_report(pipeline, previous_published_pipeline())
            write_json(pipeline_path, pipeline)
            write_json(audit_path, audit)

        action = "Validated" if args.check else "Generated"
        print(
            f"{action} mock CRM snapshot revision {pipeline['metadata']['sourceRevision']} "
            f"({pipeline['metrics']['pipelineValue']:,.0f} pipeline value)."
        )
        return 0
    except Exception as exc:
        print(f"Mock CRM sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
