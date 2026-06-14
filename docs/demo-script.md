# Demo Script

1. Reset to a clean baseline:

   ```bash
   npm run crm:reset
   ```

   Wait for GitHub Pages to redeploy.

2. Open the website. It should show one obvious state:
   - closed-won sales are behind the goal
   - Claude copy says they are behind the goal

3. Show the CRM source briefly:
   - `data/mock-crm.json`
   - `.mcp.json`
   - `scripts/mock_crm_mcp_server.py`

4. Run:

   ```bash
   npm run crm:win
   ```

5. Explain what just happened:
   - a mock CRM opportunity changed to `Closed Won`
   - the command pushed the CRM change
   - the command published a `crm-refresh-*` release
   - that release wakes the Claude Routine

6. Show the Claude Routine run.

7. Refresh GitHub Pages.

8. The website should now show:
   - the closed-won number changed
   - the Claude copy changed
   - the source hash/revision changed

Close with this framing:

> The CRM owns the numbers. The MCP server exposes the CRM. Claude writes the words. The website shows both changes clearly.
