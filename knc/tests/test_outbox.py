"""Outbox: per-subscriber fan-out, event filtering, envelope schema,
retention purge, and the comment.added guards."""

import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from knc.integrations import outbox

SUBSCRIBER_FIELDS = ("subscriber_name", "url", "secret", "enabled", "events")


class OutboxSettingsMixin:
    """Snapshot and restore KNC Integration Settings around each test."""

    def snapshot_settings(self):
        settings = frappe.get_doc("KNC Integration Settings")
        self._enabled = settings.enabled
        self._subscribers = [
            {k: row.get(k) for k in SUBSCRIBER_FIELDS} for row in (settings.subscribers or [])
        ]
        settings.enabled = 1
        settings.set("subscribers", [])
        settings.save(ignore_permissions=True)

    def restore_settings(self):
        settings = frappe.get_doc("KNC Integration Settings")
        settings.enabled = self._enabled
        settings.set("subscribers", [])
        for row in self._subscribers:
            settings.append("subscribers", row)
        settings.save(ignore_permissions=True)

    def add_subscriber(self, name, events="*"):
        settings = frappe.get_doc("KNC Integration Settings")
        settings.append("subscribers", {
            "subscriber_name": name,
            "url": "http://127.0.0.1:9/hook",
            "enabled": 1,
            "events": events,
        })
        settings.save(ignore_permissions=True)


class TestOutbox(OutboxSettingsMixin, FrappeTestCase):
    def setUp(self):
        self.snapshot_settings()

    def tearDown(self):
        self.restore_settings()
        frappe.db.delete("KNC Event", {"event_type": ["like", "test.%"]})
        frappe.db.commit()

    def test_no_subscribers_records_skipped(self):
        outbox.emit("test.skipped", {"a": 1})
        events = frappe.get_all(
            "KNC Event", filters={"event_type": "test.skipped"}, fields=["status", "subscriber"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].status, "Skipped")
        self.assertFalse(events[0].subscriber)

    def test_emit_fans_out_only_to_matching_subscribers(self):
        self.add_subscriber("alpha")
        self.add_subscriber("beta", events="gate.decided, payment.received")
        outbox.emit("test.fanout", {"a": 1})
        subscribers = frappe.get_all(
            "KNC Event", filters={"event_type": "test.fanout"}, pluck="subscriber")
        self.assertEqual(subscribers, ["alpha"])

    def test_envelope_schema(self):
        self.add_subscriber("alpha")
        outbox.emit("test.envelope", {"k": "v"})
        payload = json.loads(frappe.get_all(
            "KNC Event", filters={"event_type": "test.envelope"}, fields=["payload"])[0].payload)
        for key in ("id", "type", "version", "occurred_at", "data"):
            self.assertIn(key, payload)
        self.assertEqual(payload["type"], "test.envelope")
        self.assertEqual(payload["version"], "v1")
        self.assertEqual(payload["data"], {"k": "v"})

    def test_purge_respects_retention(self):
        def envelope(uid):
            return {"id": uid, "type": "test.purge", "version": "v1",
                    "occurred_at": "now", "data": {}}

        outbox._insert_event("test.purge", envelope("purge-old"), None, None, None,
                             status="Skipped")
        outbox._insert_event("test.purge_keep", envelope("purge-keep"), None, None, None,
                             status="Skipped")
        frappe.db.sql(
            "update `tabKNC Event` set creation = %s where event_type = 'test.purge'",
            add_to_date(now_datetime(), days=-100),
        )

        outbox.purge_old_events()

        self.assertFalse(frappe.db.exists("KNC Event", {"event_type": "test.purge"}))
        self.assertTrue(frappe.db.exists("KNC Event", {"event_type": "test.purge_keep"}))


class TestCommentGuard(OutboxSettingsMixin, FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.friday_user = "friday-guard-test@example.com"
        if not frappe.db.exists("User", cls.friday_user):
            user = frappe.get_doc({
                "doctype": "User",
                "email": cls.friday_user,
                "first_name": "Friday Guard",
                "user_type": "Website User",
                "send_welcome_email": 0,
            })
            user.append_roles("Friday Integration")
            user.insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        frappe.delete_doc("User", cls.friday_user, force=1, ignore_permissions=True)
        frappe.db.commit()
        super().tearDownClass()

    def setUp(self):
        self.snapshot_settings()
        self.project = frappe.get_doc({
            "doctype": "Project",
            "project_name": f"RP Guard {frappe.generate_hash(length=8)}",
            "status": "Open",
        }).insert(ignore_permissions=True)
        self.brief = None

    def tearDown(self):
        frappe.set_user("Administrator")
        self.restore_settings()
        if self.brief:
            frappe.delete_doc("KNC Brief", self.brief.name, force=1,
                              ignore_permissions=True)
        frappe.db.delete("KNC Event", {"reference_name": self.project.name})
        frappe.db.delete("Comment", {"reference_name": self.project.name})
        frappe.delete_doc("Project", self.project.name, force=1, ignore_permissions=True)
        frappe.db.commit()

    def _link_brief(self):
        self.brief = frappe.get_doc({
            "doctype": "KNC Brief",
            "full_name": "Guard Test",
            "email": f"guard-{frappe.generate_hash(length=6)}@example.com",
            "company_name": "Guard Co",
        }).insert(ignore_permissions=True)
        self.brief.db_set("project", self.project.name, update_modified=False)

    def _comment_events(self):
        return frappe.get_all("KNC Event", filters={
            "event_type": "comment.added", "reference_name": self.project.name})

    def test_non_rp_project_comment_is_ignored(self):
        self.project.add_comment("Comment", "internal note")
        self.assertEqual(len(self._comment_events()), 0)

    def test_rp_project_comment_is_emitted(self):
        self._link_brief()
        self.project.add_comment("Comment", "client says hi")
        self.assertEqual(len(self._comment_events()), 1)

    def test_friday_comment_is_not_echoed(self):
        self._link_brief()
        frappe.set_user(self.friday_user)
        try:
            self.project.add_comment("Comment", "[Friday] progress note")
        finally:
            frappe.set_user("Administrator")
        self.assertEqual(len(self._comment_events()), 0)
