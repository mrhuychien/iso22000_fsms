"""Doc-event handlers for fsms_production (hooks.doc_events)."""

import frappe
from frappe.utils import today


def create_production_order_link(doc, method=None):
	"""On Work Order submit — create a paired FSMS Production Order skeleton."""
	if frappe.db.exists("FSMS Production Order", {"work_order": doc.name}):
		return
	po = frappe.get_doc({
		"doctype": "FSMS Production Order",
		"work_order": doc.name,
		"production_date": today(),
		"status": "Lên kế hoạch",
	})
	po.insert(ignore_permissions=True)
