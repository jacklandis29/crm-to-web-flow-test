# Claude Routine Setup

Use these settings in the Claude Routine screen.

## Name

```text
CRM to Website Flow Test
```

## Recommended Trigger

Use **Release published**.

Reason: it gives you a clean demo button. You can push an updated Excel workbook, publish a release named something like `crm-refresh-2026-06-14`, and Claude will run the routine.

## Instructions To Paste

```text
You are running the automated CRM-to-website refresh for jacklandis29/crm-to-web-flow-test.

Goal:
Refresh the website from the latest sanitized CRM Excel export, then update only the AI-authored website copy from the validated metrics, commit the generated website files directly to main, and let GitHub Pages deploy.

Repository:
jacklandis29/crm-to-web-flow-test

Branch:
main

Steps:
1. Check out or open the latest main branch.
2. Read CLAUDE.md and follow it.
3. Run:
   npm run refresh:data
4. Read site/data/pipeline.json.
5. Update site/data/ai-summary.json as the AI-authored copy step.
   - Do not change any numeric facts.
   - Do not edit the Excel workbook.
   - Do not manually edit site/data/pipeline.json.
   - Do not manually edit site/data/audit-log.json.
   - Every substantive claim in the copy must include source keys that resolve into site/data/pipeline.json.
   - The lead copy must explicitly say whether closed-won sales are ahead of or behind the goal using metrics.closedWon, metrics.closedWonGoal, metrics.closedWonDelta, and metrics.closedWonAttainment.
6. Run:
   npm run validate
7. If validation fails, fix only site/data/ai-summary.json unless the failure says the workbook/data generation step failed.
8. Commit only these files to main:
   - site/data/pipeline.json
   - site/data/audit-log.json
   - site/data/ai-summary.json
9. Use this commit message:
   Refresh website data and AI copy from CRM export
10. Push directly to main.

Important:
The Excel workbook owns the numbers. The AI owns only the summary language after validation. If there are no generated file changes, do not create an empty commit.
```

## Permissions

Give the routine permission to:

- Read repository contents
- Write repository contents / push commits
- Run repository commands if the UI asks for behavior/tool permissions

## Demo Choreography

1. Push the repo to GitHub.
2. Enable GitHub Pages.
3. Open the live Pages site.
4. Edit `data/crm-export-june-2026.xlsx` locally.
5. Save it.
6. Commit and push the workbook change to `main`.
7. Publish a GitHub release.
8. The Claude Routine fires from the release event.
9. Claude commits updated generated JSON files to `main`.
10. GitHub Pages redeploys and the live site changes.

## Automatic Local Trigger

To publish the release automatically after saving Excel, run:

```bash
npm run watch:routine
```

This watcher commits and pushes the workbook, then publishes a `crm-refresh-*` release. That release is what wakes this Routine.
