# KNC ⇄ Friday — Integration Contract (v1)

**Status:** knc side implemented & tested (40 tests). Friday `receive_event`
surface in progress. This document is the wire contract; both sides build to it.

## Principle

knc owns the truth and **emits facts**; Friday **consumes facts** and
writes back through a guarded, versioned API. knc never calls Friday's
business logic — it posts signed events to a subscriber URL. Friday never writes
to knc's database directly — it calls the whitelisted `knc.api.v1`
methods with an API key.

```
knc  ──(signed webhook: events)──▶  Friday  receive_event
knc  ◀──(REST: writes/reads)─────   Friday  api.v1.*
```

---

## 1. Outbound events (knc → Friday)

### Transport
`HTTP POST`, body is the JSON envelope (UTF-8), `Content-Type: application/json`.
One POST per subscriber per event. Delivered by the outbox worker
(`knc.integrations.outbox`), retried with exponential backoff
(`2^n` minutes, `max_retries` default 8), replayable.

### Envelope
```json
{
  "id": "f1e2d3c4-...-uuid4",      // idempotency key — stable across retries
  "type": "gate.decided",          // event type (see table)
  "version": "v1",
  "occurred_at": "2026-06-13 09:47:48.123456",
  "data": { ... }                  // type-specific, see table
}
```

### Signature — `X-RP-Signature`
Per **delivery attempt** (Stripe-style). Header:
```
X-RP-Signature: t=<unix_seconds>,v1=<hex>
```
where
```
v1 = HMAC_SHA256(secret, f"{t}.{raw_body}")
```
- `secret` = the shared secret on the subscriber row (KNC Integration Settings).
- `raw_body` = the **exact bytes received**. ⚠️ Verify over the raw body, never
  over a re-serialized JSON object — re-encoding changes whitespace/key order
  and breaks the HMAC. This is the #1 integration bug; see INTEGRATION-TESTING.md.
- `t` is regenerated on every attempt, so **retries and replays stay valid**
  under a staleness window.

Also sent: `X-RP-Event: <outbox row id>` (support/debug correlation).

### Friday verification recipe
```python
import hmac, hashlib, time

def verify(raw_body: bytes, header: str, secret: str, tolerance=300) -> bool:
    parts = dict(p.split("=", 1) for p in header.split(","))
    t, v1 = parts["t"], parts["v1"]
    if abs(time.time() - int(t)) > tolerance:        # optional staleness check
        return False
    expected = hmac.new(secret.encode(), f"{t}.".encode() + raw_body,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(v1, expected)
```

### Idempotency
Dedupe on the envelope **`id`**. It is the same across all retries of one event
and unique per business occurrence. A duplicate POST (same `id`) must be a no-op
that returns `2xx`. Replays carry the original `id`.

### Delivery semantics
- `2xx` → knc marks the event `Delivered`.
- Any other response or a timeout (15s) → `Failed`, retried with backoff until
  `max_retries`. After that it stays `Failed` until manually replayed.
- Events are purged after `retention_days` (default 90).

### Event catalogue

| `type` | Fires when | `data` |
|---|---|---|
| `brief.submitted` | Wizard final step (pre-payment) | `{brief, company, email, sales_order}` |
| `payment.received` | Payment Entry submitted against the SO | `{brief, sales_order}` |
| `payment.refunded` | Payment Entry **cancelled/refunded** (kill switch) | `{brief, sales_order, payment_entry}` |
| `project.created` | Kickoff creates the project | `{project, brief, brief_snapshot, start_date}` |
| `project.cancelled` | Project status → Cancelled (kill switch) | `{project, brief}` |
| `phase.changed` | A task moves to Working/Completed | `{project, task, phase, status}` |
| `gate.opened` | A gate task moves to Working | `{project, task, gate, which}` |
| `gate.reminder` | Gate open > nudge threshold (hourly, repeats) | `{project, task, gate, which, waiting_hours}` |
| `gate.decided` | A KNC Gate Decision is recorded | `{project, gate, round, decision, chosen_direction, client_comments}` |
| `refinement.requested` | Gate 2 decision = Refinement Requested | `{project, gate, round, client_comments}` |
| `comment.added` | Client posts to the project thread | `{project, comment_by, content}` |
| `files.delivered` | Final task completed | `{project}` |
| `project.completed` | Final task completed (project closed) | `{project}` |

