# Copyright (c) 2026, Friday Labs and contributors
# For license information, please see license.txt

"""KNC Portfolio Project — one piece of work shown in the marketing site's Work section,
and (with the case-study fields filled) the expressive /work/<slug> page.

Studio-managed content: add, reorder, publish, upload images, and write the
case study in the Frappe desk; no frontend rebuild needed. Served to the (guest)
SPA via `knc.api.v1.get_portfolio` (the grid) and `get_case_study` (one).
"""

import re

from frappe.model.document import Document


def slugify(value: str) -> str:
    """URL-safe slug: lowercase, non-alphanumerics to single hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


class KNCPortfolioProject(Document):
    def before_validate(self):
        # Keep the slug in step with the title; the SPA routes /work/<slug>.
        if self.title and not self.slug:
            self.slug = slugify(self.title)
