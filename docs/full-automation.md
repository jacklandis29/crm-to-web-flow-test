# Fully Automated CRM-To-Site Flow

The demo path is:

```text
Mock CRM change
-> MCP-readable CRM source
-> crm-refresh release
-> Claude Routine wakes up
-> deterministic CRM snapshot
-> Claude writes copy from validated facts
-> GitHub Pages updates
```

## Main Demo Command

First reset the public site to the known behind-goal baseline:

```bash
npm run cloud:reset
```

After GitHub Pages redeploys, run the actual automated demo:

Run:

```bash
npm run cloud:win
```

End-to-end:

1. `scripts/mock_crm_update.py` changes `data/mock-crm.json`.
2. The command commits and pushes the CRM change with a `[routine]` marker.
3. The command publishes a `crm-refresh-*` GitHub release.
4. The Claude Routine wakes from **Release published**.
5. Claude runs `npm run crm:sync`.
6. Claude updates only `site/data/ai-summary.json`.
7. Claude runs `npm run validate`.
8. Claude commits generated website JSON to `main`.
9. GitHub Pages redeploys.

## MCP Role

Run the local mock CRM MCP server:

```bash
npm run crm:mcp
```

MCP lets Claude or another MCP-aware client inspect:

- current CRM revision
- opportunity rows
- validated pipeline snapshot
- recent CRM change events

MCP is the data access layer. The release is the trigger layer.

## Anti-Hallucination Boundary

The AI never writes numbers directly.

1. CRM data is validated into `site/data/pipeline.json`.
2. Claude reads `pipeline.json`.
3. Claude writes only `site/data/ai-summary.json`.
4. `scripts/validate_ai_summary.py` checks that every source key resolves into `pipeline.json`.
