# Builder Kit — wiring Builder pages to the knc API

All UI lives in Frappe Builder. These client scripts connect your
Builder pages to the `knc` backend. Paste each script into the
page's **Client Script** in Builder (Settings → Script), and bind your
blocks to the element IDs noted below.

| Builder page | Route | Script | Access |
|---|---|---|---|
| Start wizard | /start | `wizard.js` | Public |
| Portal — project | /portal | `portal.js` | Protected Page (login required) |

## Wizard page (/start)

Design 6 step containers + a review step in Builder, give them IDs
`knc-step-1` … `knc-step-6`, `knc-review`. Buttons: `knc-next`, `knc-prev`,
`knc-pay`. Inputs: `data-knc-field="<fieldname>"` attribute on each
input/textarea/select (fieldnames from ONBOARDING-BRIEF-SPEC.md).
`wizard.js` handles step switching, per-step auto-save
(`knc.api.v1.save_step`), capacity check, and the final
`submit_brief` call which redirects to Stripe checkout.

## Portal page (/portal)

Mark the page **Protected** in Builder. Design blocks with IDs:
`knc-timeline`, `knc-phase`, `knc-gate`, `knc-decisions`, `knc-comments`.
`portal.js` calls `knc.api.v1.get_project_state` on load and
renders into those blocks; gate buttons call `decide_gate`; the
comment box calls `post_comment`.

## Files page

Simplest: a Builder page with a button linking to the project's
Frappe Drive folder (the share link is posted to the project comment
thread at kickoff).

## Notes

- Builder Data Scripts can also fetch `get_project_state` server-side
  if you prefer rendering with bindings instead of client JS.
- The same API namespace (`knc.api.v1`) is what Friday uses —
  one contract, two consumers.
