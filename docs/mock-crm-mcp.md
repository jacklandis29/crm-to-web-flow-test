# Mock CRM MCP Architecture

This demo treats the CRM as a service instead of treating Excel as the primary source.

## Components

- `data/mock-crm.json`: synthetic CRM database.
- `scripts/mock_crm_mcp_server.py`: local MCP server exposing CRM tools and resources.
- `scripts/sync_from_mock_crm.py`: deterministic CRM-to-public-snapshot sync.
- `site/data/pipeline.json`: validated website facts generated from the CRM.
- `site/data/ai-summary.json`: AI-authored copy generated from validated facts.
- `docs/claude-routine-instructions.md`: the Claude Routine prompt that owns the cloud refresh.

## MCP Tools

The mock CRM MCP server exposes:

- `crm_get_revision`
- `crm_list_opportunities`
- `crm_get_pipeline_snapshot`
- `crm_get_change_events`
- `crm_update_opportunity`

Run it locally:

```bash
npm run crm:mcp
```

The repo also includes `.mcp.json` for local MCP-aware clients.

## Safe Data Flow

```text
Mock CRM
-> MCP/API access
-> deterministic validation
-> site/data/pipeline.json
-> AI copy step reads pipeline.json
-> site/data/ai-summary.json
-> GitHub Pages
```

The website does not publish directly from AI output. It publishes from a validated snapshot. The AI can change wording, but it does not own the numbers.

## Triggering Cloud Automation

MCP is not the trigger by itself. It gives Claude a way to read CRM data when Claude is already running.

For a one-command demo that changes the mock CRM and triggers the Claude Routine through a release:

```bash
npm run crm:win
```

The command updates `OPP-2026-002` to `Closed Won`, pushes the CRM change, and publishes a `crm-refresh-*` release. The release wakes the Claude Routine, which syncs the CRM snapshot, writes copy, validates, and commits generated website data.
