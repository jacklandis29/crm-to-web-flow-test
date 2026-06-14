# Demo Script

1. Show `data/crm-export-june-2026.xlsx` and explain that it is a synthetic CRM export.
2. Open the website and point out that closed-won revenue is currently behind the `$2,000,000` goal.
3. Change one Closed Won amount or change another opportunity to `Closed Won` so closed-won revenue moves above the goal.
4. Save the workbook.
5. Run `npm run refresh:data` to regenerate the CRM-derived metrics.
6. Run `npm run ai:local` to simulate the AI copy-writing step locally.
7. Run `npm run validate` to show both the data and AI summary passed guardrails.
8. Refresh the website and point out that the numbers changed first, then the copy changed to match.
9. Open `.github/workflows/crm-export-to-main.yml` to show where Claude Code Action can run in the cloud.
10. Open `docs/claude-routine-instructions.md` to show the Claude Routine version that can fire on a GitHub release event.

Close with this framing:

> The AI never owns the numbers. The CRM export owns the numbers; the AI owns the summary language after the metrics are validated.
