"""Doc-event handlers + endpoints for fsms_recall (hooks.doc_events)."""

import frappe
from frappe.utils import today


def handle_recall_state_change(doc, method=None):
	"""On Recall Event workflow_state change — sync downstream Recall Plan / Report."""
	if doc.workflow_state == "Đang thu hồi" and doc.recall_plan:
		frappe.db.set_value("FSMS Recall Plan", doc.recall_plan, "workflow_state", "Executing")


def create_traceability_trace(doc, method=None):
	"""On Recall Event submit — auto-create a linked Traceability Trace."""
	if not doc.get("affected_batches"):
		return
	first_batch = doc.affected_batches[0].get("batch") if doc.affected_batches else None
	if not first_batch:
		return
	trace = frappe.get_doc({
		"doctype": "FSMS Traceability Trace",
		"trace_date": today(),
		"trigger": "Recall",
		"linked_recall_event": doc.name,
		"target_batch": first_batch,
	})
	trace.insert(ignore_permissions=True)
