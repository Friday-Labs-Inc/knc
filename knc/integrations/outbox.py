"""Event outbox — INTEGRATION-SPEC.md.

knc owns the truth and emits facts; Friday consumes facts and
writes back through a guarded, versioned API. Events are persisted
(outbox pattern), delivered with HMAC signatures and exponential
retry, and replayable.
"""

import hashlib
import hmac
import json
import time
import uuid

import frappe
from frappe.utils import add_to_date, now_datetime

EVENT_SCHEMA_VERSION = "v1"


def emit(event_type: str, payload: dict, reference_doctype: str | None = None,
         reference_name: str | None = None):
    """Persist one KNC Event per enabled subscriber. Never raises into
    the calling transaction — event emission must not break business flow."""
    try:
        settings = frappe.get_cached_doc("KNC Integration Settings")
        if not settings.enabled:
            return
        envelope = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "version": EVENT_SCHEMA_VERSION,
            "occurred_at": str(now_datetime()),
            "data": payload,
        }
        subscribers = [s for s in (settings.subscribers or []) if s.enabled]
        if not subscribers:
            _insert_event(event_type, envelope, None, reference_doctype, reference_name, status="Skipped")
            return
        for sub in subscribers:
            wanted = (sub.events or "*").strip()
            if wanted != "*" and event_type not in [e.strip() for e in wanted.split(",")]:
                continue
            _insert_event(event_type, envelope, sub.subscriber_name, reference_doctype, reference_name)
        # Try immediate delivery in the background
        frappe.enqueue("knc.integrations.outbox.deliver_pending", queue="short")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "KNC Event emit failed")


def _insert_event(event_type, envelope, subscriber, ref_dt, ref_dn, status="Pending"):
    frappe.get_doc({
        "doctype": "KNC Event",
        "event_uuid": envelope["id"] if subscriber is None else f"{envelope['id']}:{subscriber}",
        "event_type": event_type,
        "payload": json.dumps(envelope, default=str),
        "status": status,
        "subscriber": subscriber,
        "reference_doctype": ref_dt,
        "reference_name": ref_dn,
    }).insert(ignore_permissions=True)


def deliver_pending():
    """Scheduler + enqueue target: deliver Pending/Failed events with
    exponential backoff (retry n waits 2^n minutes)."""
    settings = frappe.get_cached_doc("KNC Integration Settings")
    if not settings.enabled:
        return
    max_retries = settings.max_retries or 8
    subs = {s.subscriber_name: s for s in (settings.subscribers or []) if s.enabled}

    events = frappe.get_all(
        "KNC Event",
        filters={"status": ["in", ["Pending", "Failed"]], "retry_count": ["<", max_retries]},
        fields=["name", "subscriber", "payload", "retry_count", "modified"],
        order_by="creation asc",
        limit_page_length=50,
    )
    for ev in events:
        sub = subs.get(ev.subscriber)
        if not sub:
            continue
        # Exponential backoff: skip if not yet due
        if ev.retry_count and now_datetime() < add_to_date(ev.modified, minutes=2 ** ev.retry_count):
            continue
        _deliver_one(ev, sub)


def _signature_header(secret: str, body: str) -> str:
    """Stripe-style per-attempt signature: t=<unix>,v1=HMAC(secret, "t.body").
    Signed at send time, not at occurrence time, so a receiver staleness
    window never rejects our backoff retries or manual replays."""
    timestamp = int(time.time())
    digest = hmac.new(secret.encode(), f"{timestamp}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def _deliver_one(ev, sub):
    import requests

    secret = sub.get_password("secret") if sub.secret else ""
    body = ev.payload or "{}"
    signature = _signature_header(secret, body) if secret else ""
    try:
        resp = requests.post(
            sub.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-RP-Signature": signature,
                "X-RP-Event": ev.name,
            },
            timeout=15,
        )
        if resp.ok:
            frappe.db.set_value("KNC Event", ev.name, {
                "status": "Delivered", "delivered_on": now_datetime()})
        else:
            _mark_failed(ev, f"HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        _mark_failed(ev, str(e)[:200])
    frappe.db.commit()


def purge_old_events():
    """Daily: enforce KNC Integration Settings retention_days. Events past
    retention are dead regardless of status — a Pending event that old
    has no subscriber left to deliver to."""
    days = frappe.db.get_single_value("KNC Integration Settings", "retention_days") or 90
    cutoff = add_to_date(now_datetime(), days=-days)
    frappe.db.delete("KNC Event", {"creation": ["<", cutoff]})


def _mark_failed(ev, error):
    frappe.db.set_value("KNC Event", ev.name, {
        "status": "Failed",
        "retry_count": (ev.retry_count or 0) + 1,
        "last_error": error,
    })


# ------------------------------------------------------------------
# Comment hook (comment.added on client-facing Projects)
# ------------------------------------------------------------------
def on_comment_added(doc, method=None):
    if doc.reference_doctype != "Project" or doc.comment_type != "Comment":
        return
    if not frappe.db.exists("KNC Brief", {"project": doc.reference_name}):
        return  # not a KNC engagement
    # Explicit Has Role lookup: frappe.get_roles() reports every role for
    # Administrator, which would swallow admin comments too.
    if frappe.db.exists(
        "Has Role", {"parenttype": "User", "parent": doc.owner, "role": "Friday Integration"}
    ):
        return  # don't echo Friday's own writes back to subscribers
    emit(
        "comment.added",
        {
            "project": doc.reference_name,
            "comment_by": doc.owner,
            "content": doc.content,
        },
        "Project",
        doc.reference_name,
    )
