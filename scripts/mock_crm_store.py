#!/usr/bin/env python3
"""Shared helpers for the mock CRM data store and MCP server."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingest_crm_export import (
    PIPELINE_STAGES,
    audit_payload,
    build_site_payload,
    write_json,
)


CRM_COLUMNS = [
    "opportunityId",
    "account",
    "segment",
    "region",
    "owner",
    "stage",
    "forecastCategory",
    "amount",
    "probability",
    "expectedCloseDate",
    "lastUpdated",
]

FORECAST_BY_STAGE = {
    "Prospecting": "Pipeline",
    "Qualification": "Pipeline",
    "Proposal": "Best Case",
    "Negotiation": "Commit",
    "Closed Won": "Closed",
    "Closed Lost": "Omitted",
}

DEFAULT_CRM_PATH = Path("data/mock-crm.json")
DEFAULT_SITE_DATA_DIR = Path("site/data")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_database(path: Path = DEFAULT_CRM_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_database(database: dict[str, Any], path: Path = DEFAULT_CRM_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(database, indent=2) + "\n", encoding="utf-8")


def database_hash(database: dict[str, Any]) -> str:
    encoded = json.dumps(database, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_opportunity(record: dict[str, Any], row_number: int) -> dict[str, Any]:
    missing = [field for field in CRM_COLUMNS if field not in record or record[field] in ("", None)]
    if missing:
        raise ValueError(f"CRM row {row_number}: missing {', '.join(missing)}.")
    if record["stage"] not in PIPELINE_STAGES:
        raise ValueError(f"CRM row {row_number}: unknown stage {record['stage']}.")

    amount = float(record["amount"])
    probability = float(record["probability"])
    if amount < 0:
        raise ValueError(f"CRM row {row_number}: amount must be non-negative.")
    if probability < 0 or probability > 1:
        raise ValueError(f"CRM row {row_number}: probability must be between 0 and 1.")

    return {
        "opportunityId": str(record["opportunityId"]),
        "account": str(record["account"]),
        "segment": str(record["segment"]),
        "region": str(record["region"]),
        "owner": str(record["owner"]),
        "stage": str(record["stage"]),
        "forecastCategory": str(record["forecastCategory"]),
        "amount": round(amount, 2),
        "probability": probability,
        "weightedAmount": round(amount * probability, 2),
        "expectedCloseDate": str(record["expectedCloseDate"]),
        "lastUpdated": str(record["lastUpdated"]),
    }


def validated_records(database: dict[str, Any]) -> list[dict[str, Any]]:
    records = database.get("opportunities")
    if not isinstance(records, list) or not records:
        raise ValueError("Mock CRM database must include at least one opportunity.")
    return [validate_opportunity(record, index + 1) for index, record in enumerate(records)]


def build_pipeline(database: dict[str, Any], source_path: Path = DEFAULT_CRM_PATH) -> dict[str, Any]:
    records = validated_records(database)
    payload = build_site_payload(records, source_path, database_hash(database), "mock_crm.opportunities")
    payload["metadata"]["sourceSystem"] = database.get("metadata", {}).get("system", "MockCRM")
    payload["metadata"]["sourceRevision"] = database.get("metadata", {}).get("revision")
    payload["metadata"]["sourceUpdatedAt"] = database.get("metadata", {}).get("updatedAt")
    payload["metadata"]["guardrail"] = (
        "This file is a validated public snapshot of mock CRM data; AI-authored text lives in ai-summary.json."
    )
    return payload


def build_audit(pipeline: dict[str, Any], database: dict[str, Any]) -> dict[str, Any]:
    audit = audit_payload(pipeline, CRM_COLUMNS)
    audit["run"]["sourceSystem"] = pipeline["metadata"].get("sourceSystem")
    audit["run"]["sourceRevision"] = pipeline["metadata"].get("sourceRevision")
    audit["checks"].append(
        {
            "name": "Mock CRM revision captured",
            "status": "pass",
            "detail": "The public website snapshot includes the CRM revision and source hash.",
            "evidence": {
                "revision": database.get("metadata", {}).get("revision"),
                "sourceSha256": pipeline["metadata"]["sourceSha256"],
            },
        }
    )
    return audit


def write_site_snapshot(database: dict[str, Any], out_dir: Path = DEFAULT_SITE_DATA_DIR) -> dict[str, Any]:
    pipeline = build_pipeline(database)
    audit = build_audit(pipeline, database)
    write_json(out_dir / "pipeline.json", pipeline)
    write_json(out_dir / "audit-log.json", audit)
    return pipeline


def stable_payload(payload: dict[str, Any]) -> dict[str, Any]:
    stable = copy.deepcopy(payload)
    stable.get("metadata", {}).pop("generatedAt", None)
    if "run" in stable:
        stable["run"].pop("generatedAt", None)
    return stable


def update_opportunity(
    opportunity_id: str,
    *,
    amount: float | None = None,
    stage: str | None = None,
    probability: float | None = None,
    actor: str = "mock.crm.user",
    path: Path = DEFAULT_CRM_PATH,
) -> dict[str, Any]:
    database = load_database(path)
    match = None
    for record in database["opportunities"]:
        if record["opportunityId"] == opportunity_id:
            match = record
            break
    if match is None:
        raise ValueError(f"Opportunity not found: {opportunity_id}")

    changes: dict[str, Any] = {}
    if amount is not None and float(match["amount"]) != float(amount):
        changes["amount"] = {"from": match["amount"], "to": amount}
        match["amount"] = amount
    if stage is not None and match["stage"] != stage:
        if stage not in PIPELINE_STAGES:
            raise ValueError(f"Unknown stage: {stage}")
        changes["stage"] = {"from": match["stage"], "to": stage}
        match["stage"] = stage
    if stage is not None:
        forecast_category = FORECAST_BY_STAGE.get(stage, match["forecastCategory"])
        if match["forecastCategory"] != forecast_category:
            changes["forecastCategory"] = {"from": match["forecastCategory"], "to": forecast_category}
            match["forecastCategory"] = forecast_category
    if probability is not None and float(match["probability"]) != float(probability):
        if probability < 0 or probability > 1:
            raise ValueError("Probability must be between 0 and 1.")
        changes["probability"] = {"from": match["probability"], "to": probability}
        match["probability"] = probability

    if not changes:
        raise ValueError(f"No CRM changes needed for {opportunity_id}.")

    now = utc_now()
    match["lastUpdated"] = now[:10]
    metadata = database.setdefault("metadata", {})
    metadata["revision"] = int(metadata.get("revision", 0)) + 1
    metadata["updatedAt"] = now
    metadata["changedBy"] = actor
    event = {
        "id": f"evt-{now.replace(':', '').replace('-', '').replace('T', '-')}",
        "type": "opportunity.updated",
        "opportunityId": opportunity_id,
        "createdAt": now,
        "actor": actor,
        "changes": changes,
    }
    database.setdefault("events", []).append(event)
    validated_records(database)
    save_database(database, path)
    return event
