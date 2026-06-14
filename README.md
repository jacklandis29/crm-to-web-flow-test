# Sanitized CRM to Web Flow

This repo is a safe demo of the workflow you described:

1. A Salesforce-style CRM export lands as an Excel workbook.
2. A validation/generation job reads only the raw export table.
3. The job writes auditable JSON for the website and embedded analytics layer.
4. An AI/code-agent step reads the validated metrics and writes website copy.
5. GitHub Actions or a Claude Routine commits the generated files to `main`.
6. GitHub Pages deploys the live static website.

The included workbook is synthetic and contains no employer, customer, or private data.

## Quick Demo

```bash
npm run generate
npm run validate
npm run serve
```

Then open [http://localhost:4173](http://localhost:4173).

## Fully Automated Demo

Leave this running while you edit the workbook if you want GitHub Actions to run the AI step:

```bash
npm run watch:excel
```

Leave this running instead if you want the Claude Routine to run after a release event:

```bash
npm run watch:routine
```

Then save `data/crm-export-june-2026.xlsx`.

The watcher commits and pushes only the workbook. GitHub Actions then:

1. Regenerates CRM-derived JSON.
2. Runs Claude Code Action if `ANTHROPIC_API_KEY` is configured, or the local fallback if not.
3. Validates the AI summary.
4. Commits generated site data to `main`.
5. Deploys GitHub Pages from the same workflow.

With `watch:routine`, the watcher also publishes a GitHub release. Your Claude Routine is configured for **Release published**, so that release is the event that wakes it.

## What To Point Out

- `data/crm-export-june-2026.xlsx` is the sanitized CRM export.
- `scripts/ingest_crm_export.py` validates the workbook and generates the website data.
- `site/data/pipeline.json` is the CRM-derived source for dashboard numbers.
- `site/data/ai-summary.json` is the AI-authored website copy derived from the pipeline JSON.
- `site/data/audit-log.json` shows the guardrails that passed before publishing.
- `.github/workflows/crm-export-to-main.yml` demonstrates the automated direct-to-main refresh.
- `.github/workflows/deploy-site.yml` deploys the static site after generated files hit `main`.
- `docs/claude-routine-instructions.md` contains the exact Claude Routine prompt.
- `scripts/watch_excel_and_push.py` turns a local Excel save into the GitHub push event.

## How It Maps To The Real Flow

| Real workflow | Sanitized demo |
| --- | --- |
| Internal Salesforce-powered CRM export | Synthetic Excel workbook in `data/` |
| Power BI dataset refresh | Generated JSON summaries and the embedded analytics panel |
| AI/code agent updates website | Claude Code Action or local simulated AI updates `ai-summary.json` |
| Claude routine or GitHub Action updates copy | Routine prompt in `docs/claude-routine-instructions.md`, fallback workflow in `.github/workflows/crm-export-to-main.yml` |
| Human or policy approval | Direct-to-main for the demo, PR review in a stricter production version |

## Refreshing With A New Export

Drop a new `.xlsx` file into `data/`, then run:

```bash
python3 scripts/ingest_crm_export.py data/your-export.xlsx
python3 scripts/simulate_ai_summary.py
```

The workbook must include a `CRM_Export` sheet with these columns:

`Opportunity ID`, `Account`, `Segment`, `Region`, `Owner`, `Stage`, `Forecast Category`, `Amount`, `Probability`, `Expected Close Date`, `Last Updated`.

## Demo Talk Track

The important claim is not that an AI can invent dashboard numbers. It is that the automation can safely move a validated CRM export into a web experience, while the AI is restricted to rewriting copy from already-validated metrics. The audit trail makes that visible.

## GitHub Setup

For a local-only demo, no GitHub setup is required.

For the full cloud demo:

1. Push this folder to a GitHub repo.
2. Enable GitHub Actions.
3. In repo settings, enable GitHub Pages with source set to GitHub Actions.
4. Add an `ANTHROPIC_API_KEY` repository secret if you want the workflow to run Claude Code Action.
5. Run `npm run watch:excel` for the GitHub Actions route, or `npm run watch:routine` for the Claude Routine route.

Without `ANTHROPIC_API_KEY`, the workflow falls back to `scripts/simulate_ai_summary.py` so the demo still updates `main`.
