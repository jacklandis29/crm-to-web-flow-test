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

Edit any opportunity, then publish it:

```bash
npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000   # or hand-edit data/mock-crm.json
npm run cloud:push
```

(`npm run cloud:win` is the scripted shortcut that closes CivicGrid Energy and publishes in
one step. `npm run cloud:reset` returns the live site to the behind-goal baseline.)

End-to-end:

1. The CRM edit changes `data/mock-crm.json`.
2. `cloud:push` commits and pushes it with a `[routine]` marker (bumping the revision so the
   release tag is unique).
3. It publishes a `crm-refresh-*` GitHub release.
4. The Claude Routine wakes from **Release published**.
5. Claude runs `npm run crm:sync`, which writes a `changeReport` (the diff vs the last
   published snapshot) into `site/data/pipeline.json`.
6. Claude updates only `site/data/ai-summary.json`, leading with what changed.
7. Claude runs `npm run validate`.
8. Claude commits the generated website JSON to `main`.
9. GitHub Pages redeploys and the live site shows the change.

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
