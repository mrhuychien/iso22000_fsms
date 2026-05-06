"""Scheduled tasks for fsms_emergency."""

import frappe
from frappe.utils import add_days, today


def check_inspection_due():
	"""Daily — surface Fire Equipment whose next_inspection_date <= today + 7d."""
	due = frappe.get_all(
		"FSMS Fire Equipment",
		filters={"next_inspection_date": ("between", [today(), add_days(today(), 7)])},
		fields=["name", "equipment_code", "next_inspection_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_fire_inspection_due",
			message={"equipment": row.name, "code": row.equipment_code, "due": str(row.next_inspection_date)},
		)
