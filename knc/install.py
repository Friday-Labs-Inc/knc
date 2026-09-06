"""after_install seeding — everything M0/M1 needs, automated.

Seeds: custom fields, Friday Integration role, RP-ESSENTIALS item +
price, Selling Settings, 12 KNC Brand Attributes, the "Essentials — 10 Day"
Project Template (7 tasks, gates flagged), KNC Settings defaults, and
starter Builder marketing pages (only when missing — never overwrites
pages you already built).
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

BRAND_ATTRIBUTES = [
    "Bold", "Minimal", "Warm", "Technical", "Playful", "Premium",
    "Trustworthy", "Edgy", "Calm", "Energetic", "Classic", "Futuristic",
]

TEMPLATE_TASKS = [
    # (subject, begin day, duration days, is_gate)
    ("Intake review", 0, 1, 0),
    ("Strategy & naming", 1, 3, 0),
    ("Three directions", 4, 2, 0),
    ("Gate 1 — choose direction", 5, 1, 1),
    ("Build system", 6, 4, 0),
    ("Gate 2 — final review", 9, 1, 1),
    ("Delivery & handoff", 10, 1, 0),
]

PROJECT_TEMPLATE = "Essentials — 10 Day"


# Selected work for the marketing site's Work section. Seeded as KNC Portfolio Project records; the studio edits and
# reorders these in the desk, and the SPA reads them via api.v1.get_portfolio.
# Images get uploaded later in the desk. (title, tag, description)
PORTFOLIO: list[tuple[str, str, str]] = []  # seed the studio's own work here (title, tag, description)


def backfill_portfolio_slugs():
    """One-off: set the slug on KNC Portfolio Projects seeded before that field
    existed. Re-saving triggers the controller's slug derivation. Idempotent."""
    for name in frappe.get_all("KNC Portfolio Project", pluck="name"):
        if not frappe.db.get_value("KNC Portfolio Project", name, "slug"):
            frappe.get_doc("KNC Portfolio Project", name).save(ignore_permissions=True)
    frappe.db.commit()


def setup_razorpay_gateway():
    """One-off (idempotent): wire the Razorpay gateway after the keys are saved in
    Razorpay Settings. Ensures a Payment Gateway Account (INR) and points RP
    Settings at it. Never touches the API secret — that lives in Razorpay Settings.
    Returns a status dict for diagnosis."""
    if not frappe.db.exists("Payment Gateway", "Razorpay"):
        return {"ok": False, "error": "No 'Razorpay' Payment Gateway yet — enable + save Razorpay Settings first."}

    company = frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")
    payment_account = (
        frappe.db.get_value(
            "Account",
            {"company": company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0},
            "name",
        )
        if company
        else None
    )

    pga = frappe.db.get_value("Payment Gateway Account", {"payment_gateway": "Razorpay"}, "name")
    if not pga:
        doc = frappe.get_doc({
            "doctype": "Payment Gateway Account",
            "payment_gateway": "Razorpay",
            "currency": "INR",
            "payment_account": payment_account,
            "is_default": 1,
        })
        doc.flags.ignore_mandatory = not payment_account
        doc.insert(ignore_permissions=True)
        pga = doc.name

    frappe.db.set_single_value("KNC Settings", "payment_gateway_account", pga)
    frappe.db.commit()
    return {
        "ok": True,
        "gateway_account": pga,
        "payment_account": payment_account,
        "company": company,
        "company_currency": frappe.db.get_value("Company", company, "default_currency") if company else None,
    }


# Journal seed — a few on-brand posts so /journal is never empty. The studio
# writes real ones in the desk (Article doctype). (title, category, excerpt, body, published_on)
ARTICLES: list[tuple[str, str, str, str, str]] = []  # (title, category, excerpt, body, published_on)


def _articles():
    """Seed the Journal. Idempotent — keyed by title; never overwrites a post
    you've edited in the desk."""
    for title, category, excerpt, body, published_on in ARTICLES:
        if frappe.db.exists("KNC Article", title):
            continue
        frappe.get_doc({
            "doctype": "KNC Article",
            "title": title,
            "category": category,
            "excerpt": excerpt,
            "body": body,
            "author": "KNC",
            "published": 1,
            "published_on": published_on,
        }).insert(ignore_permissions=True)


def after_install():
    _custom_fields()
    _friday_role()
    _package_item()
    _selling_settings()
    _brand_attributes()
    _portfolio()
    _articles()
    _project_template()
    _rp_settings()
    _integration_settings()
    _builder_pages()
    frappe.db.commit()
    print("✓ KNC seeded: item, template, attributes, custom fields, settings")


def _custom_fields():
    fields = {
        "Task": [
            {"fieldname": "is_gate", "fieldtype": "Check", "label": "Is Decision Gate",
             "insert_after": "is_milestone", "default": "0"},
            {"fieldname": "client_visible", "fieldtype": "Check", "label": "Client Visible",
             "insert_after": "is_gate", "default": "1"},
        ],
    }
    if "helpdesk" in frappe.get_installed_apps():
        fields["HD Ticket"] = [
            {"fieldname": "project", "fieldtype": "Link", "label": "Project",
             "options": "Project", "insert_after": "customer"},
        ]
    create_custom_fields(fields, ignore_validate=True)


def _friday_role():
    if not frappe.db.exists("Role", "Friday Integration"):
        frappe.get_doc({
            "doctype": "Role", "role_name": "Friday Integration",
            "desk_access": 0,
        }).insert(ignore_permissions=True)


