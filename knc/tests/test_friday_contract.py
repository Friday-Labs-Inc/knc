"""Design-60 integration contract: per-attempt signatures, kill-switch
events, gate reminders, heartbeat write-back, and Friday read/signal
endpoints."""

import hashlib
import hmac

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from knc.api.v1 import (
    get_comments,
    get_project,
    request_gate_open,
    update_task_progress,
)
from knc.automation.gates import gate_tasks
from knc.automation.kickoff import on_payment_entry_cancel
from knc.automation.scheduler import nudge_stale_gates
from knc.integrations.outbox import _signature_header
from knc.tests.test_gates import (
    complete_in_order,
    delete_project,
    make_bare_project,
    make_engagement,
)


class TestSignatureHeader(FrappeTestCase):
    def test_per_attempt_signature_verifies(self):
        secret, body = "s3cret-key", '{"id": "abc", "data": {"k": "v"}}'
        header = _signature_header(secret, body)

        parts = dict(p.split("=", 1) for p in header.split(","))
        self.assertIn("t", parts)
        self.assertIn("v1", parts)
        expected = hmac.new(
            secret.encode(), f"{parts['t']}.{body}".encode(), hashlib.sha256).hexdigest()
        self.assertEqual(parts["v1"], expected)


class TestFridayContract(FrappeTestCase):
    def setUp(self):
        self.project, self.brief = make_engagement()

    def tearDown(self):
        frappe.db.delete("KNC Event", {"reference_name": self.brief.name})
        frappe.db.delete("KNC Gate Decision", {"project": self.project.name})
        frappe.delete_doc("KNC Brief", self.brief.name, force=1, ignore_permissions=True)
        delete_project(self.project.name)
        frappe.db.commit()

    # -- kill-switch events -------------------------------------------

    def test_project_cancelled_emits_event(self):
        p = frappe.get_doc("Project", self.project.name)
        p.status = "Cancelled"
        p.save(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("KNC Event", {
            "event_type": "project.cancelled", "reference_name": self.project.name}))

    def test_payment_cancel_emits_refund_event(self):
        self.brief.db_set("sales_order", "TEST-SO-REFUND", update_modified=False)
        on_payment_entry_cancel(frappe._dict(
            name="TEST-PE-REFUND",
            references=[frappe._dict(
                reference_doctype="Sales Order", reference_name="TEST-SO-REFUND")],
        ))
        self.assertTrue(frappe.db.exists("KNC Event", {
            "event_type": "payment.refunded", "reference_name": self.brief.name}))

    # -- gate.reminder ------------------------------------------------

    def test_stale_gate_emits_reminder(self):
        complete_in_order(self.project.name, stop_before="Gate 1")
        gate1 = frappe.get_doc("Task", gate_tasks(self.project.name)[0].name)
        gate1.status = "Working"
        gate1.save(ignore_permissions=True)
        frappe.db.sql(
            "update `tabTask` set modified = %s where name = %s",
            (add_to_date(now_datetime(), hours=-30), gate1.name),
        )

        nudge_stale_gates()

        self.assertTrue(frappe.db.exists("KNC Event", {
            "event_type": "gate.reminder", "reference_name": gate1.name}))

    # -- heartbeat write-back -----------------------------------------

    def test_progress_heartbeat_does_not_touch_status(self):
        task = gate_tasks(self.project.name)[0]
        before = frappe.db.get_value("Task", task.name, "status")
        out = update_task_progress(task.name, progress=40)
        self.assertEqual(out["progress"], 40)
        self.assertEqual(frappe.db.get_value("Task", task.name, "status"), before)

    def test_pending_review_status_accepted(self):
        task = frappe.db.get_value(
            "Task", {"project": self.project.name, "is_gate": 0}, "name")
        out = update_task_progress(task, status="Pending Review", note="needs a human")
        self.assertEqual(out["status"], "Pending Review")

    def test_invalid_status_rejected(self):
        task = gate_tasks(self.project.name)[0]
        with self.assertRaises(frappe.ValidationError):
            update_task_progress(task.name, status="Blocked")

    # -- request_gate_open --------------------------------------------

    def test_request_gate_open_is_signal_only(self):
        gate1 = gate_tasks(self.project.name)[0]
        before = frappe.db.get_value("Task", gate1.name, "status")
        request_gate_open(self.project.name, "Gate 1", note="directions attached")
        self.assertEqual(frappe.db.get_value("Task", gate1.name, "status"), before)
        comments = frappe.get_all("Comment", filters={
            "reference_doctype": "Project", "reference_name": self.project.name,
            "comment_type": "Comment"}, pluck="content")
        self.assertTrue(any("Gate 1 ready to open" in (c or "") for c in comments))

    def test_request_gate_open_rejects_non_rp_project(self):
        bare = make_bare_project()
        try:
            with self.assertRaises(frappe.ValidationError):
                request_gate_open(bare.name, "Gate 1")
        finally:
            delete_project(bare.name)

    # -- read endpoints -----------------------------------------------

    def test_get_project_returns_full_state(self):
        state = get_project(self.project.name)
        self.assertEqual(state["brief"]["name"], self.brief.name)
        self.assertEqual(len(state["tasks"]), 7)
        labels = [t.get("which") for t in state["tasks"] if t.is_gate]
        self.assertEqual(labels, ["Gate 1", "Gate 2"])
        self.assertEqual(state["decisions"], [])

    def test_get_comments_returns_thread(self):
        frappe.get_doc("Project", self.project.name).add_comment("Comment", "hello thread")
        comments = get_comments(self.project.name)
        self.assertTrue(any("hello thread" in (c.content or "") for c in comments))

    def test_get_project_rejects_non_rp_project(self):
        bare = make_bare_project()
        try:
            with self.assertRaises(frappe.ValidationError):
                get_project(bare.name)
        finally:
            delete_project(bare.name)
