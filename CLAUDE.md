# Claude Instructions

This repo is a sanitized CRM-to-website demo with a mock CRM MCP server.

## Core Contract

- `data/mock-crm.json` is the primary mock CRM source of truth.
- The mock CRM can be queried through `scripts/mock_crm_mcp_server.py`.
- `site/data/pipeline.json` and `site/data/audit-log.json` are generated from the CRM snapshot.
- `site/data/ai-summary.json` is AI-authored copy generated from `site/data/pipeline.json`.
- Do not manually invent or alter numeric facts.
- Do not edit CRM source data unless the user explicitly asks.
- Do not edit `site/data/pipeline.json` or `site/data/audit-log.json` by hand.
- If writing website copy, update `site/data/ai-summary.json` only.

## Standard Refresh

Run:

```bash
npm run crm:sync
npm run ai:local
npm run validate
```

If you are the AI authoring step, you may replace `npm run ai:local` by writing `site/data/ai-summary.json` yourself, but the final validation must pass:

```bash
npm run validate
```

## AI Summary Requirements

`site/data/ai-summary.json` must include:

- `metadata.generatedBy`
- `metadata.sourceFile = "site/data/pipeline.json"`
- `metadata.sourceSha256` copied from `pipeline.metadata.sourceSha256`
- `metadata.dataAsOf` copied from `pipeline.metadata.dataAsOf`
- `hero.headline`, `hero.body`, `hero.sources`
- `cards` with at least 3 cards
- Source keys for every substantive claim

The lead copy should say whether closed-won sales are ahead of or behind goal using:

- `metrics.closedWon`
- `metrics.closedWonGoal`
- `metrics.closedWonDelta`
- `metrics.closedWonAttainment`

## Change Narrative

When `pipeline.changeReport.hasChanges` is true, `ai-summary.json` should include a
top-level `change` object that leads with what moved this refresh:

- `headline`, `body` — what changed (named opportunity, from/to, metric ripple), with
  `sources` keys for every figure.
- `rationale` — **why it matters**, drawn from `context/business-context.md` (the org and
  account knowledge). This is qualitative interpretation: it carries no numbers and needs no
  source keys. The numbers stay in `body`; the meaning goes in `rationale`.

Omit `change` when there are no changes.

## Commit Scope

For an automated refresh commit, include only:

- `site/data/pipeline.json`
- `site/data/audit-log.json`
- `site/data/ai-summary.json`

Use a commit message like:

```text
Refresh website data and AI copy from mock CRM
```
