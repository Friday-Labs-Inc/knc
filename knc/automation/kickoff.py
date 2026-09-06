"""Hook chain B — payment received: the idempotent kickoff chain.

1. Brief -> Paid, freeze brief_snapshot
2. Day-0 Sales Invoice (advance allocated)
3. Project from "Essentials — 10 Day" template anchored to preferred_start
4. Drive folder tree + copy brief uploads
5. Website User + portal invite
6. Brief -> Converted, emit payment.received + project.created

Any step failure is logged and retryable; payment is never stranded.
"""

import frappe
from frappe.utils import add_days, getdate, nowdate

from knc.integrations import outbox

PROJECT_TEMPLATE = "Essentials — 10 Day"

DRIVE_FOLDERS = ["01 Brief", "02 Strategy", "03 Directions", "04 Build", "05 Handoff"]


def on_payment_entry_submit(doc, method=None):
    """doc_events hook on Payment Entry."""
    for ref in doc.references or []:
        if ref.reference_doctype == "Sales Order":
            brief_name = frappe.db.get_value(
                "KNC Brief", {"sales_order": ref.reference_name}, "name")
            if brief_name:
                frappe.enqueue(
                    "knc.automation.kickoff.run_kickoff",
                    queue="default",
                    brief_name=brief_name,
                    payment_entry=doc.name,
                    enqueue_after_commit=True,
                )


def on_payment_entry_cancel(doc, method=None):
    """Kill switch half 1: a refunded/cancelled payment must reach
    subscribers so Friday stops and cancels queued work."""
    for ref in doc.references or []:
        if ref.reference_doctype != "Sales Order":
            continue
        brief = frappe.db.get_value(
            "KNC Brief", {"sales_order": ref.reference_name}, "name")
        if brief:
            outbox.emit("payment.refunded", {
                "brief": brief,
                "sales_order": ref.reference_name,
                "payment_entry": doc.name,
            }, "KNC Brief", brief)


def run_kickoff(brief_name: str, payment_entry: str | None = None):
    brief = frappe.get_doc("KNC Brief", brief_name)

    # Idempotency: a Converted brief with a project is already done.
    if brief.status == "Converted" and brief.project:
        return

    try:
        _step_mark_paid(brief)
        _step_sales_invoice(brief, payment_entry)
        project = _step_project(brief)
        _step_drive_folders(brief, project)
        _step_portal_user(brief, project)
        _step_convert(brief, project)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Kickoff failed: {brief_name}")
        _alert_admin(brief_name)
        raise


def _step_mark_paid(brief):
    if brief.status != "Paid" and brief.status != "Converted":
        brief.db_set("status", "Paid", update_modified=False)
        brief.db_set("paid_on", frappe.utils.now_datetime(), update_modified=False)
        brief.freeze_snapshot()
        outbox.emit("payment.received", {
            "brief": brief.name, "sales_order": brief.sales_order,
        }, "KNC Brief", brief.name)


def _step_sales_invoice(brief, payment_entry):
    """Day-0 invoice against the SO with the advance allocated."""
    if frappe.db.exists("Sales Invoice Item", {"sales_order": brief.sales_order, "docstatus": 1}):
        return
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

    si = make_sales_invoice(brief.sales_order)
    si.allocate_advances_automatically = 1
    si.insert(ignore_permissions=True)
    si.submit()


def ensure_holiday_list() -> str | None:
    """ERPNext refuses to schedule template tasks when the company has no
    default Holiday List — that would strand a paid kickoff. Fall back to
    an empty list so project creation always succeeds."""
    company = frappe.defaults.get_global_default("company")
    if company and frappe.get_cached_value("Company", company, "default_holiday_list"):
        return None  # ERPNext resolves the company default itself

    name = "KNC — No Holidays"
    if not frappe.db.exists("Holiday List", name):
        year = getdate(nowdate()).year
        frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": name,
            "from_date": f"{year}-01-01",
            "to_date": f"{year + 1}-12-31",
        }).insert(ignore_permissions=True)
    return name


