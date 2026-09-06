"""Hook chain C — running the engagement (HOOKS-TEMPLATE-SPEC.md).

Task status changes -> phase.changed / gate.opened events.
KNC Gate Decision saved -> unblock dependents, recalc delivery, gate.decided.
"""

import frappe
from frappe.utils import add_days, getdate, nowdate

from knc.integrations import outbox


def gate_tasks(project: str) -> list:
    """Gate tasks of a project in timeline order. Index 0 is Gate 1.
    Identity comes from order, never from the task subject — subjects
    are display copy and may be renamed in the template."""
    return frappe.get_all(
        "Task",
        filters={"project": project, "is_gate": 1},
        fields=["name", "subject", "status"],
        order_by="exp_start_date asc, creation asc",
    )


def gate_label(project: str, task_name: str) -> str | None:
    for i, task in enumerate(gate_tasks(project)):
        if task.name == task_name:
            return f"Gate {i + 1}"
    return None


def _is_final_task(doc) -> bool:
    """The last task on the timeline is the delivery task."""
    tasks = frappe.get_all(
        "Task",
        filters={"project": doc.project},
        order_by="exp_start_date desc, creation desc",
        limit_page_length=1,
        pluck="name",
    )
    return bool(tasks) and tasks[0] == doc.name


def on_project_update(doc, method=None):
    """Kill switch half 2: a cancelled engagement must reach subscribers
    so Friday stops and cancels queued work."""
    if not doc.has_value_changed("status") or doc.status != "Cancelled":
        return
    brief = frappe.db.get_value("KNC Brief", {"project": doc.name}, "name")
    if not brief:
        return
    outbox.emit("project.cancelled", {
        "project": doc.name,
        "brief": brief,
    }, "Project", doc.name)


def validate_gate_open(doc, method=None):
    """A gate may only open (-> Working) once the work feeding it is
    complete — otherwise the client would be deciding on nothing, and
    their decision could not complete the gate task (ERPNext blocks
    completion while dependencies are open)."""
    if not (doc.get("is_gate") and doc.project and doc.status == "Working"):
        return
    if not doc.has_value_changed("status"):
        return
    if not frappe.db.exists("KNC Brief", {"project": doc.project}):
        return
    open_deps = [
        d.task for d in (doc.depends_on or [])
        if frappe.db.get_value("Task", d.task, "status") not in ("Completed", "Cancelled")
    ]
    if open_deps:
        subjects = ", ".join(
            frappe.db.get_value("Task", t, "subject") or t for t in open_deps)
        frappe.throw(frappe._(
            "Cannot open this gate yet — finish first: {0}").format(subjects))


def on_task_update(doc, method=None):
    """doc_events hook on Task — emits phase.changed / gate.opened."""
    if not doc.project:
        return
    if not frappe.db.exists("KNC Brief", {"project": doc.project}):
        return  # not a KNC engagement

    if doc.has_value_changed("status"):
        if doc.status == "Working" and doc.get("is_gate"):
            outbox.emit("gate.opened", {
                "project": doc.project,
                "task": doc.name,
                "gate": doc.subject,
                "which": gate_label(doc.project, doc.name),
            }, "Task", doc.name)
            _notify_client(doc.project, f"A decision gate is open: {doc.subject}",
                           "Review and decide in your portal.")
        elif doc.status in ("Working", "Completed"):
            outbox.emit("phase.changed", {
                "project": doc.project,
                "task": doc.name,
                "phase": doc.subject,
                "status": doc.status,
            }, "Task", doc.name)
            if doc.status == "Completed" and _is_final_task(doc):
                _on_delivered(doc.project)


def on_gate_decision(doc, method=None):
    """doc_events hook on KNC Gate Decision."""
    outbox.emit("gate.decided", {
        "project": doc.project,
        "gate": doc.gate,
        "round": doc.round,
        "decision": doc.decision,
        "chosen_direction": doc.chosen_direction,
        "client_comments": doc.client_comments,
    }, "KNC Gate Decision", doc.name)

    if doc.decision in ("Direction Selected", "Approved"):
        _complete_gate_task(doc)
    elif doc.decision == "Refinement Requested":
        outbox.emit("refinement.requested", {
            "project": doc.project,
            "gate": doc.gate,
            "round": doc.round,
            "client_comments": doc.client_comments,
        }, "KNC Gate Decision", doc.name)
        _extend_delivery(doc)


def _complete_gate_task(decision):
    """Mark the open gate task complete -> ERPNext unblocks dependents.
    Must never fail the KNC Gate Decision insert: the client's decision is
    the business fact; task bookkeeping problems go to the Error Log."""
    gates = gate_tasks(decision.project)
    index = 0 if decision.gate == "Gate 1" else 1
    if index >= len(gates) or gates[index].status == "Completed":
        return
    try:
        t = frappe.get_doc("Task", gates[index].name)
        t.status = "Completed"
        t.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Gate task completion failed: {decision.project} {decision.gate}",
        )


def _extend_delivery(decision):
    """Flexible Gate 2: each refinement round visibly moves delivery.
    Round 1 fits inside the 10 days; rounds 2+ add 2 days each."""
    if decision.gate != "Gate 2" or (decision.round or 1) <= 1:
        return
    project = frappe.get_doc("Project", decision.project)
    new_end = add_days(getdate(project.expected_end_date or nowdate()), 2)
    project.db_set("expected_end_date", new_end)
    _notify_client(
        decision.project,
        "Refinement round confirmed",
        f"Delivery moves to {frappe.utils.formatdate(new_end)} — visible on your timeline.",
    )


def _on_delivered(project_name):
    outbox.emit("files.delivered", {"project": project_name}, "Project", project_name)
    outbox.emit("project.completed", {"project": project_name}, "Project", project_name)
    frappe.db.set_value("Project", project_name, "status", "Completed")
    _notify_client(project_name, "Your brand is delivered",
                   "All files are in your portal under Files.")


def _notify_client(project_name, subject, body):
    """Deep-link email to the portal — never invites a reply."""
    try:
        brief = frappe.db.get_value(
            "KNC Brief", {"project": project_name}, ["email", "full_name"], as_dict=True)
        if not brief:
            return
        portal_url = frappe.utils.get_url(f"/portal/project/{project_name}")
        frappe.sendmail(
            recipients=[brief.email],
            subject=f"KNC — {subject}",
            message=f"<p>{body}</p><p><a href='{portal_url}'>Open your portal</a></p>",
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Client notification failed")
