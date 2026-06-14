# GitHub Setup

Use this when you want the full cloud demo with direct-to-main updates and GitHub Pages.

## One-Time Setup

1. Push this project to `jacklandis29/crm-to-web-flow-test`.
2. Go to **Settings -> Actions -> General** and allow GitHub Actions.
3. Set workflow permissions to **Read and write permissions**.
4. Go to **Settings -> Pages** and set the source to **GitHub Actions**.
5. Add `ANTHROPIC_API_KEY` in **Settings -> Secrets and variables -> Actions** if you want GitHub Actions to use Claude Code Action.

Without `ANTHROPIC_API_KEY`, the workflow uses the deterministic fallback summary generator so the automation still runs.

## Primary Mock CRM Flow

Run:

```bash
npm run crm:win-actions
```

This updates `data/mock-crm.json`, commits it, pushes to `main`, and triggers `.github/workflows/mock-crm-to-main.yml`.

The workflow:

1. Syncs mock CRM data into `site/data/pipeline.json`.
2. Writes `site/data/audit-log.json`.
3. Uses Claude Code Action, or fallback copy generation, to write `site/data/ai-summary.json`.
4. Validates source keys.
5. Commits generated site data to `main`.
6. Deploys GitHub Pages.

## Claude Routine Flow

Use this when you want the Claude Routine UI to be the visible AI automation:

```bash
npm run crm:win-routine
```

This updates `data/mock-crm.json`, commits it with `[routine]`, pushes it, and publishes a `crm-refresh-*` GitHub release. The mock CRM workflow skips `[routine]` commits, so the Routine owns that run.

Routine instructions live here:

[claude-routine-instructions.md](/Users/jack/Documents/crm-to-web-flow/docs/claude-routine-instructions.md)

Recommended Routine trigger: **Release published**.

## MCP Setup

The mock CRM MCP server is local and dependency-free:

```bash
npm run crm:mcp
```

The repo includes `.mcp.json` for MCP-aware local clients. For a cloud-hosted Claude connector, the same server would need to run in an environment Claude can access or be adapted to the connector hosting model.

## Legacy Excel Flow

The older Excel route still exists for comparison:

```bash
npm run watch:excel
```

It triggers `.github/workflows/crm-export-to-main.yml`.
