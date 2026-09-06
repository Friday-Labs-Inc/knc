# KNC — Locked Launch Stack

Locked: 2026-06-11 · One Frappe Cloud private bench · one site · one database · one login

## Apps (7)

| # | App | Role |
|---|-----|------|
| 1 | Frappe Framework v15 | Platform, users, portal, email |
| 2 | ERPNext v15 | Customer, Sales Order, Payment Entry, Sales Invoice, Project/Tasks, CRM, accounting |
| 3 | Frappe Builder | Marketing pages (live at knc.studio) |
| 4 | Payments | Stripe gateway + Payment Request |
| 5 | Frappe Helpdesk | Customer support — agent inbox, SLA, knowledge base, ticket portal |
| 6 | Frappe Drive | Client file delivery — per-project folders, day-10 handoff package |
| 7 | knc (custom) | KNC Brief, KNC Gate Decision, /start wizard, portal pages, hooks, AI webhook seams |

## Document flow

```
KNC Brief (custom) → Customer → Sales Order → Payment Request → Stripe
                                            ↓ on payment
        Payment Entry + Project (from "Essentials — 10 Day" template) + Sales Invoice (day 0)
                                            ↓
              Portal invite · Drive project folder · Friday webhook (Phase 2)
```

## Key decisions

- No Quotation, no Delivery Note — fixed-price service, wizard goes straight to Sales Order
- Sales Invoice raised day 0 against payment (client gets paid invoice at checkout)
- Gates = Tasks with customer-approval flag; KNC Gate Decision doctype records choice, comments, timestamp
- Helpdesk and Drive are core at launch (not deferred)
- HD Ticket gets custom Project link field (mid-engagement tickets tie to engagement)
- Phase 2 AI (Friday) connects only via webhooks fired on project creation and gate approvals — no AI code in Phase 1
- Optional later: Frappe Insights (BI dashboards)