def _step_project(brief):
    if brief.project and frappe.db.exists("Project", brief.project):
        return frappe.get_doc("Project", brief.project)

    start = getdate(brief.preferred_start or nowdate())
    project = frappe.get_doc({
        "doctype": "Project",
        "project_name": f"{brief.company_name} — Essentials",
        "project_template": PROJECT_TEMPLATE,
        "expected_start_date": start,
        "expected_end_date": add_days(start, 10),
        "customer": brief.customer,
        "sales_order": brief.sales_order,
        "holiday_list": ensure_holiday_list(),
        "status": "Open",
    })
    project.insert(ignore_permissions=True)
    _copy_template_flags(project)
    brief.db_set("project", project.name, update_modified=False)

    outbox.emit("project.created", {
        "project": project.name,
        "brief": brief.name,
        "brief_snapshot": brief.brief_snapshot,
        "start_date": str(start),
    }, "Project", project.name)
    return project


def _copy_template_flags(project):
    """ERPNext's create_task_from_template copies a fixed field list, so
    the is_gate / client_visible custom fields never reach project tasks
    — without this, no gate ever opens."""
    tasks = frappe.get_all(
        "Task",
        filters={"project": project.name, "template_task": ["is", "set"]},
        fields=["name", "template_task"],
    )
    for task in tasks:
        flags = frappe.db.get_value(
            "Task", task.template_task, ["is_gate", "client_visible"], as_dict=True)
        if flags:
            frappe.db.set_value("Task", task.name, {
                "is_gate": flags.is_gate,
                "client_visible": flags.client_visible,
            }, update_modified=False)


def _drive_folder(team, title, parent=None):
    """Idempotent create_folder: return the existing folder when present."""
    from drive.api.files import create_folder  # type: ignore
    from drive.utils.files import get_home_folder  # type: ignore

    parent = parent or get_home_folder(team).name
    existing = frappe.db.get_value(
        "Drive File",
        {"parent_entity": parent, "title": title, "is_group": 1, "is_active": 1},
        "name",
    )
    if existing:
        return frappe.get_doc("Drive File", existing)
    return create_folder(team, title, parent)


def _step_drive_folders(brief, project):
    """Create the Drive folder tree and copy brief uploads. Best-effort:
    Drive availability must not block the kickoff."""
    try:
        if "drive" not in frappe.get_installed_apps():
            return
        team = frappe.db.get_single_value("KNC Settings", "drive_team")
        if not team:
            return
        root = _drive_folder(team, project.project_name)
        for sub in DRIVE_FOLDERS:
            _drive_folder(team, sub, parent=root.name)
        # Copy brief reference uploads into 01 Brief
        # (left as enhancement: iterate File docs attached to the brief)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Drive folders failed: {project.name}")


def _step_portal_user(brief, project):
    if frappe.db.exists("User", brief.email):
        user = frappe.get_doc("User", brief.email)
    else:
        user = frappe.get_doc({
            "doctype": "User",
            "email": brief.email,
            "first_name": brief.full_name,
            "user_type": "Website User",
            "send_welcome_email": 1,
        })
        user.append_roles("Customer")
        user.insert(ignore_permissions=True)

    # Link user to the customer contact for portal permission queries
    frappe.share.add_docshare(
        "Project", project.name, user.name, read=1, notify=0, flags={"ignore_share_permission": True}
    )


def _step_convert(brief, project):
    brief.db_set("status", "Converted", update_modified=False)


def _alert_admin(brief_name):
    try:
        frappe.sendmail(
            recipients=[frappe.db.get_single_value("System Settings", "support_email")
                        or "hello@knc.studio"],
            subject=f"[KNC] Kickoff failed for {brief_name}",
            message=(
                f"Payment was received but the kickoff chain failed for {brief_name}. "
                "Check Error Log and re-run: "
                f"bench execute knc.automation.kickoff.run_kickoff --kwargs \"{{'brief_name': '{brief_name}'}}\""
            ),
        )
    except Exception:
        pass
