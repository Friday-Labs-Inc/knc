# KNC — Build Roadmap

Locked: 2026-06-11 · Milestones in dependency order · no dates

## M0 — Foundation
- Frappe Cloud private bench confirmed
- Install apps: Payments, Helpdesk, Drive
- ERPNext setup: Company, USD, fiscal year
- Stripe credentials (test mode) via Payments app
- Item `RP-ESSENTIALS` (non-stock service) + Item Price $4,800
- Selling Settings: `dn_required = 0`, no Quotation in flow
- Email: support@ → Helpdesk inbound · no-reply outbound · SPF/DKIM

## M1 — App scaffold & capture
- `bench new-app knc` · GitHub repo · deploy pipeline to bench
- DocTypes: KNC Brief, KNC Brand Attribute, KNC Brief Reference, KNC Gate Decision, KNC Event, KNC Settings, KNC Integration Settings
- Custom fields: Task (`is_gate`, `client_visible`) · HD Ticket (`project` link)
- `/start` wizard with per-step auto-save (Draft = warm lead)

## M2 — Deal-close automation
- Brief-submit hook: Customer → Contact → Sales Order → Payment Request → Stripe checkout
- Payment kickoff chain (idempotent, ordered): brief Paid + snapshot → day-0 Sales Invoice → Project from template anchored to preferred_start → Drive folder tree + upload copy → portal user invite → brief Converted
- Project Template "Essentials — 10 Day" (7 tasks, gate dependencies)
- Error queue + admin alerts · unpaid-SO auto-close scheduler
- Milestone test: wizard → test card → engagement scaffolds itself end-to-end

## M3 — Portal
- Routes: /portal · /portal/project/<id> · /portal/brief · /portal/files · /portal/support
- Timeline rail · current-phase panel · comment thread
- Gate 1 flow (three directions, selection, KNC Gate Decision)
- Gate 2 flow (approve / refinement rounds, delivery-date recalc)
- Permission queries (own records only, no desk access)
- Notification email set + 24h nudge scheduler + visible pause flag

## M4 — Integration layer
- KNC Event outbox + delivery worker (HMAC, exponential retry, replay)
- Inbound API `knc.api.v1.*` + Friday Integration role
- KNC Integration Settings (subscribers, secrets, enabled events)
- Test against dummy webhook receiver

## M5 — Hardening & launch
- Full journey rehearsal in Stripe test mode (wizard → pay → gates → delivery)
- Failure drills: payment succeeds but kickoff step fails → retry from error queue
- Backups, monitoring, log review
- Switch Stripe live · soft-launch with pilot clients

## Phase 2 (anytime after M4)
Friday AI backend connects via the event bus + inbound API. No changes to M0–M5 required.
