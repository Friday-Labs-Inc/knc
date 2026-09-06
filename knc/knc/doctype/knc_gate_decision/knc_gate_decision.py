import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

VALID_DECISIONS = {
    "Gate 1": ("Direction Selected",),
    "Gate 2": ("Approved", "Refinement Requested"),
}


class KNCGateDecision(Document):
    def validate(self):
        if self.decision not in VALID_DECISIONS.get(self.gate, ()):
            frappe.throw(_("{0} does not allow the decision: {1}").format(self.gate, self.decision))
        if self.gate == "Gate 1" and not self.chosen_direction:
            frappe.throw(_("Gate 1 requires a chosen direction."))

    def before_insert(self):
        self.decided_by = frappe.session.user
        self.decided_on = now_datetime()
        # Round = number of prior decisions on the same gate + 1
        prior = frappe.db.count(
            "KNC Gate Decision", {"project": self.project, "gate": self.gate}
        )
        self.round = prior + 1
