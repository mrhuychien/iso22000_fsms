"""Scheduled tasks for fsms_sample."""

import frappe
from frappe.utils import today


def check_disposal_due():
	"""Daily — surface Sample Retention Logs whose expected_disposal_date <= today and not yet disposed."""
	due = frappe.get_all(
		"FSMS Sample Retention Log",
		filters={"expected_disposal_date": ("<=", today()), "actual_disposal_date": ("is", "not set")},
		fields=["name", "batch", "expected_disposal_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_sample_disposal_due",
			message={"sample": row.name, "due": str(row.expected_disposal_date)},
		)
