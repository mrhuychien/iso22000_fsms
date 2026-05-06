"""Scheduled tasks for fsms_haccp."""

import frappe
from frappe.utils import add_days, today


def haccp_plan_annual_review_check():
	"""Monthly — surface HACCP Plans whose next_review_date is within 30 days."""
	due = frappe.get_all(
		"FSMS HACCP Plan",
		filters={"next_review_date": ("between", [today(), add_days(today(), 30)])},
		fields=["name", "item", "next_review_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_haccp_review_due",
			message={"plan": row.name, "due": str(row.next_review_date)},
		)
