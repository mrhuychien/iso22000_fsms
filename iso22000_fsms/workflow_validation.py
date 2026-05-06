import frappe
from frappe.model.workflow import apply_workflow


@frappe.whitelist()
def apply_workflow_with_validation(doc, action):
	"""OR-logic approval validator wrapper around frappe.model.workflow.apply_workflow.

	Centralized hook that lets module-specific validators veto a workflow transition
	before the core engine applies it. Per-DocType validators are registered in
	the FSMS_WORKFLOW_VALIDATORS map below.
	"""
	doc = frappe.get_doc(frappe.parse_json(doc)) if isinstance(doc, str) else doc

	validator = FSMS_WORKFLOW_VALIDATORS.get(doc.doctype)
	if validator:
		frappe.get_attr(validator)(doc, action)

	return apply_workflow(doc, action)


FSMS_WORKFLOW_VALIDATORS: dict[str, str] = {
	# "FSMS NCR": "iso22000_fsms.fsms_ncr.api.validate_workflow_transition",
}