Notes:
- `which` ∈ `"Gate 1"` / `"Gate 2"` — **key off `which`, not `gate`/subject**
  (subjects are display copy and may be renamed).
- `decision` ∈ `Direction Selected` (Gate 1) / `Approved` · `Refinement Requested` (Gate 2).
  `chosen_direction` is present only for Gate 1.
- `comment.added` **excludes comments authored by the Friday API user** — Friday
  never receives its own `post_project_note`/`update_task_progress` notes back.
  Do not build dedupe for that case; it cannot happen.

### `brief_snapshot` shape
Frozen at payment — the canonical, contract-of-record brief. JSON with:
```
full_name, email, company_name, website_or_social, country, lead_source,
what_you_do, category, stage, target_audience, competitors, differentiator,
naming_status, current_name, name_meaning, brands_admired, avoid,
preferred_start, notes,
personality: [attribute, ...]            // up to 3 KNC Brand Attribute names
references: [{type, file, url, note}, ...] // up to 10 rows
```

---

## 2. Inbound API (Friday → knc)

### Base & auth
```
POST  /api/method/knc.api.v1.<method>
Authorization: token <api_key>:<api_secret>
```
The key belongs to a **User holding the `Friday Integration` role** (least
privilege; all inbound writes are gated on it). Reads use the same auth.

### Methods

| Method | Params | Effect | Rate limit |
|---|---|---|---|
| `update_task_progress` | `task`, `status?`, `note?`, `progress?` | Write-back + heartbeat. `progress` (0–100) alone never touches status. `status` ∈ `Open`/`Working`/`Pending Review`/`Completed`. Returns `{ok, status, progress}`. | 720/hr |
| `attach_deliverable` | `project`, `file_url`, `title?` | Attaches a private File to the project. For binaries, `POST /api/method/upload_file` first, then pass the returned `file_url`. | 120/hr |
| `post_project_note` | `project`, `content` | Posts a `[Friday] …` comment to the project thread. | 120/hr |
| `request_gate_open` | `project`, `gate`, `note?` | **Signal only** — posts a "gate ready" note. Never opens the gate; humans own that. | 30/hr |
| `get_project` | `project` | Full state: project, tasks (incl. `which` gate labels + `progress`), decisions, `brief_snapshot`. Rehydration without event replay. | 600/hr |
| `get_comments` | `project`, `limit?` | Project comment thread, newest first (≤200). | 600/hr |

### Status semantics — `Pending Review` ≠ failed
- `Working` → actively generating.
- `Pending Review` → **generation blocked, needs a human decision**. Use this +
  a `post_project_note` carrying the Friday-side Issue reference. Distinct from a
  failed/errored generation (which Friday handles internally and surfaces as a note).
- `Completed` → done; for a gate task, completion unblocks dependents.

### Heartbeat
Call `update_task_progress(task, progress=N)` during long generations. Status is
untouched unless explicitly passed. The 720/hr limit allows ~one beat / 5s from a
single worker IP — **tell knc your real cadence so the limit can be tuned**
before load testing.

---

## 3. Friday's receiver (their side)

Per Friday's spec, the subscriber URL points at:
```
POST /api/method/frappe.friday_core.surfaces.knc.receive_event
```
which must: verify HMAC → persist the envelope (UUID-unique) → return `200`
immediately → process on Friday's `friday` RQ worker. The `200` must not wait
on an LLM, or knc's retry timer will fire.

---

## 4. Versioning

`version: "v1"`. Within v1, changes are **additive only** (new event types, new
optional fields, new endpoints). Breaking changes bump to `v2` and run in parallel.
This document + `docs/specs/INTEGRATION-SPEC.md` are the source of truth.
