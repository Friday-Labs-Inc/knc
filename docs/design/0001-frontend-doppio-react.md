# ADR 0001 — Frontend: drop Frappe Builder, adopt a Doppio React SPA

**Status:** Accepted · 2026-06-16
**Supersedes:** the "Frappe Builder — marketing pages" row in [STACK.md](../specs/STACK.md); the Friday Labs charter line "Builder = the customer UI." (Both get updated when the removal lands — step 8.)

## The problem

The customer surfaces — marketing site, the `/start` onboarding wizard, and the `/portal` — were going to be **Frappe Builder** pages wired to `knc.api.v1` with pasted client scripts (`builder-kit/`). Looked at closely, three things don't hold up:

1. **Builder pages live in the site database, not git.** A page is Builder blocks stored in the `Builder Page` doctype on whatever site you built it on. That breaks our own operating model — "build in the local repo, deploy + verify on Legion." You can't build a page locally in git and ship it; it gets hand-rebuilt per environment.
2. **Builder can't reach the design bar.** The Creative Director's bar is precise type, one disciplined accent, and motion spec'd to the millisecond. Builder's block model can't express that; an SPA can.
3. **The portal is an app, not a page.** Auth-gated, multi-route, real workflow (gates, refinement rounds, day counters, file delivery). That is a frontend application, not a marketing page.

## The decision

- **Remove Frappe Builder** from the stack.
- **One frontend project** inside the knc app — `frontend/`, scaffolded with **Frappe Doppio**.
- **Stack:** React + **frappe-react-sdk** (Frappe data / auth / session) + a **custom Tailwind design system** for the look (NOT frappe-ui's styled components) + **Framer Motion / Lenis** for motion.
- **Render strategy per surface** (they have opposite needs):
  - **Marketing** (`/`) → **prerendered to static HTML** (SSG at build) — public, SEO- and first-paint-critical.
  - **Onboarding** (`/start`) + **Portal** (`/portal/*`) → **SPA** (portal behind login) — interactive, app-like, SEO-irrelevant.
- **One contract, unchanged.** Every surface calls the existing `knc.api.v1` — the same contract Friday consumes. We add portal-data endpoints only where PORTAL-SPEC needs them (`/brief`, `/files`, `/support`).

## Why React (not Vue / frappe-ui)

React unlocks the exact motion vocabulary the design references use (Framer Motion, Lenis) and keeps **both** brand directions (austere *Draft.* / warm) open — so we can start building before the brand direction is finally locked. `frappe-react-sdk` covers the Frappe data/auth layer that frappe-ui would otherwise provide.

## Consequences

- ✅ The whole frontend is **version-controlled and deployable to Legion** like any code.
- ✅ We can hit the design bar precisely.
- ➖ We lose Builder's WYSIWYG — marketing copy/layout edits now need a dev + rebuild. Acceptable: the precision bar rules out WYSIWYG anyway, the team is dev-driven, and the marketing site changes rarely.
- The **surface-ownership boundary is unchanged** — the customer still only touches knc's surfaces; only the *implementation* of those surfaces changes.

## Removal scope (Builder)

- delete `builder-kit/` (portal.js / wizard.js — the SPA replaces them, same API)
- `install.py`: drop `_builder_pages()` + `STARTER_PAGES`; point `role_home_page` at the SPA portal route
- remove the `builder` app from the bench app list
- update STACK.md, PORTAL-SPEC.md, README.md, HANDOFF.md, and the charter
- **gates:** 40 tests stay green · `bench migrate` clean · `grep -ri builder` (app source) returns zero

## Plan (verify-gated)

1. **Design-lock** (this doc) → verify: reviewed + accepted.
2. **De-risk Doppio on v15** — install Doppio, scaffold a throwaway SPA on knc.localhost, prove it serves + reaches `api/v1`. → verify: a route renders and a guest call (`get_brand_attributes`) returns data.
3. **Scaffold `frontend/`** — routes for `/` (marketing), `/start`, `/portal/*`; build pipeline; website rule. → verify: all three shells render; build emits a bundle.
4. **Design system** — brand tokens + base components (the locked direction). → verify: matches the reference.
5. **Wire onboarding** — `save_step` / `check_capacity` / `submit_brief` → Stripe redirect. → verify: a full wizard run round-trips and reaches checkout.
6. **Wire portal** — `get_project_state` / `decide_gate` / `post_comment` (+ the PORTAL-SPEC routes). → verify: a logged-in customer sees their project, decides a gate, posts a comment.
7. **Marketing prerender** — SSG the `/` routes. → verify: `view-source` shows rendered HTML, not an empty shell.
8. **Remove Builder** (scope above). → verify: gates above.

## Resolved

- **Brand direction — RESOLVED 2026-06-16: the austere *Draft.* language.** `KNC (2).md` (Draft. — Complete Brand & Website Guidelines) is the marketing design system and the inherited base for portal + onboarding (PORTAL-SPEC: "same visual language"). Apply the **SYSTEM only** — tokens, type scale, components, motion rules, voice — to KNC's **real** content and flow. Do NOT carry Draft.'s product specifics (the "$700", the "Google Form" submit, the "Draft." name): the hero input bar submits to the `/start` wizard (`save_step`/`submit_brief` → Stripe), the brand is KNC, price/deliverables reflect KNC's actual package.
- **Consequence for motion:** this language is anti-motion ("stillness is the premium signal"; §12 bans parallax / entrance animation / loops / scale-hover). The Framer Motion budget shrinks to the few allowed micro-transitions (150–200ms color/border, the optional card-grid scroll-reveal). React stays correct — it does austere minimalism cleanly, and the portal may still use light motion.
