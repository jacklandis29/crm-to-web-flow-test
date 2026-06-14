# Sanitized CRM to Web Flow

This repo is a safe, professional demo of the workflow you described:

1. A mock Salesforce-style CRM changes.
2. Claude/tools can query that CRM through a local MCP server.
3. Deterministic code validates the CRM data and writes website-safe JSON.
4. Claude Code reads the validated metrics and writes website copy.
5. The Claude Routine commits generated files to `main`.
6. GitHub Pages deploys the live static website.

All data is synthetic.

## Quick Demo

```bash
npm run generate
npm run validate
npm run serve
```

Then open [http://localhost:4173](http://localhost:4173).

## Professional Mock CRM Demo

Run this to change the mock CRM and trigger the Claude Routine path:

```bash
npm run crm:win
```

This updates `OPP-2026-002` to `Closed Won`, publishes a `crm-refresh-*` release, and wakes the Claude Routine.

The local-only version is:

```bash
npm run crm:win-local
```

The AI copy changes only after the validated CRM snapshot changes.

## What To Point Out

- `data/mock-crm.json` is the sanitized CRM source of truth.
- `scripts/mock_crm_mcp_server.py` exposes the mock CRM through MCP.
- `scripts/sync_from_mock_crm.py` validates CRM data and generates the website data.
- `site/data/pipeline.json` is the CRM-derived source for dashboard numbers.
- `site/data/ai-summary.json` is the AI-authored website copy derived from the pipeline JSON.
- `site/data/audit-log.json` shows the guardrails that passed before publishing.
- `docs/mock-crm-mcp.md` explains the MCP architecture.
- `docs/claude-routine-instructions.md` contains the Claude Routine prompt.

## How It Maps To The Real Flow

| Real workflow | Sanitized demo |
| --- | --- |
| Internal Salesforce-powered CRM | Mock CRM store plus MCP server |
| Power BI dataset refresh | Generated JSON summaries and the embedded analytics panel |
| AI/code agent updates website | Claude Routine updates `ai-summary.json` |
| Anti-hallucination guardrail | AI reads only validated `pipeline.json` source keys |
| Live website | GitHub Pages deploys the static `site/` folder |

## Demo Talk Track

The important claim is not that an AI can invent dashboard numbers. The CRM owns the numbers. The deterministic sync owns validation. The AI owns only the summary language after validation.

## Legacy Excel Demo

The original Excel-based path still exists:

```bash
npm run watch:excel
npm run watch:routine
```

But the recommended version for interviews is the mock CRM/MCP path above.
