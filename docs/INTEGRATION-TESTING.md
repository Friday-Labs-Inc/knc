# End-to-End Integration Testing — knc ⇄ Friday

How to bring up both systems on one machine (e.g. a Legion 5 Pro) and prove the
full loop: client journey → events out to Friday → Friday writes back.

> Read [CONTRACT.md](CONTRACT.md) first — it defines every message on the wire.

---

## 0. Topology — why two benches

**knc is Frappe v15. Friday is a Frappe v16 fork. They cannot share a
bench** (a bench is pinned to one Frappe major version). On one machine you run
**two independent benches** that talk over HTTP on localhost:

```
┌─ Bench A · Frappe v15 ───────────┐        ┌─ Bench B · Frappe v16 fork ──────┐
│ site: knc.localhost:8000  │        │ site: friday.localhost:8001      │
│ apps: frappe, erpnext, payments, │        │ apps: frappe(v16 fork),          │
│   telephony, helpdesk, builder,  │  HTTP  │   friday_core                    │
│   drive, knc              │ ◀────▶ │                                  │
│ DB: MariaDB · Redis (own ports)  │        │ DB: Postgres · Redis (own ports) │
└──────────────────────────────────┘        └──────────────────────────────────┘
        │  webhook: events                            ▲
        └──── POST http://127.0.0.1:8001/api/method/frappe.friday_core.surfaces.knc.receive_event
        ▲                                             │
        └──── REST: http://127.0.0.1:8000/api/method/knc.api.v1.*  ◀── Friday writes back
```

Two benches → two Redis instances on **distinct ports** and two web ports. Set
them per bench with `bench set-redis-*-host` / the Procfile, and run each on its
own port (`bench serve --port 8000` / `--port 8001`, or set `webserver_port` in
`sites/common_site_config.json`).

---

## 1. Prerequisites (Legion 5 / Linux)

```
Python 3.10–3.12   Node 18+   Yarn   Redis   MariaDB (bench A)   Postgres (bench B)
wkhtmltopdf (0.12.6, patched-qt)   libmagic1  (Drive needs it)
```
> Bench path must be **space-free** — bench splits commands on whitespace.
> `scripts/bench-setup.sh` (macOS-tuned) is the reference for the exact app
> branches; on Linux adjust `PY` and use the steps below.

---

## 2. Bench A — knc (the v15 stack)

From a clean clone of this repo, or adapt `scripts/bench-setup.sh`:

```bash
# 1. init the v15 bench
bench init knc-bench --frappe-branch version-15 --python python3.11
cd knc-bench

# 2. fetch the stack (branches that bench-setup.sh pins)
bench get-app erpnext   --branch version-15
bench get-app payments  --branch version-15
bench get-app telephony                       # ships 'develop' only
bench get-app builder   --branch master
bench get-app helpdesk  --branch main
bench get-app drive     --branch main

# 3. fetch knc FROM GITHUB (Legion 5 has no local symlink source)
bench get-app https://github.com/rsvasanth/knc.git

# 4. site + install
bench new-site knc.localhost --admin-password admin --db-root-password <pw>
for app in erpnext payments telephony helpdesk builder drive knc; do
  bench --site knc.localhost install-app $app
done
# (run the ERPNext setup wizard before installing knc if Company is missing —
#  see bench-setup.sh step 5; knc's seed needs Item Groups / UOMs / Price Lists)

bench --site knc.localhost migrate
bench --site knc.localhost set-config allow_tests true
```

### 2a. Verify the app in isolation first
```bash
redis-server config/redis_cache.conf --daemonize yes
redis-server config/redis_queue.conf --daemonize yes
bench --site knc.localhost run-tests --app knc     # expect: OK (40 tests)
```
If those 40 pass, knc's own logic is sound; any later failure is wiring.

### 2b. Configure Stripe test mode (unblocks the whole front of the pipeline)
The payment path has **never run without this** — it's the trigger for
`payment.received` / `project.created`.
1. Payments app → **Stripe Settings** (test keys).
2. Create a **Payment Gateway Account** for Stripe.
3. **KNC Settings → Payment Gateway Account** → select it.

---

## 3. Bench B — Friday

Bring up per Friday's own runbook (Frappe v16 fork + `friday_core`, Postgres,
dedicated `friday` worker). Ensure the `receive_event` surface is installed and
the site serves on `:8001`.

---

## 4. Wire the two sides

1. **On knc — create the Friday API user**
   ```
   New User: friday@integration.local  (System User or Website User)
   → add role "Friday Integration"
   → Settings → API Access → Generate Keys  → copy api_key + api_secret
   ```
