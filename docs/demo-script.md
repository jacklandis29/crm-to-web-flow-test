# Demo Script

1. Open the website. It should show one obvious state:
   - closed-won sales are behind the goal
   - Claude copy says they are behind the goal

2. Show the CRM source briefly:
   - `data/mock-crm.json`
   - `.mcp.json`
   - `scripts/mock_crm_mcp_server.py`

3. Run:

   ```bash
   npm run crm:win
   ```

4. Explain what just happened:
   - a mock CRM opportunity changed to `Closed Won`
   - the command pushed the CRM change
   - the command published a `crm-refresh-*` release
   - that release wakes the Claude Routine

5. Show the Claude Routine run.

6. Refresh GitHub Pages.

7. The website should now show:
   - the closed-won number changed
   - the Claude copy changed
   - the source hash/revision changed

Close with this framing:

> The CRM owns the numbers. The MCP server exposes the CRM. Claude writes the words. The website shows both changes clearly.
