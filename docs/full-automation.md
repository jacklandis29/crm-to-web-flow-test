# Fully Automated Save-To-Site Flow

GitHub cannot see a file saved on your laptop until something sends it there. For the GitHub Actions route, that bridge is:

```bash
npm run watch:excel
```

For the Claude Routine route, use:

```bash
npm run watch:routine
```

Keep one watcher running while you edit the Excel export.

## End-To-End Flow: GitHub Actions Route

1. You save `data/crm-export-june-2026.xlsx`.
2. `scripts/watch_excel_and_push.py` detects the changed file.
3. The watcher waits until Excel is done writing.
4. The watcher validates the workbook can be parsed.
5. The watcher commits and pushes only the workbook to `main`.
6. GitHub Actions sees the `data/**/*.xlsx` push.
7. `.github/workflows/crm-export-to-main.yml` regenerates `site/data/pipeline.json` and `site/data/audit-log.json`.
8. Claude Code Action, if configured, updates `site/data/ai-summary.json`.
9. The workflow validates the AI summary source keys.
10. The workflow commits generated website JSON to `main`.
11. The workflow deploys GitHub Pages.

## End-To-End Flow: Claude Routine Route

1. You save `data/crm-export-june-2026.xlsx`.
2. `scripts/watch_excel_and_push.py` detects the changed file.
3. The watcher validates, commits, and pushes only the workbook to `main`.
4. The watcher publishes a GitHub release with a `crm-refresh-*` tag.
5. The Claude Routine fires from its **Release published** trigger.
6. The Routine follows `CLAUDE.md` and `docs/claude-routine-instructions.md`.
7. The Routine updates only generated website JSON and pushes to `main`.
8. GitHub Pages deploys after the generated site files change.

## One-Time GitHub Settings

In the repo:

1. **Settings -> Pages**
   - Source: **GitHub Actions**
2. **Settings -> Actions -> General**
   - Workflow permissions: **Read and write permissions**
3. **Settings -> Secrets and variables -> Actions**
   - Add `ANTHROPIC_API_KEY` for Claude Code Action.

Without `ANTHROPIC_API_KEY`, the workflow uses the deterministic fallback summary generator so the automation still runs.

## Daily Demo Command

Run this once before the demo if you want GitHub Actions to run the AI step:

```bash
npm run watch:excel
```

Run this instead if you want the Claude Routine to run the AI step:

```bash
npm run watch:routine
```

Then open the Excel file, edit it, save it, and watch the matching cloud automation update Pages.

## MCP / Fake CRM Note

An MCP server is a good way for Claude to query a CRM-like data source, but it does not replace the trigger. Something still has to wake the routine: a release event, issue event, PR event, manual run, schedule, or webhook-like integration.

For anti-hallucination, keep a deterministic data boundary:

1. Pull data from CRM or fake CRM.
2. Validate it into a snapshot such as `site/data/pipeline.json`.
3. Let AI read that snapshot and write copy only.

That is safer than letting the AI query live data and publish prose without a frozen, auditable source.
