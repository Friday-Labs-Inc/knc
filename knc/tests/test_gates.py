"""Gate flow: decision pairing, round counting, order-based gate
identity, template flag copying, and the engagement events."""

import json

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate

from knc.automation.gates import gate_label, gate_tasks
from knc.automation.kickoff import (
    PROJECT_TEMPLATE,
    _copy_template_flags,
    ensure_holiday_list,
)
from knc.install import _template_dependencies


def make_bare_project():
    return frappe.get_doc({
        "doctype": "Project",
        "project_name": f"RP Bare {frappe.generate_hash(length=8)}",
        "status": "Open",
    }).insert(ignore_permissions=True)


def make_templated_project():
    return frappe.get_doc({
        "doctype": "Project",
        "project_name": f"RP Tmpl {frappe.generate_hash(length=8)}",
        "project_template": PROJECT_TEMPLATE,
        "expected_start_date": nowdate(),
        "holiday_list": ensure_holiday_list(),
        "status": "Open",
    }).insert(ignore_permissions=True)


def delete_project(name):
    task_names = frappe.get_all("Task", filters={"project": name}, pluck="name")
    frappe.db.delete("KNC Event", {"reference_name": ["in", task_names + [name]]})
    frappe.db.delete("Comment", {"reference_name": name})
    frappe.db.delete("Task Depends On", {"parent": ["in", task_names]})
    frappe.db.delete("Task", {"project": name})
    frappe.delete_doc("Project", name, force=1, ignore_permissions=True)


def make_engagement():
    """A templated project linked to a brief — a KNC engagement."""
    project = make_templated_project()
    _copy_template_flags(project)
    brief = frappe.get_doc({
        "doctype": "KNC Brief",
        "full_name": "Events Test",
        "email": f"events-{frappe.generate_hash(length=6)}@example.com",
        "company_name": "Events Co",
    }).insert(ignore_permissions=True)
    brief.db_set("project", project.name, update_modified=False)
    return project, brief


def complete_in_order(project_name, stop_before=None):
    """Complete tasks in timeline order, stopping before the task whose
    subject contains stop_before — dependencies require this order."""
    tasks = frappe.get_all(
        "Task", filters={"project": project_name},
        fields=["name", "subject"],
        order_by="exp_start_date asc, creation asc",
    )
    for t in tasks:
        if stop_before and stop_before in t.subject:
            return
        doc = frappe.get_doc("Task", t.name)
        if doc.status != "Completed":
            doc.status = "Completed"
            doc.save(ignore_permissions=True)


class TestKNCGateDecisionValidation(FrappeTestCase):
    def setUp(self):
        self.project = make_bare_project()

    def tearDown(self):
        frappe.db.delete("KNC Gate Decision", {"project": self.project.name})
        delete_project(self.project.name)
        frappe.db.commit()

    def _decision(self, **kwargs):
        return frappe.get_doc({"doctype": "KNC Gate Decision", "project": self.project.name, **kwargs})

    def test_gate1_rejects_approved(self):
        with self.assertRaises(frappe.ValidationError):
            self._decision(gate="Gate 1", decision="Approved").insert(ignore_permissions=True)

    def test_gate1_requires_chosen_direction(self):
        with self.assertRaises(frappe.ValidationError):
            self._decision(gate="Gate 1", decision="Direction Selected").insert(
                ignore_permissions=True)

    def test_gate2_rejects_direction_selected(self):
        with self.assertRaises(frappe.ValidationError):
            self._decision(
                gate="Gate 2", decision="Direction Selected", chosen_direction="A"
            ).insert(ignore_permissions=True)

    def test_round_increments_per_gate(self):
        first = self._decision(
            gate="Gate 1", decision="Direction Selected", chosen_direction="A"
        ).insert(ignore_permissions=True)
        second = self._decision(
            gate="Gate 1", decision="Direction Selected", chosen_direction="B"
        ).insert(ignore_permissions=True)
        self.assertEqual(first.round, 1)
        self.assertEqual(second.round, 2)

    def test_refinement_requested_event_emitted(self):
        decision = self._decision(
            gate="Gate 2", decision="Refinement Requested", client_comments="rounder"
        ).insert(ignore_permissions=True)
        events = frappe.get_all(
            "KNC Event",
            filters={"event_type": "refinement.requested", "reference_name": decision.name},
            fields=["payload"],
        )
        self.assertEqual(len(events), 1)
        data = json.loads(events[0].payload)["data"]
        self.assertEqual(data["gate"], "Gate 2")
        self.assertEqual(data["client_comments"], "rounder")
        frappe.db.delete("KNC Event", {"reference_name": decision.name})


