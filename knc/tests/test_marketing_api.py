"""Marketing / content read APIs — the portfolio grid + case study, the journal
list + post, the social-login options, and the wizard's guest endpoints. All
guest-readable; published-only. Inserts are not committed, so FrappeTestCase
rolls them back — no live-site pollution."""

import frappe
from frappe.tests.utils import FrappeTestCase

from knc.api.v1 import (
    check_capacity,
    get_article,
    get_articles,
    get_brand_attributes,
    get_case_study,
    get_login_options,
    get_portfolio,
)


class TestMarketingAPI(FrappeTestCase):
    def _project(self, title, published=1, **kw):
        return frappe.get_doc({
            "doctype": "KNC Portfolio Project",
            "title": title,
            "tag": "Test",
            "description": "A test project.",
            "published": published,
            **kw,
        }).insert(ignore_permissions=True)

    def _article(self, title, published=1, **kw):
        return frappe.get_doc({
            "doctype": "KNC Article",
            "title": title,
            "excerpt": "Test excerpt.",
            "body": "Para one.\n\nPara two.",
            "published": published,
            "published_on": "2026-06-16",
            **kw,
        }).insert(ignore_permissions=True)

    # --- portfolio ---
    def test_get_portfolio_published_only(self):
        pub = self._project("PF Published Test")
        self._project("PF Hidden Test", published=0)
        titles = [p["title"] for p in get_portfolio()]
        self.assertIn(pub.title, titles)
        self.assertNotIn("PF Hidden Test", titles)

    def test_get_case_study_by_slug(self):
        doc = self._project("Case Study Test", client="Acme", challenge="A hard problem.")
        cs = get_case_study(doc.slug)
        self.assertEqual(cs["title"], "Case Study Test")
        self.assertEqual(cs["client"], "Acme")
        self.assertEqual(cs["challenge"], "A hard problem.")

    def test_get_case_study_unpublished_raises(self):
        doc = self._project("CS Hidden Test", published=0)
        with self.assertRaises(frappe.DoesNotExistError):
            get_case_study(doc.slug)

    def test_get_case_study_unknown_slug_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            get_case_study("no-such-slug-xyz")

    # --- journal ---
    def test_get_articles_published_only(self):
        pub = self._article("Article Published Test")
        self._article("Article Hidden Test", published=0)
        slugs = [a["slug"] for a in get_articles()]
        self.assertIn(pub.slug, slugs)
        self.assertNotIn("article-hidden-test", slugs)

    def test_get_article_by_slug_has_body(self):
        doc = self._article("Article With Body Test")
        art = get_article(doc.slug)
        self.assertEqual(art["title"], "Article With Body Test")
        self.assertIn("Para one.", art["body"])

    def test_get_article_unknown_slug_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            get_article("no-such-article-xyz")

    # --- login options + wizard guest endpoints ---
    def test_get_login_options_shape(self):
        out = get_login_options()
        self.assertIn("providers", out)
        self.assertIsInstance(out["providers"], list)

    def test_get_brand_attributes(self):
        attrs = get_brand_attributes()
        self.assertIsInstance(attrs, list)
        self.assertIn("Minimal", attrs)

    def test_check_capacity_shape(self):
        cap = check_capacity()
        self.assertIn("available", cap)
        self.assertIsInstance(cap["available"], bool)
