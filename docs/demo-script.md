# Demo Script

A ~2–3 minute recorded walkthrough. The story: **put Claude between a CRM and a
website, so when the data changes, an agent understands what the change means and
publishes a clear, updated story to the site — automatically.**

Spoken lines are in quotes. Everything else is a stage direction.

---

## 1. Set the stage (~30s)

*Start on the live site (the GitHub Pages URL), or just talking to camera.*

> "Quick bit of framing first. This isn't me showing you something from my actual
> job that I then have to hand-wave around — it's a small example I built from
> scratch to show a pattern I think is really useful.
>
> The idea is to put Claude *in between* your CRM and a website — could be internal,
> could be external. Claude sits in the middle with all the context you'd give it:
> whether that's Claude Enterprise's knowledge of your organization, or context
> you've written in yourself. So when a number changes in the CRM, an agent picks
> that up, understands what the change actually *means* in context, and
> automatically pushes a clean, readable update out to the site.
>
> What I've got here is a small, working version of that. In a real build you'd
> wire in a lot more context and automate more of the plumbing. But the point of
> this demo is narrow and specific: to show the value of putting a *contextual*
> large language model between a CRM and a website."

---

## 2. Show what's on screen (~25s)

*Scroll the live site slowly.*

> "Here's the site. It's a sales pipeline view. The numbers up top — closed-won,
> pipeline, forecast — come straight from the CRM. Down here is the narrative, and
> *that* part is written by Claude.
>
> One deliberate design choice: Claude never touches the numbers. The CRM owns
> those; Claude only writes the words. So it physically can't make a figure up —
> and you can see every sentence it writes is tagged with the exact data field it
> came from. Right now the team is sitting just behind goal."

---

## 3. Change the CRM (~30s)

*Switch to your terminal (or the CRM data file).*

> "Now I'm going to play the part of someone in the business and just… change the
> CRM. Let's say a big account just expanded."

*Run:*

```bash
npm run crm:edit -- --opportunity OPP-2026-001 --amount 9185000
npm run cloud:push
```

> "That committed the change and kicked off the agent — the same way a webhook off
> your CRM would trigger it in production. I haven't told the agent anything about
> what I changed."

*Switch to the Claude routine view; let it run.*

---

## 4. The payoff (~40s)

*Once the routine finishes, refresh the live site (hard-refresh: Cmd+Shift+R).*

> "Here's what happened. The agent woke up, pulled the new CRM data, compared it
> against what was already live, and worked out *on its own* what changed — I never
> told it.
>
> And here's the result up top — this 'Updated from CRM' banner it wrote: 'Northstar
> Logistics grew by eight million dollars… total pipeline is now sixteen-point-two
> million.' It understood the change, wrote a plain-English summary of what it means,
> and published it to the site. And every number is still tagged with the validated
> field behind it — so it's accurate, not invented."

---

## 5. Close (~20s)

> "So that's the demo. To be clear about what it is: a small, working showcase of a
> pattern, not a finished product. If you were really building this, you'd give the
> agent a lot more context and automate more of the connective tissue between
> systems. But what it shows is the core benefit — a contextual model sitting
> between your CRM and your website, so the moment your data changes, the story your
> audience reads changes with it: automatically, accurately, and in plain language."

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
  (Cmd+Shift+R) — the site now always loads the latest data, but the browser may hold
  the old page shell.
- Pick a number change that's obviously big on camera (the $9.18M edit takes one
  account from ~$1.2M to ~$9.2M — very visible).
