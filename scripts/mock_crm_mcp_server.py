#!/usr/bin/env python3
"""Minimal MCP server that exposes a sanitized mock CRM over stdio JSON-RPC."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from mock_crm_store import (
    DEFAULT_CRM_PATH,
    build_pipeline,
    database_hash,
    load_database,
    update_opportunity,
    validated_records,
)


SERVER_INFO = {"name": "mock-crm", "version": "1.0.0"}
PROTOCOL_VERSION = "2024-11-05"


def text_content(payload: Any) -> list[dict[str, str]]:
    return [{"type": "text", "text": json.dumps(payload, indent=2)}]


def tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "crm_get_revision",
            "description": "Return the current mock CRM revision, update time, and source hash.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "crm_list_opportunities",
            "description": "Return validated opportunity records from the mock CRM.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "crm_get_pipeline_snapshot",
            "description": "Return the validated public pipeline snapshot generated from CRM records.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "crm_get_change_events",
            "description": "Return recent mock CRM change events.",
            "inputSchema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 20}},
                "additionalProperties": False,
            },
        },
        {
            "name": "crm_update_opportunity",
            "description": "Update one mock CRM opportunity. Use only for demos that intentionally mutate CRM data.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "opportunityId": {"type": "string"},
                    "amount": {"type": "number"},
                    "stage": {"type": "string"},
                    "probability": {"type": "number", "minimum": 0, "maximum": 1},
                    "actor": {"type": "string"},
                },
                "required": ["opportunityId"],
                "additionalProperties": False,
            },
        },
    ]


def resource_list() -> list[dict[str, Any]]:
    return [
        {
            "uri": "mock-crm://revision",
            "name": "Mock CRM Revision",
            "mimeType": "application/json",
            "description": "Current CRM revision metadata and source hash.",
        },
        {
            "uri": "mock-crm://opportunities",
            "name": "Mock CRM Opportunities",
            "mimeType": "application/json",
            "description": "Validated opportunity rows from the mock CRM.",
        },
        {
            "uri": "mock-crm://pipeline-snapshot",
            "name": "Mock CRM Pipeline Snapshot",
            "mimeType": "application/json",
            "description": "Public website snapshot derived from the mock CRM.",
        },
    ]


def revision_payload() -> dict[str, Any]:
    database = load_database(DEFAULT_CRM_PATH)
    metadata = database.get("metadata", {})
    return {
        "system": metadata.get("system", "MockCRM"),
        "revision": metadata.get("revision"),
        "updatedAt": metadata.get("updatedAt"),
        "changedBy": metadata.get("changedBy"),
        "sourceSha256": database_hash(database),
        "recordCount": len(database.get("opportunities", [])),
    }


def call_tool(name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    args = arguments or {}
    database = load_database(DEFAULT_CRM_PATH)

    if name == "crm_get_revision":
        return {"content": text_content(revision_payload())}
    if name == "crm_list_opportunities":
        return {"content": text_content({"opportunities": validated_records(database)})}
    if name == "crm_get_pipeline_snapshot":
        return {"content": text_content(build_pipeline(database, DEFAULT_CRM_PATH))}
    if name == "crm_get_change_events":
        limit = int(args.get("limit", 10))
        return {"content": text_content({"events": database.get("events", [])[-limit:]})}
    if name == "crm_update_opportunity":
        event = update_opportunity(
            args["opportunityId"],
            amount=args.get("amount"),
            stage=args.get("stage"),
            probability=args.get("probability"),
            actor=args.get("actor", "mcp.client"),
        )
        return {"content": text_content({"event": event, "revision": revision_payload()})}
    raise ValueError(f"Unknown tool: {name}")


def read_resource(uri: str) -> dict[str, Any]:
    database = load_database(DEFAULT_CRM_PATH)
    if uri == "mock-crm://revision":
        payload = revision_payload()
    elif uri == "mock-crm://opportunities":
        payload = {"opportunities": validated_records(database)}
    elif uri == "mock-crm://pipeline-snapshot":
        payload = build_pipeline(database, DEFAULT_CRM_PATH)
    else:
        raise ValueError(f"Unknown resource: {uri}")
    return {
        "contents": [
            {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(payload, indent=2),
            }
        ]
    }


def handle(method: str, params: dict[str, Any] | None) -> dict[str, Any] | None:
    params = params or {}
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}, "resources": {}},
            "serverInfo": SERVER_INFO,
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"tools": tool_definitions()}
    if method == "tools/call":
        return call_tool(params["name"], params.get("arguments"))
    if method == "resources/list":
        return {"resources": resource_list()}
    if method == "resources/read":
        return read_resource(params["uri"])
    raise ValueError(f"Unsupported method: {method}")


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        request_id = request.get("id")
        try:
            result = handle(request["method"], request.get("params"))
            if request_id is not None and result is not None:
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
        except Exception as exc:
            if request_id is not None:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
