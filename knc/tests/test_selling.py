"""Customer dedup: reuse requires email + company match, never
company name alone."""

import frappe
from frappe.tests.utils import FrappeTestCase

from knc.automation.selling import _find_existing_customer


class TestCustomerDedup(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.email = f"dedup-{frappe.generate_hash(length=6)}@example.com"
        cls.customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": f"Dedup Test Co {frappe.generate_hash(length=6)}",
            "customer_type": "Company",
            "customer_group": frappe.db.get_value("Customer Group", {"is_group": 0}, "name"),
            "territory": "All Territories",
        }).insert(ignore_permissions=True)
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": "Dedup Test",
            "links": [{"link_doctype": "Customer", "link_name": cls.customer.name}],
        })
        contact.append("email_ids", {"email_id": cls.email, "is_primary": 1})
        contact.insert(ignore_permissions=True)
        cls.contact = contact

    @classmethod
    def tearDownClass(cls):
        frappe.delete_doc("Contact", cls.contact.name, force=1, ignore_permissions=True)
        frappe.delete_doc("Customer", cls.customer.name, force=1, ignore_permissions=True)
        frappe.db.commit()
        super().tearDownClass()

    def test_same_email_and_company_reuses_customer(self):
        brief = frappe._dict(
            customer=None, email=self.email, company_name=self.customer.customer_name)
        self.assertEqual(_find_existing_customer(brief), self.customer.name)

    def test_same_company_different_email_does_not_match(self):
        brief = frappe._dict(
            customer=None, email="stranger@example.com",
            company_name=self.customer.customer_name)
        self.assertIsNone(_find_existing_customer(brief))

    def test_same_email_different_company_does_not_match(self):
        brief = frappe._dict(
            customer=None, email=self.email, company_name="A Different Company")
        self.assertIsNone(_find_existing_customer(brief))

    def test_brief_customer_pointer_wins(self):
        brief = frappe._dict(
            customer=self.customer.name, email="other@example.com", company_name="Other Co")
        self.assertEqual(_find_existing_customer(brief), self.customer.name)
