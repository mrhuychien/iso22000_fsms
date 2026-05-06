"""Doc-event handlers for fsms_document_control (hooks.doc_events)."""

import frappe
from frappe.utils import today


def publish_document(doc, method=None):
	"""On Document Change Request workflow_state → 'Phát hành': bump target register."""
	if doc.workflow_state != "Phát hành":
		return
	target_dt = doc.get("target_document_type")
	target = doc.get("target_document")
	if not (target_dt and target):
		return
	register_dt = "FSMS Document Register Internal" if target_dt == "Nội bộ" else "FSMS Document Register External"
	if frappe.db.exists(register_dt, target):
		frappe.db.set_value(register_dt, target, {
			"current_revision": doc.get("proposed_revision"),
			"effective_date": today(),
		})
