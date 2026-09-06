"""Wizard token auth: brief ids are sequential, so the access token
issued at creation must be the only way to touch an existing brief."""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from knc.api.v1 import save_step, submit_brief

STEP1 = {
    "full_name": "Token Test",
    "email": "token-test@example.com",
    "company_name": "Tokentest Co",
}


class TestWizardTokenAuth(FrappeTestCase):
    def setUp(self):
        self.briefs = []

    def tearDown(self):
        for name in self.briefs:
            frappe.delete_doc("KNC Brief", name, force=1, ignore_permissions=True)
        frappe.db.commit()

    def _create_brief(self):
        res = save_step(1, json.dumps(STEP1))
        self.briefs.append(res["brief"])
        return res

    def test_save_step_issues_token(self):
        res = self._create_brief()
        self.assertTrue(res["token"])
        self.assertEqual(
            frappe.db.get_value("KNC Brief", res["brief"], "access_token"),
            res["token"],
        )

    def test_save_step_rejects_missing_token(self):
        res = self._create_brief()
        with self.assertRaises(frappe.PermissionError):
            save_step(2, json.dumps({"what_you_do": "x"}), brief=res["brief"])

    def test_save_step_rejects_wrong_token(self):
        res = self._create_brief()
        with self.assertRaises(frappe.PermissionError):
            save_step(2, json.dumps({"what_you_do": "x"}), brief=res["brief"], token="A" * 32)

    def test_save_step_accepts_correct_token(self):
        res = self._create_brief()
        out = save_step(
            2, json.dumps({"what_you_do": "Designing"}), brief=res["brief"], token=res["token"])
        self.assertEqual(out["brief"], res["brief"])
        self.assertEqual(
            frappe.db.get_value("KNC Brief", res["brief"], "what_you_do"), "Designing")

    def test_submit_brief_rejects_wrong_token(self):
        res = self._create_brief()
        with self.assertRaises(frappe.PermissionError):
            submit_brief(res["brief"], token="B" * 32)
        # And nothing was created downstream
        self.assertEqual(
            frappe.db.get_value("KNC Brief", res["brief"], "status"), "Draft")
