# Fully Automated CRM-To-Site Flow

The professional demo path treats the CRM as a service:

```text
Mock CRM change
-> MCP/API-readable CRM source
-> deterministic validation snapshot
-> AI writes copy from validated facts
-> GitHub Pages deploy
```

## GitHub Actions Route

Run:

```bash
npm run crm:win-actions
```

End-to-end:

1. `scripts/mock_crm_update.py` changes `data/mock-crm.json`.
2. The command commits and pushes the CRM change to `main`.
3. GitHub Actions sees `data/mock-crm.json` change.
4. `.github/workflows/mock-crm-to-main.yml` runs `npm run crm:sync`.
5. The workflow creates `site/data/pipeline.json` and `site/data/audit-log.json`.
6. Claude Code Action, if configured, writes `site/data/ai-summary.json`.
7. The workflow validates source keys and commits generated website JSON.
8. The workflow deploys GitHub Pages.

## Claude Routine Route

Run:

```bash
npm run crm:win-routine
```

End-to-end:

1. `scripts/mock_crm_update.py` changes `data/mock-crm.json`.
2. The command commits and pushes the CRM change with a `[routine]` marker.
3. The command publishes a `crm-refresh-*` GitHub release.
4. The GitHub Action skips `[routine]` commits.
5. The Claude Routine wakes from **Release published**.
6. Claude runs `npm run crm:sync`, updates `site/data/ai-summary.json`, validates, and commits generated JSON.
7. GitHub Pages deploys after generated site files change.

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

MCP does not replace the trigger. It is the data access layer. The release, push, issue, schedule, or webhook-like event is the trigger layer.

## Anti-Hallucination Boundary

The AI never writes numbers directly.

1. CRM data is validated into `site/data/pipeline.json`.
2. AI reads `pipeline.json`.
3. AI writes only `site/data/ai-summary.json`.
4. `scripts/validate_ai_summary.py` checks that every source key resolves into `pipeline.json`.

That gives you an auditable chain from CRM source to public website copy.
