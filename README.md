# CRM → Validated Numbers → AI Copy

A small, sanitized demo of a real pattern: a CRM drives the numbers on an
internal website, and an AI writes the *story* around those numbers — **without
ever being allowed to touch the numbers themselves.**

The point isn't "AI can fill in a dashboard." It's the opposite:

> The CRM owns the numbers. Deterministic code validates them. The AI owns only
> the words — and every claim it writes is tagged with the exact validated field
> it came from, so it physically cannot invent a figure.

All data is synthetic.

## The flow

```
Mock CRM (data/mock-crm.json)
  → MCP server exposes it as tools/resources   (scripts/mock_crm_mcp_server.py)
  → deterministic sync validates + freezes it   (scripts/sync_from_mock_crm.py)
     → site/data/pipeline.json   (the only source of published numbers)
     → site/data/audit-log.json  (the guardrail checks that passed)
  → AI authors copy from pipeline.json          (site/data/ai-summary.json)
     → validator rejects any claim whose source key doesn't resolve
  → GitHub Pages serves the static site/
```

## Quick start (local)

```bash
npm run generate   # validate the CRM snapshot + author the AI copy
npm run validate   # prove the snapshot and copy are in sync
npm run serve      # open http://localhost:4173
```

## The demo (the one moment that sells it)

The site starts **behind goal**. One command changes the CRM, regenerates the
validated snapshot, re-authors the copy, and re-runs the guardrail — all locally,
no network:

```bash
npm run demo:win     # CivicGrid Energy closes → closed-won jumps to $3.0M (150% of goal)
```

Refresh the page: the number flips, the progress bar goes green, and the AI copy
rewrites itself to explain *why* — naming the deal that did it, each sentence
tagged with the `pipeline.json` field behind it.

Reset to the starting state to record another take:

```bash
npm run demo:reset
```

## What to point out on screen

- `data/mock-crm.json` — the CRM, the single source of truth for numbers.
- `npm run crm:mcp` — the same CRM exposed over MCP (`crm_get_revision`,
  `crm_list_opportunities`, `crm_get_pipeline_snapshot`, `crm_get_change_events`).
- `site/data/pipeline.json` — validated numbers. The website reads only this.
- `site/data/ai-summary.json` — AI copy, every claim carrying source keys.
- `site/data/audit-log.json` — the checks that ran before anything published.
- The source-key chips under each sentence on the page — that's the guardrail,
  visible.

## How it maps to production

| This demo | Real system |
| --- | --- |
| `data/mock-crm.json` + MCP server | Salesforce / HubSpot via API or MCP |
| `sync_from_mock_crm.py` | Scheduled ETL into a validated dataset |
| `npm run demo:win` (local) | A CRM webhook / nightly job |
| `simulate_ai_summary.py` | A cloud **Claude Routine** authoring the copy |
| `validate_ai_summary.py` | The same guardrail, in CI |
| GitHub Pages | Your internal dashboard host |

The local `demo:*` commands keep the live demo deterministic. The cloud version
is the same contract, triggered by a GitHub Release that wakes a Claude Routine —
see [docs/full-automation.md](docs/full-automation.md) and
[docs/claude-routine-instructions.md](docs/claude-routine-instructions.md). The
`cloud:win` / `cloud:reset` scripts drive that path.

## Docs

- [docs/demo-script.md](docs/demo-script.md) — the talk track for recording.
- [docs/mock-crm-mcp.md](docs/mock-crm-mcp.md) — the MCP architecture.
- [docs/architecture.md](docs/architecture.md) — the full diagram + guardrails.
