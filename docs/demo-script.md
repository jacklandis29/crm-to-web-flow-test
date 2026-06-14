# Demo Script

1. Show `data/crm-export-june-2026.xlsx` and explain that it is a synthetic CRM export.
2. Open the website and point out that closed-won revenue is currently behind the `$2,000,000` goal.
3. Change one Closed Won amount or change another opportunity to `Closed Won` so closed-won revenue moves above the goal.
4. Start `npm run watch:excel` for the GitHub Actions path, or `npm run watch:routine` for the Claude Routine path.
5. Save the workbook.
6. Point out that the watcher commits and pushes only the workbook.
7. For the Actions path, open GitHub Actions and show `.github/workflows/crm-export-to-main.yml` running.
8. For the Routine path, show the `crm-refresh-*` release and the Claude Routine run.
9. When it completes, refresh GitHub Pages and point out that the numbers changed first, then the AI copy changed to match.
10. Open `site/data/pipeline.json` and `site/data/ai-summary.json` to show the separation between facts and AI-authored text.

Close with this framing:

> The AI never owns the numbers. The CRM export owns the numbers; the AI owns the summary language after the metrics are validated.
