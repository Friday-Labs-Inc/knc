# knc — a mis-named copy of the RandomPack product (Frappe v15 + ERPNext)

**Status: ARCHIVED.** RandomPack is the product (`Friday-Labs-Inc/randompack`, Frappe v16); Klick N Click
is a *customer* of it, not a codebase. This copy exists only because the product was briefly renamed after
the customer. Its v15 business chain is ported into the product under epic E1 there; nothing else is used.
Do not start new features here. Bug fixes only if a live site depends on them.

## What is here (read it, then port it)
- `knc/automation/{selling,kickoff,gates,scheduler}.py` — the business chain: wizard → Customer → Sales Order → Payment
  Request; payment → idempotent kickoff; gate tasks + KNC Gate Decision; nudges and unpaid auto-close.
- `knc/api/v1.py` — guest wizard (token + rate limits), portal, Friday-inbound endpoints.
- `knc/integrations/outbox.py` + `KNC Event` — the HMAC webhook outbox. **Dead under topology A; do not extend.**
- `docs/specs/*.md`, `docs/CONTRACT.md` — the locked June 2026 specs; still the best description of the model.
- `frontend/` — the Doppio/React portal SPA.

## Dev loop
- Dev container `~/knc-dev` (`up.sh`), site `knc.localhost`, MariaDB 11.8, ERPNext setup wizard already run.
- `bench --site knc.localhost run-tests --app knc` (6 modules, 50 tests).

## Rules
- Conventional commits, PR template, a human merges. Same definition of done as randompack.
- Anything ported to randompack gets a note in the porting issue and is deleted here in the same PR series.
