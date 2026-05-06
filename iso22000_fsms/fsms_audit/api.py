"""Doc-event handlers + endpoints for fsms_audit (hooks.doc_events)."""

import frappe


def validate_finding(doc, method=None):
	"""No-op stub — Audit Finding is a child table; validation lives in parent."""
	return


def create_ncr_from_findings(doc, method=None):
	"""On Audit Execution submit — auto-create NCR for each NC Major/Minor finding."""
	if not doc.get("auto_create_ncr"):
		return
	for finding in (doc.get("findings") or []):
		if finding.get("linked_ncr"):
			continue
		ftype = finding.get("finding_type")
		if ftype not in ("NC Major", "NC Minor"):
			continue
		ncr = frappe.get_doc({
			"doctype": "FSMS NCR",
			"ncr_date": doc.get("audit_date") or frappe.utils.today(),
			"ncr_source": "AUDIT",
			"source_reference_doctype": "FSMS Audit Execution",
			"source_reference_name": doc.name,
			"severity": "Major" if ftype == "NC Major" else "Minor",
			"ncr_type": "Khắc phục",
			"affected_department": finding.get("responsible_department"),
			"nonconformity_description": finding.get("finding_description"),
		})
		ncr.insert(ignore_permissions=True)
		finding.db_set("linked_ncr", ncr.name)
