"""Doc-event handlers for fsms_supplier (hooks.doc_events)."""

import frappe
from frappe.utils import today


def escalate_rejected_material(doc, method=None):
	"""On Material Inspection Log submit — create NCR if any item rejected."""
	if doc.get("linked_ncr"):
		return
	rejected = [r for r in (doc.get("items") or []) if r.get("decision") == "Trả"]
	if not rejected:
		return
	ncr = frappe.get_doc({
		"doctype": "FSMS NCR",
		"ncr_date": today(),
		"ncr_source": "MATERIAL_REJECT",
		"source_reference_doctype": "FSMS Material Inspection Log",
		"source_reference_name": doc.name,
		"severity": "Major",
		"ncr_type": "Khắc phục",
		"nonconformity_description": frappe._("{0} item(s) rejected on inspection").format(len(rejected)),
	})
	ncr.insert(ignore_permissions=True)
	doc.db_set("linked_ncr", ncr.name)


def update_supplier_profile(doc, method=None):
	"""On Supplier Evaluation submit — push score/grade into FSMS Supplier Profile."""
	if not doc.get("supplier"):
		return
	profile = frappe.db.exists("FSMS Supplier Profile", {"supplier": doc.supplier})
	if not profile:
		return
	frappe.db.set_value("FSMS Supplier Profile", profile, {
		"last_evaluation_date": doc.get("eval_date"),
		"last_evaluation_score": doc.get("total_score"),
		"last_evaluation_grade": doc.get("grade"),
	})


def auto_create_inspection_log(doc, method=None):
	"""On Purchase Receipt submit — create blank Material Inspection Log to be filled by QC."""
	if frappe.db.exists("FSMS Material Inspection Log", {"purchase_receipt": doc.name}):
		return
	log = frappe.get_doc({
		"doctype": "FSMS Material Inspection Log",
		"inspection_date": today(),
		"purchase_receipt": doc.name,
		"supplier": doc.get("supplier"),
	})
	log.insert(ignore_permissions=True)
