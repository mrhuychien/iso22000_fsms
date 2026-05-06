"""Scheduled tasks for fsms_ncr — invoked by Frappe scheduler per hooks.py."""

import frappe
from frappe.utils import getdate, today


def check_overdue_ncr():
	"""Daily — flag NCRs whose proposed_completion_date is past and still in 'Đang thực hiện'."""
	overdue = frappe.get_all(
		"FSMS NCR",
		filters={
			"workflow_state": "Đang thực hiện",
			"proposed_completion_date": ("<", today()),
			"docstatus": 1,
		},
		fields=["name", "assigned_to", "proposed_completion_date"],
	)
	for row in overdue:
		if not row.assigned_to:
			continue
		# Lightweight notification — caller is the scheduler, no UI session.
		frappe.publish_realtime(
			event="fsms_ncr_overdue",
			message={"ncr": row.name, "due": str(row.proposed_completion_date)},
			user=row.assigned_to,
		)
