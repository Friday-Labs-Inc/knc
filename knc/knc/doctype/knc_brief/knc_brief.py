import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address


class KNCBrief(Document):
    def before_insert(self):
        # Capability token for the anonymous wizard session: brief names are
        # sequential, so possession of this token is the only ownership proof.
        self.access_token = frappe.generate_hash(length=32)

    def validate(self):
        if self.email:
            validate_email_address(self.email, throw=True)
        if self.status == "Submitted":
            self._validate_complete()

    def _validate_complete(self):
        """A brief may only reach Submitted when the wizard is complete."""
        required = {
            "full_name": _("Full name"),
            "email": _("Email"),
            "company_name": _("Company name"),
            "what_you_do": _("What you do"),
            "differentiator": _("Differentiator"),
            "naming_status": _("Naming status"),
        }
        missing = [label for field, label in required.items() if not self.get(field)]
        if missing:
            frappe.throw(_("Incomplete brief, missing: {0}").format(", ".join(missing)))
        if not self.gate_commitment:
            frappe.throw(_("The 24h gate commitment must be accepted."))
        if not self.terms_accepted:
            frappe.throw(_("Terms must be accepted."))
        if self.personality and len(self.personality) > 3:
            frappe.throw(_("Pick at most 3 personality attributes."))

    def freeze_snapshot(self):
        """Contract-of-record: frozen copy of the brief at payment."""
        data = self.as_dict(no_default_fields=True)
        data["personality"] = [p.brand_attribute for p in (self.personality or [])]
        data["references"] = [
            {"type": r.reference_type, "file": r.file, "url": r.url, "note": r.note}
            for r in (self.references or [])
        ]
        self.db_set("brief_snapshot", frappe.as_json(data), update_modified=False)
