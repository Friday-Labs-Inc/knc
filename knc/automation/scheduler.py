"""Scheduled jobs — 24h gate nudges and unpaid-SO auto-close."""

import frappe
from frappe.utils import add_days, add_to_date, now_datetime, nowdate


def nudge_stale_gates():
    """Hourly: gate task Working with no KNC Gate Decision past the nudge
    threshold -> nudge email + visible pause flag on the project."""
    hours = frappe.db.get_single_value("KNC Settings", "gate_nudge_hours") or 24
    stale = frappe.get_all(
        "Task",
        filters={"is_gate": 1, "status": "Working",
                 "modified": ["<", add_to_date(now_datetime(), hours=-hours)]},
        fields=["name", "project", "subject", "modified"],
    )
    from knc.automation.gates import gate_label
    from knc.integrations import outbox

    for task in stale:
        which = gate_label(task.project, task.name)
        if not which:
            continue
        has_decision = frappe.db.exists("KNC Gate Decision", {
            "project": task.project,
            "gate": which,
        })
        if has_decision:
            continue
        brief = frappe.db.get_value(
            "KNC Brief", {"project": task.project}, ["email"], as_dict=True)
        if not brief:
            continue
        outbox.emit("gate.reminder", {
            "project": task.project,
            "task": task.name,
            "gate": task.subject,
            "which": which,
            "waiting_hours": round((now_datetime() - task.modified).total_seconds() / 3600, 1),
        }, "Task", task.name)
        portal_url = frappe.utils.get_url(f"/portal/project/{task.project}")
        try:
            frappe.sendmail(
                recipients=[brief.email],
                subject="KNC — your timeline is paused, waiting on you",
                message=(
                    f"<p>{task.subject} has been open for more than {hours} hours. "
                    "Your ten-day timeline is paused until you decide.</p>"
                    f"<p><a href='{portal_url}'>Decide now</a></p>"
                ),
            )
        except Exception:
            # Email is best-effort: one bad address or a missing outgoing
            # account must not kill reminders for every other project.
            frappe.log_error(frappe.get_traceback(), f"Gate nudge email failed: {task.name}")


def close_unpaid_sales_orders():
    """Daily: Sales Orders from briefs that never paid, past threshold -> Closed."""
    days = frappe.db.get_single_value("KNC Settings", "unpaid_so_autoclose_days") or 7
    cutoff = add_days(nowdate(), -days)
    stale_briefs = frappe.get_all(
        "KNC Brief",
        filters={"status": "Submitted", "submitted_on": ["<", cutoff],
                 "sales_order": ["is", "set"]},
        fields=["name", "sales_order"],
    )
    for brief in stale_briefs:
        so_status = frappe.db.get_value("Sales Order", brief.sales_order, "status")
        if so_status in ("To Deliver and Bill", "To Bill", "To Deliver"):
            advance = frappe.db.get_value("Sales Order", brief.sales_order, "advance_paid")
            if not advance:
                from erpnext.selling.doctype.sales_order.sales_order import update_status
                update_status("Closed", brief.sales_order)
