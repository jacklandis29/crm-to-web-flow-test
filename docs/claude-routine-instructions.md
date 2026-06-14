# Claude Routine Setup

Use these settings in the Claude Routine screen.

## Name

```text
CRM to Website Flow Test
```

## Recommended Trigger

Use **Release published**.

Reason: MCP gives Claude access to CRM data once Claude is running, but it does not wake the routine by itself. The release event is the clean demo trigger.

## Instructions To Paste

```text
You are running the automated CRM-to-website refresh for jacklandis29/crm-to-web-flow-test.

Goal:
Refresh the website from the latest mock CRM data, update only the AI-authored website copy from validated metrics, commit the generated website files directly to main, and let GitHub Pages deploy.

Repository:
jacklandis29/crm-to-web-flow-test

Branch:
main

Steps:
1. Check out or open the latest main branch.
2. Read CLAUDE.md and follow it.
3. Treat data/mock-crm.json as the CRM source of truth. If a mock-crm MCP connector is available, use it to inspect the current CRM revision and pipeline snapshot.
4. Run:
   npm run crm:sync
5. Read site/data/pipeline.json. This is the validated source of truth for all published numbers.
   - It includes a `changeReport` block describing what moved since the last published
     snapshot (which opportunities changed, from/to values, and metric deltas).
6. Update site/data/ai-summary.json as the AI-authored copy step.
   - Do not change any numeric facts.
   - Do not edit data/mock-crm.json.
   - Do not manually edit site/data/pipeline.json.
   - Do not manually edit site/data/audit-log.json.
   - Every substantive claim in the copy must include source keys that resolve into site/data/pipeline.json.
   - The lead copy must explicitly say whether closed-won sales are ahead of or behind the goal using metrics.closedWon, metrics.closedWonGoal, metrics.closedWonDelta, and metrics.closedWonAttainment.
   - If `changeReport.hasChanges` is true, add a top-level `change` object ({headline, body,
     sources}) that leads with WHAT CHANGED this refresh — name the opportunity, state the
     from/to, and quantify the ripple into the metrics. Cite the changed opportunity's current
     value (e.g. opportunities[i].amount) and the moved metrics. Omit `change` when there are
     no changes.
7. Run:
   npm run validate
8. If validation fails, fix only site/data/ai-summary.json unless the failure says the CRM sync step failed.
9. Commit only these files to main:
   - site/data/pipeline.json
   - site/data/audit-log.json
   - site/data/ai-summary.json
10. Use this commit message:
   Refresh website data and AI copy from mock CRM
11. Push directly to main.

Important:
The CRM owns the numbers. The deterministic sync owns validation. The AI owns only the summary language after validation. If there are no generated file changes, do not create an empty commit.
```

## Permissions

Give the routine permission to:

- Read repository contents
- Write repository contents / push commits
- Run repository commands if the UI asks for behavior/tool permissions
- Use the mock CRM MCP connector if you configure it in Claude

## Demo Choreography (edit any company, on camera)

1. Push the repo to GitHub; enable GitHub Pages (Settings → Pages → source: GitHub Actions).
2. Open the live Pages site. Note the current numbers — no "Updated from CRM" banner.
3. Edit any opportunity. Either hand-edit `data/mock-crm.json`, or:

   ```bash
   npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000
   ```

   (`crm:edit` bumps the revision and logs a change event; a hand edit works too —
   `cloud:push` will bump the revision for you so the release tag stays unique.)
4. Publish it to wake the routine:

   ```bash
   npm run cloud:push
   ```

5. That commits `data/mock-crm.json` with a `[routine]` marker, pushes it, and publishes a
   `crm-refresh-rev-*` GitHub release.
6. The Claude Routine fires from the release event.
7. Claude runs the sync, reads `pipeline.json` (including `changeReport`), authors the
   **change-aware** copy that names what you edited, validates, and commits the generated
   JSON to `main`.
8. GitHub Pages redeploys; the live site shows your number change and the AI's "Updated
   from CRM" banner about it.

To reset for another take: `npm run cloud:reset` (scripted baseline) or revert the CRM
commit and push.