2. **On knc — add Friday as a subscriber**
   `KNC Integration Settings` → Subscribers → add row:
   | field | value |
   |---|---|
   | subscriber_name | `friday` |
   | url | `http://127.0.0.1:8001/api/method/frappe.friday_core.surfaces.knc.receive_event` |
   | secret | `<shared secret S>` (also store on Friday) |
   | events | `*` (or a comma list) |
   | enabled | ✓ |

   And ensure `KNC Integration Settings.enabled = 1`.
3. **On Friday** — store: shared secret `S`; knc base URL
   `http://127.0.0.1:8000`; the `api_key:api_secret` for inbound calls.

---

## 5. Handshake test (smallest loop — do this before the full journey)

### 5a. knc → Friday (one signed event)
On bench A:
```bash
bench --site knc.localhost console
>>> from knc.integrations import outbox
>>> outbox.emit("phase.changed", {"project": "PING", "task": "T", "phase": "Handshake", "status": "Working"})
>>> # worker delivers; check status:
>>> import frappe; frappe.get_all("KNC Event", filters={"event_type":"phase.changed"}, fields=["status","last_error"], order_by="creation desc", limit_page_length=1)
```
Expect the row to reach **`Delivered`**. On Friday, confirm one persisted event
row with a **verified** signature. If `Failed`: see Troubleshooting.

### 5b. Friday → knc (one inbound call)
From bench B (or curl):
```bash
curl -s http://127.0.0.1:8000/api/method/knc.api.v1.get_project \
  -H "Authorization: token <api_key>:<api_secret>" \
  --data-urlencode "project=<a real RP project>"
```
Expect `200` with project/tasks/brief. A `403` means the role/token is wrong.

---

## 6. Full journey rehearsal

Drive a real engagement and watch each event land on Friday.

| Step (knc) | Action | Event(s) emitted | Friday should |
|---|---|---|---|
| 1 | `/start` wizard, 6 steps, submit | `brief.submitted` | run a completeness check |
| 2 | Pay with Stripe test card `4242 4242 4242 4242` | `payment.received`, then kickoff → `project.created` | ingest `brief_snapshot`, plan tasks, start strategy + 3 directions |
| 3 | Team completes intake→directions; opens Gate 1 | `phase.changed`×, `gate.opened` (`which: Gate 1`) | verify directions attached; post gate summary |
| 4 | Client picks a direction in portal | `gate.decided` (`decision: Direction Selected`) | start build-out lane |
| 5 | (If gate sits >24h) | `gate.reminder` hourly | reprioritize / chase |
| 6 | Build → Gate 2 → client requests changes | `gate.opened` (Gate 2), `refinement.requested` | generate revision drafts |
| 7 | Client approves; final task completes | `gate.decided` (Approved), `files.delivered`, `project.completed` | close tasks, write retrospective memory |
| — | Friday writes progress throughout | (inbound) | `update_task_progress` (+`progress`), `attach_deliverable`, `post_project_note` |
| — | Refund / cancel path | `payment.refunded` / `project.cancelled` | **stop & cancel queued work** |

Re-run a kickoff if a step fails:
```bash
bench --site knc.localhost execute knc.automation.kickoff.run_kickoff \
  --kwargs "{'brief_name': 'KNC-BRIEF-0001'}"
```

---

## 7. Acceptance criteria

- [ ] knc 40-test suite green on Legion 5.
- [ ] Handshake 5a: a signed event reaches Friday and verifies (no signature error).
- [ ] Handshake 5b: a Friday-authenticated inbound call returns `200`.
- [ ] Stripe test payment fires `payment.received` + `project.created` automatically.
- [ ] Each journey step emits the expected event(s) (table §6).
- [ ] Friday write-backs appear in the portal (`update_task_progress`, notes, files).
- [ ] `project.cancelled` / `payment.refunded` reach Friday and halt its work.
- [ ] A duplicate / replayed event `id` is a no-op on Friday (idempotency).

---

## 8. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Event stuck `Pending` | Outbox worker not running — start Redis + `bench worker` / `bench start`; `deliver_pending` runs hourly + on-emit enqueue. |
| Event `Failed`, `last_error` HTTP 0/timeout | Friday URL/port wrong, or `200` is waiting on the LLM (it must ack immediately, process async). |
| **Signature mismatch on Friday** | Verifying over a re-serialized body. HMAC the **raw received bytes** as `f"{t}." + raw_body`, not `json.dumps(parsed)`. Most common failure. |
| Inbound `403 PermissionError` | Token user lacks `Friday Integration` role, or `Authorization: token key:secret` malformed. |
| Inbound `417`/rate-limited | Exceeded the per-method hourly limit (CONTRACT §2). Heartbeats: confirm cadence vs the 720/hr `update_task_progress` limit. |
| No `payment.received` after paying | Stripe Gateway Account not set in KNC Settings, or Payment Entry not submitted against the SO. |
| Two benches clash on Redis/port | Give each bench distinct Redis ports + web port (`common_site_config.json`). |
