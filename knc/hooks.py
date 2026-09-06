app_name = "knc"
app_title = "KNC"
app_publisher = "KNC Studio"
app_description = "Onboarding, client portal, gate governance and AI integration seams on ERPNext"
app_email = "hello@knc.studio"  # placeholder — set the studio's real address
app_license = "MIT"

# ------------------------------------------------------------------
# Install
# ------------------------------------------------------------------
after_install = "knc.install.after_install"

# ------------------------------------------------------------------
# Document events — the engine room (HOOKS-TEMPLATE-SPEC.md)
# ------------------------------------------------------------------
doc_events = {
    "Payment Entry": {
        # B. Payment received → idempotent kickoff chain
        "on_submit": "knc.automation.kickoff.on_payment_entry_submit",
        # Kill switch: refund/cancel → payment.refunded event
        "on_cancel": "knc.automation.kickoff.on_payment_entry_cancel",
    },
    "Project": {
        # Kill switch: cancelled engagement → project.cancelled event
        "on_update": "knc.automation.gates.on_project_update",
    },
    "Task": {
        # C. gates only open once their feeding work is complete
        "validate": "knc.automation.gates.validate_gate_open",
        # C. phase.changed / gate.opened events + notifications
        "on_update": "knc.automation.gates.on_task_update",
    },
    "KNC Gate Decision": {
        # C. gate.decided → unblock dependents, recalc delivery
        "after_insert": "knc.automation.gates.on_gate_decision",
    },
    "Comment": {
        # C. comment.added on Projects → portal notification + event
        "after_insert": "knc.integrations.outbox.on_comment_added",
    },
}

# ------------------------------------------------------------------
# Scheduler
# ------------------------------------------------------------------
scheduler_events = {
    "hourly": [
        # Outbox delivery worker (retry pending/failed events)
        "knc.integrations.outbox.deliver_pending",
        # 24h gate nudge + visible pause flag
        "knc.automation.scheduler.nudge_stale_gates",
    ],
    "daily": [
        # Auto-close Sales Orders unpaid past KNC Settings threshold
        "knc.automation.scheduler.close_unpaid_sales_orders",
        # Enforce KNC Integration Settings retention_days on the outbox
        "knc.integrations.outbox.purge_old_events",
    ],
}

# ------------------------------------------------------------------
# Website
# ------------------------------------------------------------------
# All UI lives in Frappe Builder (marketing, /start wizard, portal pages).
# Builder pages call the whitelisted API in knc.api.v1.
# Portal users land on the Builder-built portal page after login.
role_home_page = {"Customer": "portal"}

website_route_rules = [{'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},]