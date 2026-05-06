"""Scheduled tasks for fsms_traceability."""

import frappe
from frappe.utils import add_months, getdate, today


def drill_due_check():
	"""Monthly — check FSMS Traceability Settings.last_drill_date vs frequency."""
	if not frappe.db.exists("DocType", "FSMS Traceability Settings"):
		return
	settings = frappe.get_cached_doc("FSMS Traceability Settings")
	last = settings.get("last_drill_date")
	freq = settings.get("mandatory_drill_frequency_months") or 6
	if not last:
		return
	due_on = add_months(getdate(last), freq)
	if getdate(today()) >= getdate(due_on):
		frappe.publish_realtime(
			event="fsms_trace_drill_due",
			message={"due_on": str(due_on)},
		)