class TestTemplateFlags(FrappeTestCase):
    def setUp(self):
        self.project = make_templated_project()

    def tearDown(self):
        delete_project(self.project.name)
        frappe.db.commit()

    def test_erpnext_drops_flags_and_copy_restores_them(self):
        self.assertEqual(frappe.db.count("Task", {"project": self.project.name}), 7)
        # ERPNext's create_task_from_template copies a fixed field list,
        # so custom flags are lost on the raw copy.
        self.assertEqual(
            frappe.db.count("Task", {"project": self.project.name, "is_gate": 1}), 0)

        _copy_template_flags(self.project)

        gates = gate_tasks(self.project.name)
        self.assertEqual(len(gates), 2)
        self.assertEqual(gate_label(self.project.name, gates[0].name), "Gate 1")
        self.assertEqual(gate_label(self.project.name, gates[1].name), "Gate 2")
        self.assertEqual(
            frappe.db.count("Task", {"project": self.project.name, "client_visible": 1}), 7)


class TestEngagementEvents(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _template_dependencies()

    def setUp(self):
        self.project, self.brief = make_engagement()

    def tearDown(self):
        frappe.delete_doc("KNC Brief", self.brief.name, force=1, ignore_permissions=True)
        delete_project(self.project.name)
        frappe.db.commit()

    def test_gate_opened_event_carries_order_based_label(self):
        complete_in_order(self.project.name, stop_before="Gate 1")
        gates = gate_tasks(self.project.name)
        task = frappe.get_doc("Task", gates[0].name)
        task.status = "Working"
        task.save(ignore_permissions=True)

        events = frappe.get_all(
            "KNC Event",
            filters={"event_type": "gate.opened", "reference_name": task.name},
            fields=["payload"],
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(json.loads(events[0].payload)["data"]["which"], "Gate 1")

    def test_final_task_completion_delivers_project(self):
        complete_in_order(self.project.name)

        for event_type in ("files.delivered", "project.completed"):
            self.assertTrue(
                frappe.db.exists("KNC Event", {
                    "event_type": event_type, "reference_name": self.project.name}),
                f"missing {event_type}",
            )
        self.assertEqual(
            frappe.db.get_value("Project", self.project.name, "status"), "Completed")


class TestDependencyChain(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _template_dependencies()  # older sites may predate the chain

    def setUp(self):
        self.project, self.brief = make_engagement()

    def tearDown(self):
        frappe.delete_doc("KNC Brief", self.brief.name, force=1, ignore_permissions=True)
        frappe.db.delete("KNC Gate Decision", {"project": self.project.name})
        delete_project(self.project.name)
        frappe.db.commit()

    def _task_by_subject(self, fragment):
        name = frappe.db.get_value(
            "Task", {"project": self.project.name, "subject": ["like", f"%{fragment}%"]}, "name")
        return frappe.get_doc("Task", name)

    def test_project_tasks_inherit_template_chain(self):
        tasks = frappe.get_all(
            "Task", filters={"project": self.project.name},
            fields=["name"], order_by="exp_start_date asc, creation asc")
        for prev, curr in zip(tasks, tasks[1:]):
            deps = frappe.get_all(
                "Task Depends On", filters={"parent": curr.name}, pluck="task")
            self.assertIn(prev.name, deps)

    def test_build_cannot_complete_before_gate1_decided(self):
        complete_in_order(self.project.name, stop_before="Gate 1")
        build = self._task_by_subject("Build system")
        build.status = "Completed"
        with self.assertRaises(frappe.ValidationError):
            build.save(ignore_permissions=True)

    def test_gate_cannot_open_before_feeding_work_done(self):
        gate1 = self._task_by_subject("Gate 1")
        gate1.status = "Working"
        with self.assertRaises(frappe.ValidationError):
            gate1.save(ignore_permissions=True)

    def test_client_decision_completes_gate_and_unblocks_build(self):
        complete_in_order(self.project.name, stop_before="Gate 1")
        gate1 = self._task_by_subject("Gate 1")
        gate1.status = "Working"
        gate1.save(ignore_permissions=True)  # allowed: directions are done

        frappe.get_doc({
            "doctype": "KNC Gate Decision",
            "project": self.project.name,
            "gate": "Gate 1",
            "decision": "Direction Selected",
            "chosen_direction": "B",
        }).insert(ignore_permissions=True)

        self.assertEqual(
            frappe.db.get_value("Task", gate1.name, "status"), "Completed")
        build = self._task_by_subject("Build system")
        build.status = "Completed"
        build.save(ignore_permissions=True)  # no longer blocked
