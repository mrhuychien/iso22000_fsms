"""Scheduled tasks for fsms_equipment."""

import frappe
from frappe.utils import add_days, today


def check_calibration_due():
	"""Daily — surface Measurement Equipment whose next_calibration_date <= today + 14d."""
	due = frappe.get_all(
		"FSMS Measurement Equipment",
		filters={"next_calibration_date": ("between", [today(), add_days(today(), 14)])},
		fields=["name", "equipment_name", "next_calibration_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_calibration_due",
			message={"equipment": row.name, "due": str(row.next_calibration_date)},
		)
