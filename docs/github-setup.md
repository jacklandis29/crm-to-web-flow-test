# GitHub Setup

Use this when you want the full cloud demo with direct-to-main updates and GitHub Pages.

## One-Time Setup

1. Push this project to `jacklandis29/crm-to-web-flow-test`.
2. Go to **Settings -> Pages** and set the source to **GitHub Actions** so the static site can deploy.
3. Create the Claude Routine using `docs/claude-routine-instructions.md`.

GitHub Actions is only used to deploy Pages in this version. Claude Routine owns the data refresh and AI copy step.

## Primary Mock CRM Flow

Run:

```bash
npm run crm:win
```

This updates `data/mock-crm.json`, commits it with `[routine]`, pushes it, and publishes a `crm-refresh-*` GitHub release. The release wakes the Claude Routine.

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
