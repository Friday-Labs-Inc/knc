"""Hook chain A — wizard completes (HOOKS-TEMPLATE-SPEC.md).

Brief submitted -> Customer + Contact -> Sales Order -> Payment Request
-> the configured payment gateway's checkout URL (Razorpay) back to the wizard.
"""

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate, now_datetime, nowdate

from knc.integrations import outbox


def close_deal(brief_name: str) -> dict:
    """Called by the wizard's final step. Returns {payment_url, sales_order}."""
    brief = frappe.get_doc("KNC Brief", brief_name)

    if brief.status not in ("Draft", "Submitted"):
        frappe.throw(_("This brief is already {0}.").format(brief.status))

    brief.status = "Submitted"
    brief.submitted_on = now_datetime()
    brief.save(ignore_permissions=True)

    customer = _ensure_customer(brief)
    so = _ensure_sales_order(brief, customer)
    payment_url = _payment_request(so, brief)

    outbox.emit("brief.submitted", {
        "brief": brief.name,
        "company": brief.company_name,
        "email": brief.email,
        "sales_order": so.name,
    }, "KNC Brief", brief.name)

    return {"payment_url": payment_url, "sales_order": so.name, "customer": customer.name}


def _find_existing_customer(brief):
    """Reuse a Customer only when the brief's email already belongs to a
    contact of a customer with the same company name — name alone would
    merge two unrelated clients who happen to share it."""
    if brief.customer and frappe.db.exists("Customer", brief.customer):
        return brief.customer
    contact = frappe.db.get_value("Contact Email", {"email_id": brief.email}, "parent")
    if not contact:
        return None
    linked = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "parent": contact, "link_doctype": "Customer"},
        pluck="link_name",
    )
    for name in linked:
        if frappe.db.get_value("Customer", name, "customer_name") == brief.company_name:
            return name
    return None


def _ensure_customer(brief):
    existing = _find_existing_customer(brief)
    if existing:
        customer = frappe.get_doc("Customer", existing)
    else:
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": brief.company_name,
            "customer_type": "Company",
            "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group")
                or "Commercial",
            "territory": "All Territories",
        }).insert(ignore_permissions=True)

    if not frappe.db.exists("Contact Email", {"email_id": brief.email}):
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": brief.full_name,
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        })
        contact.append("email_ids", {"email_id": brief.email, "is_primary": 1})
        contact.insert(ignore_permissions=True)

    brief.db_set("customer", customer.name, update_modified=False)
    return customer


def _ensure_sales_order(brief, customer):
    if brief.sales_order and frappe.db.exists("Sales Order", brief.sales_order):
        return frappe.get_doc("Sales Order", brief.sales_order)

    settings = frappe.get_cached_doc("KNC Settings")
    start = getdate(brief.preferred_start or nowdate())
    so = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer.name,
        "transaction_date": nowdate(),
        "delivery_date": add_days(start, 10),
        "order_type": "Sales",
        "items": [{
            "item_code": settings.package_item or "RP-ESSENTIALS",
            "qty": 1,
            "rate": flt(settings.package_amount) or 4800,
            "delivery_date": add_days(start, 10),
        }],
    })
    so.insert(ignore_permissions=True)
    so.submit()
    brief.db_set("sales_order", so.name, update_modified=False)
    return so


def _payment_request(so, brief):
    """Native Payments-app flow: Payment Request -> Stripe checkout URL.
    Reuses a live Payment Request on re-submission — make_payment_request
    throws once the SO amount is fully requested, so a retry without this
    guard errors out instead of returning the checkout link."""
    from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

    existing = frappe.db.get_value(
        "Payment Request",
        {"reference_doctype": "Sales Order", "reference_name": so.name,
         "docstatus": 1, "status": ["not in", ["Paid", "Cancelled"]]},
        "name",
    )
    if existing:
        return frappe.get_doc("Payment Request", existing).get_payment_url()

    settings = frappe.get_cached_doc("KNC Settings")
    pr = make_payment_request(
        dt="Sales Order",
        dn=so.name,
        recipient_id=brief.email,
        payment_gateway_account=settings.payment_gateway_account,
        submit_doc=True,
        return_doc=True,
        mute_email=True,
    )
    return pr.get_payment_url()


def validate_start_date(preferred_start: str) -> dict:
    """Capacity check (hook chain D): max_active_projects from KNC Settings."""
    settings = frappe.get_cached_doc("KNC Settings")
    limit = settings.max_active_projects or 4
    active = frappe.db.count("Project", {"status": "Open", "project_template": "Essentials — 10 Day"})
    ok = active < limit
    return {
        "available": ok,
        "active_projects": active,
        "max_active_projects": limit,
        "message": None if ok else _("We are at capacity. The next window opens soon — submit and we will confirm your start date."),
    }
