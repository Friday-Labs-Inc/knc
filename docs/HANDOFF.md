# Integration Handoff & Status

For agents picking up the knc ⇄ Friday integration. Read
[CONTRACT.md](CONTRACT.md) and [INTEGRATION-TESTING.md](INTEGRATION-TESTING.md)
alongside this.

_Last updated: 2026-06-13._

---

## Where it stands — three layers

**Layer 1 — knc contract surface · ✅ DONE (40 tests).**
Everything Friday talks to is built and tested: 13 events, per-attempt HMAC
signing, retry/backoff, replay, retention purge; 6 inbound endpoints; the
`Friday Integration` role gating writes.

**Layer 2 — the actual connection · ❌ NOT WIRED.**
On the dev site: **0** subscribers, **0** users with the Friday role, Friday's
`receive_event` not yet live. The two halves have never exchanged a real message.
The contract is *designed* to match; it is not yet *proven* to interoperate.

**Layer 3 — the journey that feeds Friday · ⚠️ GAPS.**
No Stripe gateway configured → the payment path (trigger for `payment.received`
/ `project.created`) has **never run**, even locally. 0 real briefs; all events
on the dev site are test artifacts.

> "Integration-ready", not "integrated."

---

## Prioritized next steps

1. **Friday: finish `receive_event`** (their side) — verify HMAC → persist
   (UUID-unique) → `200` immediately → process async. Until this exists, nothing
   can be wired.
2. **Wire + handshake** — INTEGRATION-TESTING §4–5. Create the Friday API user,
   exchange the secret, add the subscriber row, prove both directions with the
   smallest loop before anything else.
3. **Stripe test mode** — INTEGRATION-TESTING §2b. Unblocks the entire front of
   the pipeline; without it the real triggers never fire.
4. **Full journey rehearsal** — INTEGRATION-TESTING §6.

### Open work items on the knc side
| Item | Where | Note |
|---|---|---|
| Capacity check ignores the requested date | `automation/selling.py` `validate_start_date` | Spec says validate `preferred_start` against open slots + offer next window; currently counts active projects today and ignores the arg. |
| Brief uploads not copied into Drive at kickoff | `automation/kickoff.py` `_step_drive_folders` | TODO comment in place; folders are created, uploads not yet copied in. |
| "exactly 3" personality attributes | `api/v1.py` `save_step` step 5 | Enforced as `max 3`, spec says exactly 3. |
| Heartbeat rate-limit calibration | `api/v1.py` `update_task_progress` (720/hr) | Tune once Friday shares real heartbeat cadence. |
| Brief enrichment fields (tone samples, hard constraints, usage surfaces, locale, decision-maker) | onboarding brief + wizard | **Product decision pending** with the owner — not yet scoped. |

### Pushed back (decided not to build)
- `brief.updated` event — briefs are immutable after submit (enforced in
  `save_step`), so the state can't occur.
- "rounds remaining" counter — there is no round cap (unlimited refinements at
  +2 delivery days each); `refinement.requested` carries `round`.

---

## Code map

| Path | Responsibility |
|---|---|
| `knc/api/v1.py` | The one API: wizard (guest), portal (customer), Friday inbound (role-gated). |
| `knc/automation/selling.py` | Brief → Customer → Sales Order → Payment Request (Stripe). |
| `knc/automation/kickoff.py` | Payment → invoice + project + Drive + portal invite; `payment.refunded` emit. Idempotent. |
| `knc/automation/gates.py` | Gate open guard, gate.decided handling, delivery detection; `project.cancelled` emit. Order-based gate identity. |
| `knc/automation/scheduler.py` | Hourly gate nudge (+`gate.reminder` emit), daily unpaid-SO close. |
| `knc/integrations/outbox.py` | Outbox: persist, per-attempt sign, deliver, retry, purge; `comment.added` hook. |
| `knc/install.py` | Seeds item/price/template/attributes/custom fields/settings + **template task dependency chain**. Idempotent. |
| `knc/hooks.py` | Wires all doc_events + scheduler. |
| `builder-kit/` | Client scripts for the Builder `/start` and `/portal` pages. |

---

## Conventions for picking-up agents

- The app is developed **outside the bench**, symlinked in. On a Legion 5 clone
  it's a normal git checkout under `apps/knc` — edit there.
- **Run the test suite before pushing** — it's the integration's safety net:
  `bench --site <site> run-tests --app knc` must stay green.
- Add tests with new behaviour. Current suites: `test_api_security`, `test_gates`,
  `test_outbox`, `test_selling`, `test_friday_contract`.
- The contract is versioned **v1**, additive-only. Anything breaking → bump and
  run parallel. Update [CONTRACT.md](CONTRACT.md) in the same change.
- Gate identity is **order-based**, never by task subject (subjects are display
  copy). Use `gates.gate_label()` / `gates.gate_tasks()`.
