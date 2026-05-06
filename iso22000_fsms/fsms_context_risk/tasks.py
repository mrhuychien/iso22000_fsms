"""Scheduled tasks for fsms_context_risk."""

import frappe
from frappe.utils import add_days, today


def risk_review_reminder():
	"""Monthly — surface Risk Register entries whose next_review_date is within 30 days."""
	due = frappe.get_all(
		"FSMS Risk Register",
		filters={"next_review_date": ("between", [today(), add_days(today(), 30)])},
		fields=["name", "risk_description", "next_review_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_risk_review_due",
			message={"risk": row.name, "due": str(row.next_review_date)},
		)
