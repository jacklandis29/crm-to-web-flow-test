# Fully Automated Save-To-Site Flow

GitHub cannot see a file saved on your laptop until something sends it there. For this demo, that bridge is:

```bash
npm run watch:excel
```

Keep that watcher running while you edit the Excel export.

## End-To-End Flow

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

Run this once before the demo:

```bash
npm run watch:excel
```

Then open the Excel file, edit it, save it, and watch GitHub Actions/Pages update.
