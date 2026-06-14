# Mock CRM MCP Architecture

This demo treats the CRM as a service instead of treating Excel as the primary source.

## Components

- `data/mock-crm.json`: synthetic CRM database.
- `scripts/mock_crm_mcp_server.py`: local MCP server exposing CRM tools and resources.
- `scripts/sync_from_mock_crm.py`: deterministic CRM-to-public-snapshot sync.
- `site/data/pipeline.json`: validated website facts generated from the CRM.
- `site/data/ai-summary.json`: AI-authored copy generated from validated facts.
- `.github/workflows/mock-crm-to-main.yml`: cloud refresh workflow for mock CRM changes.

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

Use one of these trigger paths:

- **GitHub Actions path:** change `data/mock-crm.json` and push it. `.github/workflows/mock-crm-to-main.yml` runs automatically.
- **Claude Routine path:** publish a release after a CRM change. The Routine wakes from `Release published` and queries/uses the CRM snapshot.

For a one-command demo that changes the mock CRM and triggers GitHub Actions:

```bash
npm run crm:win-actions
```

For a one-command demo that changes the mock CRM and triggers the Claude Routine through a release:

```bash
npm run crm:win-routine
```

Both commands update `OPP-2026-002` to `Closed Won`, which moves closed-won sales further ahead of goal.
