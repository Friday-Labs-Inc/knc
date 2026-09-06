# KNC Brief — DocType & Wizard Spec

Locked: 2026-06-11 · Custom doctype in `knc` app · naming series `KNC-BRIEF-.####`

## Wizard: 6 steps + review/pay. Every step auto-saves (Draft = warm lead).

### Step 1 — You
| Field | Type | Rules |
|---|---|---|
| full_name | Data | required |
| email | Data (email) | required; becomes portal user |
| company_name | Data | required |
| website_or_social | Data | optional |
| country | Link (Country) | drives currency/tax |
| lead_source | Select | "How did you hear about us" — CRM analytics |

### Step 2 — The business
| Field | Type | Rules |
|---|---|---|
| what_you_do | Small Text | required — "explain it like you'd tell a friend" |
| category | Select | SaaS / Fintech / D2C / Skincare / Media / Agency / Other |
| stage | Select | Idea / Pre-launch / Launched / Rebranding |
| existing_brand_assets | Attach (multiple) | shown only when stage = Rebranding |

### Step 3 — Audience & edge
| Field | Type | Rules |
|---|---|---|
| target_audience | Small Text | who buys, who decides |
| competitors | Small Text | 2–3 names or links |
| differentiator | Small Text | required |

### Step 4 — Naming (only scope variable in the package)
| Field | Type | Rules |
|---|---|---|
| naming_status | Select | Name is locked / Open to exploring / Need a name — drives Strategy phase |
| current_name | Data | hidden when "Need a name" |
| name_meaning | Small Text | optional |

### Step 5 — Taste & tone
| Field | Type | Rules |
|---|---|---|
| personality | Table MultiSelect → KNC Brand Attribute | pick exactly 3 (~12 options) |
| brands_admired | Small Text | 2–3 brands and why |
| avoid | Small Text | colors, styles, clichés to avoid |
| references | Child table: KNC Brief Reference | per row: file upload OR URL + note. jpg/png/pdf/svg/zip, 25 MB/file, max 10 rows |

### Step 6 — Logistics & commitment
| Field | Type | Rules |
|---|---|---|
| preferred_start | Date | validated against open slots |
| gate_commitment | Check | required — "I'll respond within 24h at the two gates" |
| terms_accepted | Check | required |
| notes | Small Text | optional |

## System fields (not in wizard)
status (Draft → Submitted → Paid → Converted) · links: customer, sales_order, project (set by hooks) · submitted_on · paid_on · brief_snapshot (JSON frozen at payment — contract-of-record)

## Decisions
- No budget/timeline questions — price and timeline are fixed and stated
- No phone/WhatsApp — email is login + notifications only
- All follow-ups through the customer portal (comments, gates, Helpdesk tickets); notification emails deep-link to portal, no-reply sender
- Brief uploads are copied to the project's Drive folder at kickoff