def _package_item():
    if not frappe.db.exists("Item", "RP-ESSENTIALS"):
        frappe.get_doc({
            "doctype": "Item",
            "item_code": "RP-ESSENTIALS",
            "item_name": "Essentials — brand identity in ten days",
            "item_group": frappe.db.get_value("Item Group", {"is_group": 0}, "name") or "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "include_item_in_manufacturing": 0,
            "description": "Positioning and naming territory, three directions, "
                           "logo suite, colour/type/core system, guidelines and source files.",
        }).insert(ignore_permissions=True)

    price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list") \
        or "Standard Selling"
    if not frappe.db.exists("Item Price", {"item_code": "RP-ESSENTIALS", "price_list": price_list}):
        frappe.get_doc({
            "doctype": "Item Price",
            "item_code": "RP-ESSENTIALS",
            "price_list": price_list,
            "price_list_rate": 4800,
        }).insert(ignore_permissions=True)


def _selling_settings():
    # Services: no Delivery Note in the chain
    frappe.db.set_single_value("Selling Settings", "dn_required", "No")
    frappe.db.set_single_value("Selling Settings", "so_required", "No")


def _brand_attributes():
    for attr in BRAND_ATTRIBUTES:
        if not frappe.db.exists("KNC Brand Attribute", attr):
            frappe.get_doc({"doctype": "KNC Brand Attribute", "attribute_name": attr})\
                .insert(ignore_permissions=True)


def _portfolio():
    """Seed the marketing Work section. Idempotent — keyed by title, so it never
    overwrites a project you've edited, re-ordered, or added an image to in the desk."""
    for order, (title, tag, description) in enumerate(PORTFOLIO):
        if frappe.db.exists("KNC Portfolio Project", title):
            continue
        frappe.get_doc({
            "doctype": "KNC Portfolio Project",
            "title": title,
            "tag": tag,
            "description": description,
            "display_order": order,
            "published": 1,
        }).insert(ignore_permissions=True)


def _project_template():
    if not frappe.db.exists("Project Template", PROJECT_TEMPLATE):
        template = frappe.get_doc({
            "doctype": "Project Template",
            "name": PROJECT_TEMPLATE,
            "project_type": frappe.db.get_value("Project Type", {}, "name") or "External",
        })
        for subject, begin, duration, is_gate in TEMPLATE_TASKS:
            task = frappe.get_doc({
                "doctype": "Task",
                "subject": subject,
                "is_template": 1,
                "start": begin,
                "duration": duration,
                "is_gate": is_gate,
                "client_visible": 1,
            }).insert(ignore_permissions=True)
            template.append("tasks", {"task": task.name, "subject": subject})
        template.insert(ignore_permissions=True)
    _template_dependencies()


def _template_dependencies():
    """Each template task depends on the previous one (HOOKS-TEMPLATE-SPEC):
    Build is blocked until Gate 1 is decided, Delivery until Gate 2 approves.
    ERPNext maps these onto project tasks at creation and refuses to complete
    a task whose dependencies are open. Idempotent — existing installs pick
    up the chain on re-seed."""
    template = frappe.get_doc("Project Template", PROJECT_TEMPLATE)
    previous = None
    for row in template.tasks:
        if previous:
            task = frappe.get_doc("Task", row.task)
            if not any(d.task == previous for d in (task.depends_on or [])):
                task.append("depends_on", {"task": previous})
                task.save(ignore_permissions=True)
        previous = row.task


def _integration_settings():
    """An unsaved Single reads as enabled=None, which emit() treats as
    disabled — events would be silently dropped until someone saves the
    doc by hand. Seed it so the outbox records from day one."""
    settings = frappe.get_doc("KNC Integration Settings")
    if settings.enabled is None:
        settings.enabled = 1
    settings.max_retries = settings.max_retries or 8
    settings.retention_days = settings.retention_days or 90
    settings.save(ignore_permissions=True)


def _rp_settings():
    settings = frappe.get_doc("KNC Settings")
    settings.max_active_projects = settings.max_active_projects or 4
    settings.unpaid_so_autoclose_days = settings.unpaid_so_autoclose_days or 7
    settings.gate_nudge_hours = settings.gate_nudge_hours or 24
    settings.package_item = "RP-ESSENTIALS"
    settings.package_amount = settings.package_amount or 4800
    settings.save(ignore_permissions=True)


# ------------------------------------------------------------------
# Starter Builder pages — created ONLY when the route does not exist.
# Your live pages are never touched.
# ------------------------------------------------------------------

STARTER_PAGES = {
    "home": "KNC — AI-assisted branding",
    "how-it-works": "How it works — KNC",
    "work": "Work — KNC",
    "pricing": "Pricing — KNC",
}


def _builder_pages():
    if "builder" not in frappe.get_installed_apps():
        return
    try:
        for route, title in STARTER_PAGES.items():
            if frappe.db.exists("Builder Page", {"route": route}):
                continue
            frappe.get_doc({
                "doctype": "Builder Page",
                "page_title": title,
                "route": route,
                "published": 0,  # drafts — design them in Builder
                "blocks": frappe.as_json([_starter_block(title)]),
            }).insert(ignore_permissions=True)
    except Exception:
        # Builder schema differences must never fail the install
        frappe.log_error(frappe.get_traceback(), "Builder starter pages skipped")


def _starter_block(title):
    return {
        "element": "section",
        "baseStyles": {"display": "flex", "flexDirection": "column",
                       "alignItems": "center", "padding": "96px 40px"},
        "children": [{
            "element": "h1",
            "innerHTML": title,
            "baseStyles": {"fontSize": "48px", "fontWeight": "300"},
        }],
    }
