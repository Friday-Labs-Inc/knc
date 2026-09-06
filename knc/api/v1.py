"""knc API v1 — the single contract for Builder pages (wizard +
portal) and for Friday (inbound writes). INTEGRATION-SPEC.md.

Builder client/data scripts call these with frappe.call();
Friday authenticates with an API key user holding the
"Friday Integration" role.
"""

import hmac
import json

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, now_datetime

from knc.automation.gates import gate_label

# ------------------------------------------------------------------
# Wizard (guest-accessible: the visitor is not logged in yet)
# ------------------------------------------------------------------

WIZARD_FIELDS = {
    1: ["full_name", "email", "company_name", "website_or_social", "country", "lead_source"],
    2: ["what_you_do", "category", "stage", "existing_brand_assets"],
    3: ["target_audience", "competitors", "differentiator"],
    4: ["naming_status", "current_name", "name_meaning"],
    5: ["brands_admired", "avoid"],  # personality + references via dedicated params
    6: ["preferred_start", "gate_commitment", "terms_accepted", "notes"],
}


def _check_brief_token(doc, token: str | None):
    """Brief ids are sequential and the wizard runs as Guest, so the
    token issued at creation is the only proof of ownership."""
    if not token or not hmac.compare_digest(doc.access_token or "", token):
        frappe.throw(_("Not permitted"), frappe.PermissionError)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60 * 60)
def save_step(step: int, data: str, brief: str | None = None, token: str | None = None):
    """Auto-save one wizard step. Creates the Draft brief on step 1.
    Returns {brief, token} so the Builder page keeps both in localStorage."""
    step = int(step)
    if step not in WIZARD_FIELDS:
        frappe.throw(_("Invalid step"))
    values = json.loads(data) if isinstance(data, str) else data

    if brief and frappe.db.exists("KNC Brief", brief):
        doc = frappe.get_doc("KNC Brief", brief)
        _check_brief_token(doc, token)
        if doc.status not in ("Draft",):
            frappe.throw(_("This brief is already submitted."))
    else:
        doc = frappe.new_doc("KNC Brief")

    for field in WIZARD_FIELDS[step]:
        if field in values:
            doc.set(field, values[field])

    # Step 5 extras
    if step == 5:
        if "personality" in values:
            doc.set("personality", [])
            for attr in (values["personality"] or [])[:3]:
                doc.append("personality", {"brand_attribute": attr})
        if "references" in values:
            doc.set("references", [])
            for ref in (values["references"] or [])[:10]:
                doc.append("references", {
                    "reference_type": ref.get("type", "URL"),
                    "url": ref.get("url"),
                    "file": ref.get("file"),
                    "note": ref.get("note"),
                })

    doc.wizard_step = max(doc.wizard_step or 1, step)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"brief": doc.name, "token": doc.access_token, "step": step}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60 * 60)
def check_capacity():
    """Slot availability for the wizard's start-date step."""
    from knc.automation.selling import validate_start_date
    return validate_start_date(None)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def submit_brief(brief: str, token: str | None = None):
    """Final wizard step: validate, create Customer/SO/Payment Request,
    return the Stripe checkout URL to redirect to."""
    from knc.automation.selling import close_deal
    doc = frappe.get_doc("KNC Brief", brief)
    _check_brief_token(doc, token)
    result = close_deal(brief)
    frappe.db.commit()
    return result


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=60, seconds=60 * 60)
def get_brand_attributes():
    return [d.name for d in frappe.get_all("KNC Brand Attribute")]


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=600, seconds=60 * 60)
def get_portfolio():
    """Published work for the marketing site's Work section, in display order.
    Studio-managed via the KNC Portfolio Project doctype (edit/reorder/publish in
    the desk, no rebuild). Public read — names + an optional image only."""
    return frappe.get_all(
        "KNC Portfolio Project",
        filters={"published": 1},
        fields=["title", "tag", "description", "image"],
        order_by="display_order asc, title asc",
    )


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=600, seconds=60 * 60)
def get_case_study(slug: str):
    """One published project's full case study, by slug — for /work/<slug>."""
    name = frappe.db.get_value("KNC Portfolio Project", {"slug": slug, "published": 1}, "name")
    if not name:
        frappe.throw(_("Not found"), frappe.DoesNotExistError)
    return frappe.db.get_value(
        "KNC Portfolio Project",
        name,
        ["title", "tag", "description", "image", "client", "year", "hero_image",
         "challenge", "approach", "outcome", "body"],
        as_dict=True,
    )


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=600, seconds=60 * 60)
def get_articles():
    """Published Journal posts, newest first (no body — list view)."""
    return frappe.get_all(
        "KNC Article",
        filters={"published": 1},
        fields=["title", "slug", "excerpt", "cover_image", "author", "category", "published_on"],
        order_by="published_on desc, creation desc",
    )


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=600, seconds=60 * 60)
def get_article(slug: str):
    """One published Journal post by slug — for /journal/<slug>."""
    name = frappe.db.get_value("KNC Article", {"slug": slug, "published": 1}, "name")
    if not name:
        frappe.throw(_("Not found"), frappe.DoesNotExistError)
    return frappe.db.get_value(
        "KNC Article",
        name,
        ["title", "slug", "excerpt", "cover_image", "author", "category", "published_on", "body"],
        as_dict=True,
    )


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=120, seconds=60 * 60)
def get_login_options(redirect_to: str = "/frontend/portal"):
    """Enabled social-login providers + their authorize URLs, so the SPA can
    render native "Continue with X" buttons. Frappe's OAuth handles the flow and
    maps the login onto the existing customer by email (User docname = email).
    Returns nothing until a Social Login Key is configured + enabled."""
    from frappe.utils.oauth import get_oauth2_authorize_url

    providers = []
    for key in frappe.get_all(
        "Social Login Key", filters={"enable_social_login": 1}, fields=["name", "provider_name"]
    ):
        try:
            providers.append(
                {"name": key.name, "label": key.provider_name, "url": get_oauth2_authorize_url(key.name, redirect_to)}
            )
        except Exception:
            continue  # a misconfigured key never breaks the login page
    return {"providers": providers}


