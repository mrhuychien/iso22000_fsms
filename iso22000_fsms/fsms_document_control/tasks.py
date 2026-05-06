"""Scheduled tasks for fsms_document_control."""

import frappe
from frappe.utils import add_days, today


def check_document_review_due():
	"""Weekly — surface Internal Documents whose next_review_date <= today + 30d."""
	due = frappe.get_all(
		"FSMS Document Register Internal",
		filters={"next_review_date": ("between", [today(), add_days(today(), 30)]), "obsolete": 0},
		fields=["name", "doc_code", "next_review_date"],
	)
	for row in due:
		frappe.publish_realtime(
			event="fsms_doc_review_due",
			message={"doc": row.name, "code": row.doc_code, "due": str(row.next_review_date)},
		)
