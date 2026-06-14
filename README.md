# Sanitized CRM to Web Flow

This repo is a safe, professional demo of the workflow you described:

1. A mock Salesforce-style CRM changes.
2. Claude/tools can query that CRM through a local MCP server.
3. Deterministic code validates the CRM data and writes website-safe JSON.
4. An AI/code-agent step reads the validated metrics and writes website copy.
5. GitHub Actions or a Claude Routine commits generated files to `main`.
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

Run this to change the mock CRM and trigger the GitHub Actions path:

```bash
npm run crm:win-actions
```

Run this instead to publish a release that wakes the Claude Routine:

```bash
npm run crm:win-routine
```

Both commands update `OPP-2026-002` to `Closed Won`, pushing closed-won sales further ahead of the goal. The AI copy changes only after the validated CRM snapshot changes.

## What To Point Out

- `data/mock-crm.json` is the sanitized CRM source of truth.
- `scripts/mock_crm_mcp_server.py` exposes the mock CRM through MCP.
- `scripts/sync_from_mock_crm.py` validates CRM data and generates the website data.
- `site/data/pipeline.json` is the CRM-derived source for dashboard numbers.
- `site/data/ai-summary.json` is the AI-authored website copy derived from the pipeline JSON.
- `site/data/audit-log.json` shows the guardrails that passed before publishing.
- `.github/workflows/mock-crm-to-main.yml` is the primary mock CRM cloud refresh.
- `.github/workflows/crm-export-to-main.yml` is the legacy Excel refresh fallback.
- `docs/mock-crm-mcp.md` explains the MCP architecture.

## How It Maps To The Real Flow

| Real workflow | Sanitized demo |
| --- | --- |
| Internal Salesforce-powered CRM | Mock CRM store plus MCP server |
| Power BI dataset refresh | Generated JSON summaries and the embedded analytics panel |
| AI/code agent updates website | Claude Code Action or Claude Routine updates `ai-summary.json` |
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
