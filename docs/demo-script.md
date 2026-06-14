# Demo Script (recorded walkthrough)

Total runtime: ~2 minutes. Everything runs locally — no network, nothing to fail
on camera.

## Before you record

```bash
npm run demo:reset   # start behind goal
npm run serve        # http://localhost:4173
```

Open the page. It should read **$1,750,000 closed-won, $250,000 behind goal**, red
progress bar.

## The talk track

**1. Frame the problem (15s).**
> "Sales leadership wants a live internal page off the CRM. Easy to wire the
> numbers up. The risk is the *commentary* — nobody wants an AI quietly inventing
> a figure on a page execs read. So I split it: the CRM owns the numbers, code
> validates them, and the AI only ever writes words."

**2. Show the source of truth (20s).** Open `data/mock-crm.json`.
> "This is the mock CRM — the system of record. It's also exposed over MCP, so an
> agent can query it as live tools, not a copied spreadsheet."

Optionally run `npm run crm:mcp` and call `crm_get_revision` to show it's a real
service.

**3. Show the page (20s).** Scroll it.
> "Numbers up top come straight from the validated CRM snapshot. Down here is the
> Claude-authored copy — and notice every sentence is tagged with the exact
> `pipeline.json` field it used. That's the guardrail, made visible."

**4. Change the CRM yourself (15s).** Edit any company — by hand in
`data/mock-crm.json`, or with one command. Don't say which one you changed:

```bash
npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000
```

> "I'm going into the CRM and bumping one account's number — let's say a big
> expansion just landed. Nothing on the website knows about this yet."

Then run the routine:

```bash
npm run refresh
```

> "That re-ran validation into a fresh snapshot and handed it to the AI step — which
> diffed it against what's live and wrote copy about the difference. Watch the
> guardrail pass."

**5. The payoff (20s).** Refresh the browser.
> "Up top — an 'Updated from CRM' banner the AI wrote on its own. I never told it
> what I changed; it compared the new numbers to the published ones and figured it
> out: Northstar Logistics grew $8 million, total pipeline is now $16.2 million. And
> every figure carries the validated field it came from. The model wrote the story
> about my edit. It never touched a number."

Reset between takes with `npm run crm:restore`.

**6. Close (15s).**
> "Locally this is a deterministic stand-in so the demo is repeatable. In
> production the exact same contract runs in the cloud: a CRM change publishes a
> release, a Claude Routine wakes up, reads the validated snapshot, writes the
> copy, and the guardrail blocks the commit if any claim can't be traced. Same
> boundary, same safety."

## Reset between takes

```bash
npm run crm:restore   # undo any hand edit, back to the committed baseline
# or, for the scripted demo:win flow:
npm run demo:reset
```

## If you want to show the cloud path too

`docs/full-automation.md` covers `npm run cloud:push` (publish any hand edit) and
`npm run cloud:win` (the scripted close), which push the CRM change and publish the
GitHub Release that triggers the Claude Routine. Leave this out
of the core recording — it depends on GitHub Pages redeploy timing — and mention
it verbally instead.
