"""Scheduled tasks for fsms_audit — registered in hooks.scheduler_events."""

import frappe
from frappe.utils import add_days, today


def audit_plan_kickoff_reminder():
	"""Weekly — notify lead auditors when an Audit Plan kickoff is within 7 days."""
	upcoming = frappe.get_all(
		"FSMS Audit Plan",
		filters={"kickoff_meeting_date": ("between", [today(), add_days(today(), 7)])},
		fields=["name", "audit_program"],
	)
	for row in upcoming:
		frappe.publish_realtime(
			event="fsms_audit_kickoff_reminder",
			message={"audit_plan": row.name, "program": row.audit_program},
		)


def year_end_audit_reminder():
	"""Cron Dec 1 — remind FSMS Manager to close out yearly Audit Program."""
	frappe.publish_realtime(
		event="fsms_audit_year_end",
		message={"date": today(), "note": "Year-end audit close-out reminder"},
	)
