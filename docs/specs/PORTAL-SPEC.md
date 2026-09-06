# Customer Portal — Spec

Locked: 2026-06-11 · Custom portal pages in `knc` app · website users only, no desk access

## Access
Payment hook creates Website User (Customer role) → Contact → Customer. Permission query restricts all data to own records. Invite email sets password.

## Routes

| Route | Purpose |
|---|---|
| /portal | Home — engagement card: day counter, phase, next action |
| /portal/project/<id> | Main page — timeline rail (7 tasks, Day 0–10), current-phase panel, gate panel, comment thread (Frappe Comments on Project = the async channel) |
| /portal/brief | Read-only brief_snapshot + deliverables list + paid Sales Invoice PDF |
| /portal/files | Project's Drive folder — presentations, Day-10 handoff package |
| /portal/support | Helpdesk tickets, auto-linked to active Project |

## Gate mechanics

**Gate 1 (Day 5):** three direction cards (preview, rationale, Drive presentation link) → client selects one + comments → KNC Gate Decision record → unblocks Build tasks → notifies team → fires Phase-2 webhook.

**Gate 2 (Day 9) — flexible refinement:**
- Approve or request refinements; no hard limit shown in portal
- Each round = a KNC Gate Decision record (round n + notes) — explicit history
- Art director decides refinement (in scope) vs new scope (conversation / add-on SO)
- Round 1 fits in 10 days; further rounds visibly move delivery date in the portal
- Delivery task unblocks only on approve

**24h commitment:** gates show the reminder; past 24h → automated nudge + timeline shows "paused — waiting on you". Day counter pauses visibly when waiting on client.

## Notifications (deep-link to portal, no-reply sender)
Payment receipt + invite · phase changes · gate open · 24h nudge · team comment reply · files delivered

## Design
Same visual language as knc.studio marketing site.
