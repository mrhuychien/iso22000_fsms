"""Doc-event handlers for fsms_communication (hooks.doc_events)."""

import frappe
from frappe.utils import today


def handle_complaint(doc, method=None):
	"""On Customer Complaint submit — optionally cascade to NCR / Recall Event."""
	if doc.get("auto_create_ncr") and not doc.get("linked_ncr"):
		ncr = frappe.get_doc({
			"doctype": "FSMS NCR",
			"ncr_date": today(),
			"ncr_source": "COMPLAINT",
			"source_reference_doctype": "FSMS Customer Complaint",
			"source_reference_name": doc.name,
			"severity": "Major" if doc.get("severity") in ("Cấp 1", "Cấp 2") else "Minor",
			"ncr_type": "Khắc phục",
			"nonconformity_description": doc.get("complaint_subject"),
		})
		ncr.insert(ignore_permissions=True)
		doc.db_set("linked_ncr", ncr.name)
	if doc.get("auto_create_recall_event") and not doc.get("linked_recall_event"):
		event = frappe.get_doc({
			"doctype": "FSMS Recall Event",
			"event_date": today(),
			"trigger_source": "Khiếu nại KH",
			"defect_description": doc.get("complaint_subject"),
			"defect_severity": doc.get("severity"),
		})
		event.insert(ignore_permissions=True)
		doc.db_set("linked_recall_event", event.name)
