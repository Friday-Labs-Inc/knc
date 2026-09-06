# Hooks & Project Template — Spec

Locked: 2026-06-11 · The engine room of the `knc` app

## Project Template: "Essentials — 10 Day"
Custom fields on Task: `is_gate` (Check), `client_visible` (Check)

| # | Task | Days | Depends on |
|---|---|---|---|
| 1 | Intake review | D0 | — |
| 2 | Strategy & naming | D1–3 | 1 — checklist varies by brief `naming_status` |
| 3 | Three directions | D4–5 | 2 |
| 4 | **Gate 1 — choose direction** | D5 | 3 |
| 5 | Build system | D6–9 | 4 (blocked until KNC Gate Decision) |
| 6 | **Gate 2 — final review** | D9 | 5 |
| 7 | Delivery & handoff | D10 | 6 (blocked until approve) |

## Hook chain

### A. Wizard completes (brief submitted)
Validate → create Customer + Contact → submit Sales Order (RP-ESSENTIALS, $4,800) → Payment Request → return Stripe checkout URL → redirect. Emit `brief.submitted`.
Unpaid SOs auto-closed by scheduler after 7 days.

### B. Payment Entry on_submit — idempotent, ordered
1. Brief → Paid; freeze `brief_snapshot`
2. Day-0 Sales Invoice, advance allocated, submitted
3. Project from template, anchored to **preferred_start** (confirmed: pay today, start later is allowed), linked to brief/SO/customer
4. Drive folder tree (01-Brief … 05-Handoff), brief uploads copied in
5. Website User + portal invite email
6. Brief → Converted; emit `payment.received`, `project.created`

Failure handling: error queue + admin alert, each step retryable; payment never stranded in a half-built state.

### C. Running the engagement
- Task status change → `phase.changed` + portal update + client email
- Gate task starts → `gate.opened` + portal gate panel + email
- KNC Gate Decision saved → unblock dependents, `gate.decided` webhook
- Refinement round → new KNC Gate Decision row, delivery date recalculated, shown in portal
- Scheduler (hourly): gate open >24h, no decision → nudge email + visible "paused" flag
- Task 7 complete → share Drive handoff folder, emit `files.delivered` + `project.completed`, close project

### D. Capacity
KNC Settings singleton: `max_active_projects`. Wizard validates `preferred_start` against open slots; offers next open window when full.
