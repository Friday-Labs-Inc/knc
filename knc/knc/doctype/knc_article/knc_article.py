# Copyright (c) 2026, Friday Labs and contributors
# For license information, please see license.txt

"""Article — a Journal post on the marketing site. Studio-managed in the desk
(write, set a cover image, publish); served to the (guest) SPA via
`knc.api.v1.get_articles` (the list) and `get_article` (one post)."""

import re

from frappe.model.document import Document


def slugify(value: str) -> str:
    """URL-safe slug: lowercase, non-alphanumerics to single hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


class KNCArticle(Document):
    def before_validate(self):
        # Keep the slug in step with the title; the SPA routes /journal/<slug>.
        if self.title and not self.slug:
            self.slug = slugify(self.title)