# ------------------------------------------------------------------
# Portal (logged-in customer; the customer-facing SPA)
# ------------------------------------------------------------------

def _get_customer_projects():
    """Projects shared with the logged-in portal user."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in."), frappe.PermissionError)
    shared = frappe.share.get_shared("Project", frappe.session.user)
    return shared or []


@frappe.whitelist()
@rate_limit(limit=120, seconds=60 * 60)
def get_project_state(project: str | None = None):
    """Everything a portal page needs in one call: timeline, phase,
    open gate, decisions, brief snapshot, day counter + pause flag."""
    projects = _get_customer_projects()
    if not projects:
        return {"projects": []}
    if not project:
        project = projects[0]
    if project not in projects and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    p = frappe.get_doc("Project", project)
    tasks = frappe.get_all(
        "Task",
        filters={"project": project},
        fields=["name", "subject", "status", "exp_start_date", "exp_end_date",
                "is_gate", "client_visible"],
        order_by="exp_start_date asc, creation asc",
    )
    decisions = frappe.get_all(
        "KNC Gate Decision",
        filters={"project": project},
        fields=["gate", "round", "decision", "chosen_direction", "client_comments", "decided_on"],
        order_by="decided_on asc",
    )
    brief = frappe.db.get_value(
        "KNC Brief", {"project": project},
        ["name", "brief_snapshot", "company_name"], as_dict=True)

    open_gate = next((t for t in tasks if t.is_gate and t.status == "Working"), None)
    waiting_hours = 0
    if open_gate:
        modified = frappe.db.get_value("Task", open_gate.name, "modified")
        waiting_hours = (now_datetime() - modified).total_seconds() / 3600

    return {
        "projects": projects,
        "project": {
            "name": p.name,
            "title": p.project_name,
            "status": p.status,
            "start": str(p.expected_start_date or ""),
            "end": str(p.expected_end_date or ""),
            "percent_complete": p.percent_complete,
        },
        "tasks": [t for t in tasks if t.client_visible or t.is_gate],
        "gate": {
            "open": bool(open_gate),
            "task": open_gate.subject if open_gate else None,
            "which": gate_label(project, open_gate.name) if open_gate else None,
            "paused": waiting_hours > (frappe.db.get_single_value("KNC Settings", "gate_nudge_hours") or 24),
        },
        "decisions": decisions,
        "brief": brief,
    }


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=20, seconds=60 * 60)
def decide_gate(project: str, gate: str, decision: str,
                chosen_direction: str | None = None, comments: str | None = None):
    """Portal gate action -> KNC Gate Decision (hooks handle the rest)."""
    if project not in _get_customer_projects():
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    if gate not in ("Gate 1", "Gate 2"):
        frappe.throw(_("Invalid gate"))
    if decision not in ("Direction Selected", "Approved", "Refinement Requested"):
        frappe.throw(_("Invalid decision"))

    brief = frappe.db.get_value("KNC Brief", {"project": project}, "name")
    doc = frappe.get_doc({
        "doctype": "KNC Gate Decision",
        "project": project,
        "brief": brief,
        "gate": gate,
        "decision": decision,
        "chosen_direction": chosen_direction,
        "client_comments": comments,
    }).insert(ignore_permissions=True)
    frappe.db.commit()
    return {"gate_decision": doc.name, "round": doc.round}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60 * 60)
def post_comment(project: str, content: str):
    """Portal comment thread — the single async channel."""
    if project not in _get_customer_projects():
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    frappe.get_doc("Project", project).add_comment("Comment", content)
    frappe.db.commit()
    return {"ok": True}


# ------------------------------------------------------------------
# Friday inbound (role: Friday Integration)
# ------------------------------------------------------------------

def _require_friday():
    if "Friday Integration" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not permitted"), frappe.PermissionError)


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=720, seconds=60 * 60)
def update_task_progress(task: str, status: str | None = None, note: str | None = None,
                         progress: int | None = None):
    """Friday write-back + heartbeat. `progress` alone never touches
    status (heartbeat-safe); status changes only when passed explicitly.
    "Pending Review" = generation blocked, needs a human decision —
    distinct from failed."""
    _require_friday()
    doc = frappe.get_doc("Task", task)
    if status is not None:
        if status not in ("Open", "Working", "Pending Review", "Completed"):
            frappe.throw(_("Invalid status"))
        doc.status = status
    if progress is not None:
        doc.progress = min(max(cint(progress), 0), 100)
    doc.save(ignore_permissions=True)
    if note:
        doc.add_comment("Comment", f"[Friday] {note}")
    return {"ok": True, "status": doc.status, "progress": doc.progress}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=120, seconds=60 * 60)
def attach_deliverable(project: str, file_url: str, title: str | None = None):
    _require_friday()
    frappe.get_doc({
        "doctype": "File",
        "file_url": file_url,
        "file_name": title or file_url.rsplit("/", 1)[-1],
        "attached_to_doctype": "Project",
        "attached_to_name": project,
        "is_private": 1,
    }).insert(ignore_permissions=True)
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=120, seconds=60 * 60)
def post_project_note(project: str, content: str):
    _require_friday()
    frappe.get_doc("Project", project).add_comment("Comment", f"[Friday] {content}")
    return {"ok": True}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60 * 60)
def request_gate_open(project: str, gate: str, note: str | None = None):
    """Friday signals a gate's deliverables are ready. Signal only —
    humans own the gate; this never touches task status."""
    _require_friday()
    if gate not in ("Gate 1", "Gate 2"):
        frappe.throw(_("Invalid gate"))
    if not frappe.db.exists("KNC Brief", {"project": project}):
        frappe.throw(_("Not a KNC engagement"))
    message = f"[Friday] {gate} ready to open." + (f" {note}" if note else "")
    frappe.get_doc("Project", project).add_comment("Comment", message)
    return {"ok": True}


@frappe.whitelist()
@rate_limit(limit=600, seconds=60 * 60)
def get_project(project: str):
    """Friday rehydration: full engagement state without event replay."""
    _require_friday()
    brief = frappe.db.get_value(
        "KNC Brief", {"project": project},
        ["name", "status", "brief_snapshot", "company_name", "sales_order"], as_dict=True)
    if not brief:
        frappe.throw(_("Not a KNC engagement"))
    p = frappe.get_doc("Project", project)
    tasks = frappe.get_all(
        "Task",
        filters={"project": project},
        fields=["name", "subject", "status", "progress", "exp_start_date", "exp_end_date",
                "is_gate", "client_visible"],
        order_by="exp_start_date asc, creation asc",
    )
    for t in tasks:
        if t.is_gate:
            t["which"] = gate_label(project, t.name)
    decisions = frappe.get_all(
        "KNC Gate Decision",
        filters={"project": project},
        fields=["name", "gate", "round", "decision", "chosen_direction",
                "client_comments", "decided_on"],
        order_by="decided_on asc",
    )
    return {
        "project": {
            "name": p.name,
            "title": p.project_name,
            "status": p.status,
            "start": str(p.expected_start_date or ""),
            "end": str(p.expected_end_date or ""),
            "percent_complete": p.percent_complete,
        },
        "tasks": tasks,
        "decisions": decisions,
        "brief": brief,
    }


@frappe.whitelist()
@rate_limit(limit=600, seconds=60 * 60)
def get_comments(project: str, limit: int = 50):
    """Friday rehydration: the project's async channel, newest first."""
    _require_friday()
    if not frappe.db.exists("KNC Brief", {"project": project}):
        frappe.throw(_("Not a KNC engagement"))
    return frappe.get_all(
        "Comment",
        filters={"reference_doctype": "Project", "reference_name": project,
                 "comment_type": "Comment"},
        fields=["name", "owner", "content", "creation"],
        order_by="creation desc",
        limit_page_length=min(cint(limit) or 50, 200),
    )
