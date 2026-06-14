#!/usr/bin/env python3
"""Convert a sanitized CRM Excel export into website-ready data.

The script deliberately uses only the Python standard library so the demo can
run anywhere GitHub Actions or a locked-down laptop has Python 3 available.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import posixpath
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


REQUIRED_COLUMNS = [
    "Opportunity ID",
    "Account",
    "Segment",
    "Region",
    "Owner",
    "Stage",
    "Forecast Category",
    "Amount",
    "Probability",
    "Expected Close Date",
    "Last Updated",
]

PIPELINE_STAGES = [
    "Prospecting",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

STAGE_ORDER = {stage: index for index, stage in enumerate(PIPELINE_STAGES)}
OPEN_STAGES = {"Prospecting", "Qualification", "Proposal", "Negotiation"}
STALE_DAYS = 21
CLOSED_WON_GOAL = 2_000_000


@dataclass
class ParsedWorkbook:
    rows: list[dict[str, str]]
    sheet_name: str
    columns: list[str]


def cell_column(cell_ref: str) -> int:
    letters = "".join(char for char in cell_ref if char.isalpha()).upper()
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def text_from_node(node: ET.Element | None, namespaces: dict[str, str]) -> str:
    if node is None:
        return ""
    parts = [text or "" for text in node.itertext()]
    return "".join(parts)


def read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        xml = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    root = ET.fromstring(xml)
    namespaces = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    strings: list[str] = []
    for item in root.findall("main:si", namespaces):
        strings.append(text_from_node(item, namespaces))
    return strings


def workbook_sheet_path(archive: zipfile.ZipFile, sheet_name: str | None) -> tuple[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    workbook_ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rels_ns = {"pkg": "http://schemas.openxmlformats.org/package/2006/relationships"}
    rels = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels_root.findall("pkg:Relationship", rels_ns)
    }

    sheets = workbook.findall("main:sheets/main:sheet", workbook_ns)
    if not sheets:
        raise ValueError("Workbook does not contain any sheets.")

    selected = None
    if sheet_name:
        for sheet in sheets:
            if sheet.attrib.get("name") == sheet_name:
                selected = sheet
                break
        if selected is None:
            available = ", ".join(sheet.attrib.get("name", "") for sheet in sheets)
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {available}")
    else:
        selected = sheets[0]

    rid = selected.attrib[f"{{{workbook_ns['rel']}}}id"]
    target = rels[rid]
    if target.startswith("/"):
        path = target.lstrip("/")
    else:
        path = posixpath.normpath(posixpath.join("xl", target))
    return path, selected.attrib.get("name", sheet_name or "Sheet1")


def read_xlsx_table(path: Path, sheet_name: str | None = "CRM_Export") -> ParsedWorkbook:
    if not path.exists():
        raise FileNotFoundError(f"Export file not found: {path}")

    with zipfile.ZipFile(path) as archive:
        shared_strings = read_shared_strings(archive)
        sheet_path, resolved_sheet_name = workbook_sheet_path(archive, sheet_name)
        sheet_root = ET.fromstring(archive.read(sheet_path))

    namespaces = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    records: list[list[str]] = []
    for row in sheet_root.findall("main:sheetData/main:row", namespaces):
        values: list[str] = []
        for cell in row.findall("main:c", namespaces):
            column_index = cell_column(cell.attrib.get("r", "A1"))
            while len(values) <= column_index:
                values.append("")
            cell_type = cell.attrib.get("t")
            value_node = cell.find("main:v", namespaces)
            if cell_type == "s":
                raw_value = value_node.text if value_node is not None and value_node.text else "0"
                value = shared_strings[int(raw_value)] if shared_strings else ""
            elif cell_type == "inlineStr":
                value = text_from_node(cell.find("main:is", namespaces), namespaces)
            else:
                value = value_node.text if value_node is not None and value_node.text else ""
            values[column_index] = value.strip() if isinstance(value, str) else str(value)
        if any(value != "" for value in values):
            records.append(values)

    if not records:
        raise ValueError(f"Sheet '{resolved_sheet_name}' did not contain a table.")

    headers = [header.strip() for header in records[0]]
    rows: list[dict[str, str]] = []
    for source_row in records[1:]:
        padded = source_row + [""] * max(0, len(headers) - len(source_row))
        row = {headers[index]: padded[index].strip() for index in range(len(headers))}
        if any(row.values()):
            rows.append(row)

    return ParsedWorkbook(rows=rows, sheet_name=resolved_sheet_name, columns=headers)


def parse_currency(value: str, field: str, row_number: int) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    if cleaned == "":
        raise ValueError(f"Row {row_number}: missing {field}.")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: {field} must be numeric, got '{value}'.") from exc


def parse_probability(value: str, row_number: int) -> float:
    cleaned = value.replace("%", "").strip()
    if cleaned == "":
        raise ValueError(f"Row {row_number}: missing Probability.")
    try:
        probability = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: Probability must be numeric, got '{value}'.") from exc
    if probability > 1:
        probability = probability / 100
    if probability < 0 or probability > 1:
        raise ValueError(f"Row {row_number}: Probability must be between 0 and 1.")
    return probability


def parse_iso_date(value: str, field: str, row_number: int) -> date:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: {field} must use YYYY-MM-DD, got '{value}'.") from exc


def normalized_record(raw: dict[str, str], row_number: int) -> dict[str, Any]:
    missing_values = [column for column in REQUIRED_COLUMNS if not raw.get(column, "").strip()]
    if missing_values:
        raise ValueError(f"Row {row_number}: missing values for {', '.join(missing_values)}.")

    stage = raw["Stage"].strip()
    if stage not in STAGE_ORDER:
        raise ValueError(f"Row {row_number}: unknown Stage '{stage}'.")

    amount = parse_currency(raw["Amount"], "Amount", row_number)
    probability = parse_probability(raw["Probability"], row_number)
    expected_close = parse_iso_date(raw["Expected Close Date"], "Expected Close Date", row_number)
    last_updated = parse_iso_date(raw["Last Updated"], "Last Updated", row_number)

    record = {
        "opportunityId": raw["Opportunity ID"].strip(),
        "account": raw["Account"].strip(),
        "segment": raw["Segment"].strip(),
        "region": raw["Region"].strip(),
        "owner": raw["Owner"].strip(),
        "stage": stage,
        "forecastCategory": raw["Forecast Category"].strip(),
        "amount": round(amount, 2),
        "probability": probability,
        "weightedAmount": round(amount * probability, 2),
        "expectedCloseDate": expected_close.isoformat(),
        "lastUpdated": last_updated.isoformat(),
    }
    return record


def group_records(records: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "amount": 0.0, "weightedAmount": 0.0})
    for record in records:
        key = record[field]
        grouped[key]["count"] += 1
        grouped[key]["amount"] += record["amount"]
        grouped[key]["weightedAmount"] += record["weightedAmount"]

    summaries = [
        {
            "name": key,
            "count": value["count"],
            "amount": round(value["amount"], 2),
            "weightedAmount": round(value["weightedAmount"], 2),
        }
        for key, value in grouped.items()
    ]

    if field == "stage":
        return sorted(summaries, key=lambda item: STAGE_ORDER.get(item["name"], 99))
    return sorted(summaries, key=lambda item: item["amount"], reverse=True)


def top_item(summary: list[dict[str, Any]]) -> dict[str, Any]:
    if not summary:
        return {"name": "N/A", "amount": 0, "count": 0, "weightedAmount": 0}
    return max(summary, key=lambda item: item["amount"])


def build_site_payload(records: list[dict[str, Any]], source_path: Path, source_hash: str, sheet_name: str) -> dict[str, Any]:
    if not records:
        raise ValueError("No records found after validation.")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    data_as_of = max(parse_iso_date(record["lastUpdated"], "Last Updated", index + 2) for index, record in enumerate(records))
    pipeline_value = sum(record["amount"] for record in records)
    weighted_pipeline = sum(record["weightedAmount"] for record in records)
    open_pipeline = sum(record["amount"] for record in records if record["stage"] in OPEN_STAGES)
    closed_won = sum(record["amount"] for record in records if record["stage"] == "Closed Won")
    closed_lost = sum(record["amount"] for record in records if record["stage"] == "Closed Lost")
    avg_probability = sum(record["probability"] for record in records) / len(records)

    stale_before = data_as_of.toordinal() - STALE_DAYS
    stale_records = [
        record
        for record in records
        if record["stage"] in OPEN_STAGES
        and parse_iso_date(record["lastUpdated"], "Last Updated", 0).toordinal() <= stale_before
    ]

    by_stage = group_records(records, "stage")
    by_region = group_records(records, "region")
    by_owner = group_records(records, "owner")
    by_segment = group_records(records, "segment")
    top_region = top_item(by_region)
    top_segment = top_item(by_segment)
    top_stage = top_item(by_stage)

    return {
        "metadata": {
            "demoName": "Sanitized CRM to Web Flow",
            "sourceFile": str(source_path),
            "sourceSheet": sheet_name,
            "sourceSha256": source_hash,
            "generatedAt": generated_at,
            "dataAsOf": data_as_of.isoformat(),
            "staleThresholdDays": STALE_DAYS,
            "guardrail": "This file contains validated CRM-derived metrics only; AI-authored text lives in ai-summary.json.",
        },
        "metrics": {
            "totalRecords": len(records),
            "pipelineValue": round(pipeline_value, 2),
            "weightedPipeline": round(weighted_pipeline, 2),
            "openPipeline": round(open_pipeline, 2),
            "closedWon": round(closed_won, 2),
            "closedWonGoal": CLOSED_WON_GOAL,
            "closedWonDelta": round(closed_won - CLOSED_WON_GOAL, 2),
            "closedWonAttainment": round(closed_won / CLOSED_WON_GOAL, 4),
            "closedLost": round(closed_lost, 2),
            "averageProbability": round(avg_probability, 4),
            "staleOpenCount": len(stale_records),
            "topRegion": top_region["name"],
            "topSegment": top_segment["name"],
            "largestStage": top_stage["name"],
        },
        "summaries": {
            "byStage": by_stage,
            "byRegion": by_region,
            "byOwner": by_owner,
            "bySegment": by_segment,
        },
        "opportunities": sorted(
            records,
            key=lambda item: (STAGE_ORDER.get(item["stage"], 99), -item["amount"], item["account"]),
        ),
    }


def audit_payload(payload: dict[str, Any], source_columns: list[str]) -> dict[str, Any]:
    return {
        "run": {
            "generatedAt": payload["metadata"]["generatedAt"],
            "sourceFile": payload["metadata"]["sourceFile"],
            "sourceSheet": payload["metadata"]["sourceSheet"],
            "sourceSha256": payload["metadata"]["sourceSha256"],
        },
        "checks": [
            {
                "name": "Required columns present",
                "status": "pass",
                "detail": f"{len(REQUIRED_COLUMNS)} required columns found.",
                "evidence": REQUIRED_COLUMNS,
            },
            {
                "name": "Rows validated",
                "status": "pass",
                "detail": f"{payload['metrics']['totalRecords']} opportunity rows parsed from export.",
                "evidence": {"rowCount": payload["metrics"]["totalRecords"], "columns": source_columns},
            },
            {
                "name": "Website data generated",
                "status": "pass",
                "detail": "Pipeline JSON and audit JSON were generated from the same source hash.",
                "evidence": {
                    "pipelineJson": "site/data/pipeline.json",
                    "auditJson": "site/data/audit-log.json",
                },
            },
            {
                "name": "AI handoff ready",
                "status": "pass",
                "detail": "The AI copy step receives pipeline JSON after validation and is expected to update ai-summary.json only.",
                "evidence": {
                    "aiInput": "site/data/pipeline.json",
                    "aiOutput": "site/data/ai-summary.json",
                    "numberEditing": "disallowed",
                },
            },
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def payloads_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_copy = copy.deepcopy(left)
    right_copy = copy.deepcopy(right)
    for payload in (left_copy, right_copy):
        payload.get("metadata", {}).pop("generatedAt", None)
        if "run" in payload:
            payload["run"].pop("generatedAt", None)
    return left_copy == right_copy


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate website data from a sanitized CRM Excel export.")
    parser.add_argument("source", nargs="?", default="data/crm-export-june-2026.xlsx", help="Path to .xlsx CRM export.")
    parser.add_argument("--sheet", default="CRM_Export", help="Worksheet name containing the raw export table.")
    parser.add_argument("--out-dir", default="site/data", help="Directory for generated website JSON files.")
    parser.add_argument("--check", action="store_true", help="Validate without modifying files; fail if checked-in JSON is stale.")
    args = parser.parse_args()

    source_path = Path(args.source)
    out_dir = Path(args.out_dir)

    try:
        parsed = read_xlsx_table(source_path, args.sheet)
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in parsed.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        records = [normalized_record(row, index + 2) for index, row in enumerate(parsed.rows)]
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        pipeline = build_site_payload(records, source_path, source_hash, parsed.sheet_name)
        audit = audit_payload(pipeline, parsed.columns)

        pipeline_path = out_dir / "pipeline.json"
        audit_path = out_dir / "audit-log.json"
        if args.check:
            if not pipeline_path.exists() or not audit_path.exists():
                raise ValueError("Generated JSON files are missing. Run `npm run generate` first.")
            existing_pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
            existing_audit = json.loads(audit_path.read_text(encoding="utf-8"))
            if not payloads_equal(pipeline, existing_pipeline) or not payloads_equal(audit, existing_audit):
                raise ValueError("Generated JSON is stale. Run `npm run generate` and commit the result.")
        else:
            write_json(pipeline_path, pipeline)
            write_json(audit_path, audit)

        action = "Validated" if args.check else "Generated"
        print(
            f"{action} {len(records)} records from {source_path} "
            f"({pipeline['metrics']['pipelineValue']:,.0f} pipeline value)."
        )
        return 0
    except Exception as exc:
        print(f"CRM export ingestion failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
