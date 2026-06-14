# Demo Script

1. Show `data/mock-crm.json` and explain that it is a sanitized CRM source.
2. Show `.mcp.json` and `scripts/mock_crm_mcp_server.py` to explain that Claude/tools can query the CRM through MCP.
3. Open the website and point out the current closed-won goal status.
4. Run one of these:

   ```bash
   npm run crm:win-actions
   ```

   or:

   ```bash
   npm run crm:win-routine
   ```

5. Explain that this simulates a CRM user changing an opportunity to `Closed Won`.
6. For the Actions path, open GitHub Actions and show `.github/workflows/mock-crm-to-main.yml` running.
7. For the Routine path, show the `crm-refresh-*` release and the Claude Routine run.
8. When it completes, refresh GitHub Pages.
9. Open `site/data/pipeline.json` and show that the numbers are a validated CRM snapshot.
10. Open `site/data/ai-summary.json` and show that the AI copy references source keys from the snapshot.

Close with this framing:

> The CRM owns the numbers. The MCP server exposes the CRM. The deterministic sync freezes validated facts. The AI only writes language from those facts.
