> **Archived.** This repository is a mis-named copy of the RandomPack product. The product lives at
> [Friday-Labs-Inc/randompack](https://github.com/Friday-Labs-Inc/randompack); Klick N Click is its first customer.

# knc

The custom Frappe app behind [knc.studio](https://knc.studio) —
onboarding capture, deal-close automation, gate governance, and the
Friday AI integration seam, on top of ERPNext.

**Rule:** Builder owns the UI. ERPNext owns money, projects, tickets.
This app owns capture, automation, client experience APIs, and events.

## What it contains

| Module | Purpose |
|---|---|
| `knc/doctype/*` | KNC Brief, KNC Gate Decision, KNC Event, KNC Brand Attribute, RP/KNC Integration Settings |
| `automation/selling.py` | Brief → Customer → Sales Order → Payment Request (Stripe) |
| `automation/kickoff.py` | Payment → invoice + project + Drive folders + portal invite (idempotent) |
| `automation/gates.py` | Gate decisions, task unblocking, refinement rounds, delivery events |
| `automation/scheduler.py` | 24h gate nudges, unpaid-SO auto-close |
| `integrations/outbox.py` | Persisted event outbox, HMAC delivery, retries, replay |
| `api/v1.py` | One API contract for Builder pages and Friday |
| `install.py` | Seeds item, price, template, attributes, custom fields, starter pages |
| `builder-kit/` | Client scripts to paste into Builder pages (/start, /portal) |

## Documentation

| Doc | What it covers |
|---|---|
| [docs/CONTRACT.md](docs/CONTRACT.md) | **Canonical Friday integration contract** — every event payload, the signature algorithm, all inbound endpoints. The interop bible; both sides build to this. |
| [docs/INTEGRATION-TESTING.md](docs/INTEGRATION-TESTING.md) | **End-to-end test runbook** — two-bench (v15 + v16) topology, wiring knc ↔ Friday, handshake test, full journey rehearsal. |
| [docs/HANDOFF.md](docs/HANDOFF.md) | **Status & what's left** — what's built, what's not wired, prioritized next steps for picking-up agents. |
| [docs/specs/](docs/specs/) | The locked product specs (stack, roadmap, onboarding brief, hooks/template, portal, integration, brand guidelines). Source of intent. |
| [scripts/bench-setup.sh](scripts/bench-setup.sh) | One-command v15 bench with the full stack (macOS-tuned; see testing doc for Linux/Legion 5). |

## Install

```bash
bench get-app /path/to/knc
bench --site yoursite install-app knc
```

Seeding runs automatically on install (idempotent — safe to re-run):

```bash
bench --site yoursite execute knc.install.after_install
```

Or build a complete local bench with the whole stack:

```bash
../bench-setup.sh
```

## Event contract (v1)

Emitted: `brief.submitted`, `payment.received`, `payment.refunded`,
`project.created`, `project.cancelled`, `phase.changed`, `gate.opened`,
`gate.reminder`, `gate.decided`, `refinement.requested`, `comment.added`,
`files.delivered`, `project.completed`.

Envelope: `{id, type, version, occurred_at, data}`. Signature header
`X-RP-Signature: t=<unix>,v1=<hex>` where `v1 = HMAC-SHA256(secret,
"{t}.{raw_body}")`, signed per delivery attempt (retries and replays
carry a fresh `t`). Configure subscribers in **KNC Integration Settings**.

Inbound (Friday Integration role): `update_task_progress` (with
`progress` heartbeat + `Pending Review` needs-human status),
`attach_deliverable`, `post_project_note`, `request_gate_open`
(signal only), `get_project`, `get_comments`.

## Re-run a failed kickoff

```bash
bench --site yoursite execute knc.automation.kickoff.run_kickoff \
  --kwargs "{'brief_name': 'KNC-BRIEF-0001'}"
```

## License

AGPL-3.0-or-later. See [license.txt](license.txt).
