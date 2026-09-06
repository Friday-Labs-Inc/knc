# Friday Integration Layer — Spec

Locked: 2026-06-11 · Event-driven seam in `knc` app · Friday stays external and swappable

## Principle
knc owns the truth and emits facts; Friday consumes facts and writes back through a guarded, versioned API.

## 1. Event bus
Structured events for every business moment:
`brief.submitted` · `payment.received` · `project.created` · `phase.changed` · `gate.opened` · `gate.decided` · `refinement.requested` · `comment.added` · `files.delivered` · `project.completed`

## 2. Outbox pattern — KNC Event doctype
Fields: event UUID, type, JSON payload, status (pending/delivered/failed), retry count, subscriber, timestamps.
Background job delivers with HMAC-signed requests + exponential retry. Events are replayable (rehydrate Friday from history).

## 3. Inbound API (Friday → knc)
`/api/method/knc.api.v1.*` — update task progress, attach draft deliverables, post comments, drop files to Drive folder, request gate open.
Auth: dedicated API-key user with scoped "Friday Integration" role. Least privilege, full audit trail.

## 4. Contracts
Fixed, versioned JSON schemas per event (v1). `brief_snapshot` = canonical brief format. Friday's internals (n8n / agent SDK / other) can change without touching knc.

## 5. KNC Integration Settings doctype
Subscriber URL(s), shared secret, enabled events, retry policy. New consumers (Slack, analytics) = a settings row, not a deploy.

## 6. Idempotency
Event UUIDs for dedupe; inbound endpoints safe to retry. No duplicate projects or double-fired gates.
