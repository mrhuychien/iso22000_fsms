"""Doc-event handlers for fsms_training (hooks.doc_events)."""

import frappe


def update_employee_competency(doc, method=None):
	"""On Training Session submit — update each attendee's competency record."""
	for att in (doc.get("attendees") or []):
		if att.get("passed") and att.get("employee"):
			# Light stamp — full Competency Matrix update is a separate workflow.
			frappe.db.set_value("Employee", att.employee, "fsms_last_training_date", doc.get("session_date"))
