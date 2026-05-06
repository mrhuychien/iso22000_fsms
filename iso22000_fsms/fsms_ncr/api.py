"""Whitelisted endpoints + doc_event handlers for fsms_ncr.

Wires NCR lifecycle hooks declared in iso22000_fsms.hooks.doc_events.
"""

import frappe
from frappe import _
from frappe.utils import today


def validate_ncr(doc, method=None):
	"""Validate hook for FSMS NCR — delegates to controller.fsms_validate if exists."""
	if hasattr(doc, "fsms_validate"):
		doc.fsms_validate()


def set_signatures(doc, method=None):
	"""Auto-populate signature image fields from linked Employee records."""
	signature_pairs = [
		("requestor", "requestor_signature"),
		("analyzer", "analyzer_signature"),
		("approver", "approver_signature"),
		("verifier", "verifier_signature"),
	]
	for emp_field, sig_field in signature_pairs:
		emp = doc.get(emp_field)
		if emp and not doc.get(sig_field):
			sig = frappe.db.get_value("Employee", emp, "signature")
			if sig:
				doc.set(sig_field, sig)


def notify_assignees(doc, method=None):
	"""Share NCR with assigned employee on submit (in-app notification)."""
	if doc.get("assigned_to"):
		try:
			frappe.share.add(doc.doctype, doc.name, doc.assigned_to, write=1, notify=1)
		except Exception:
			pass


def handle_state_changes(doc, method=None):
	"""Hook into workflow_state changes after submit (verification fail → reissue)."""
	if doc.workflow_state == "Chuyển tiếp" and not doc.get("reissued_to_ncr"):
		new = frappe.get_doc({
			"doctype": "FSMS NCR",
			"ncr_date": today(),
			"ncr_source": doc.ncr_source,
			"severity": doc.severity,
			"ncr_type": doc.ncr_type,
			"affected_department": doc.affected_department,
			"nonconformity_description": _("Re-issued from {0}: {1}").format(
				doc.name, doc.nonconformity_description or ""
			),
			"reissued_from_ncr": doc.name,
		})
		new.insert(ignore_permissions=True)
		doc.db_set("reissued_to_ncr", new.name)


def audit_cancellation(doc, method=None):
	"""Append a comment recording who cancelled the NCR."""
	doc.add_comment("Info", _("NCR cancelled by {0}").format(frappe.session.user))


@frappe.whitelist()
def create_ncr_from_source(source_doctype: str, source_name: str, payload: dict | None = None) -> str:
	"""Cross-module helper — create an NCR linked to a triggering source document."""
	if not frappe.has_permission("FSMS NCR", ptype="create"):
		frappe.throw(_("Không có quyền tạo NCR"), frappe.PermissionError)
	payload = payload or {}
	ncr = frappe.get_doc({
		"doctype": "FSMS NCR",
		"ncr_date": today(),
		"source_reference_doctype": source_doctype,
		"source_reference_name": source_name,
		**payload,
	})
	ncr.insert()
	return ncr.name
