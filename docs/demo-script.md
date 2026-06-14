# Demo Script

A ~2.5–3 minute recorded walkthrough. The story: **today, turning a CRM change
into a published, written update is a manual chain. Put Claude in the middle and
it writes the story and ships it — automatically.**

Spoken lines are in quotes. Everything else is a stage direction.

---

## 1. Set the stage (~40s)

*Talking to camera, or on the live site.*

> "Let me start with where this comes from. Part of what I do is track metrics
> across our sector — the kind of numbers that matter for the partnerships we go
> after. They live in a CRM, and the way we share them across the org is an internal
> website: a dashboard people can actually look at.
>
> Today, that's a manual chain. The CRM gets updated. Someone exports the data,
> builds a Power BI dashboard, embeds it in the site — and then a person sits down
> and *writes the story*: what the numbers mean, why they moved, why they matter.
> Every time the data changes, someone rewrites that narrative by hand.
>
> So I built this to show what happens when you drop Claude into the middle of that
> chain. Claude doesn't connect to the CRM, and it doesn't own the data — it sits
> downstream. The moment something changes, that change flows to Claude through a
> routine. Claude already has the context for what these numbers *mean*, so it writes
> the story itself and pushes the updated site — automatically. That whole manual
> step disappears."

---

## 2. Show what's on screen (~25s)

*Scroll the live site slowly.*

> "Here's the site. The numbers up top are the data — straight from the source, not
> anything Claude invented. Down here is the narrative, and that's the part Claude
> writes.
>
> The split is deliberate. Claude never connects to the CRM and it never owns or
> alters a number — it only ever sees the validated data the routine hands it, and it
> only writes the words around it. And every claim it makes is tagged with the exact
> field it came from, so it's fully traceable. Right now the team's sitting just
> behind goal."

---

## 3. Change the data (~30s)

*Switch to your terminal.*

> "Now watch what happens when the data changes. I'll play the part of the CRM
> getting updated — say a big account just expanded."

```bash
npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000
npm run cloud:push
```

> "That change just flowed to the agent through the routine — the same way a live
> CRM update would trigger it. And I haven't told it a thing about what I changed."

*Switch to the Claude routine view; let it run.*

---

## 4. The payoff (~40s)

*Once the routine finishes, hard-refresh the live site (Cmd+Shift+R).*

> "The agent picked up the change, compared it against what was already live, and
> worked out on its own what moved — I never told it. And here's the result: it wrote
> this banner — 'Northstar Logistics grew by eight million dollars… total pipeline is
> now sixteen-point-two million.'
>
> It understood the change, wrote the story in plain English, and published it to the
> site. No export, no rebuilding a dashboard, no one writing copy by hand. And every
> figure is still tied straight back to the real data."

---

## 5. Honest caveat + close (~30s)

> "One bit of honesty about the demo: here I'm standing in a mock CRM and simplifying
> the data path, so it's not the full production setup — in the real thing you'd have
> the live CRM and a proper export feeding it. But the part I actually wanted to show
> is real, and it's the part that matters: Claude sitting between your data and your
> audience, turning a number change into a written, contextual update on its own.
>
> It collapses a whole manual process — export the data, build the dashboard, write
> the story, publish it — into something that just happens the moment the data moves.
> That's the time it saves. And that's the point."

---

## Run-of-show cheatsheet

| Step | Action |
| --- | --- |
| Before recording | `npm run crm:restore` (start at the behind-goal baseline), open the live site |
| Make the change | `npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000` |
| Publish it | `npm run cloud:push` → wakes the Claude Routine |
| Show the result | wait for the routine to commit, then hard-refresh the live site |
| Reset for another take | `npm run crm:restore` |

## Reliability notes (rehearse once before filming)

- The Claude Routine usually takes ~1–3 minutes; plan to cut or narrate during the wait.
- After the routine commits, GitHub Pages redeploys in ~15–20s. Hard-refresh
  (Cmd+Shift+R) — the page always loads the latest data, but the browser can hold an
  old shell.
- Pick an obviously big change on camera (the $9.18M edit takes one account from
  ~$1.2M to ~$9.2M — very visible).
