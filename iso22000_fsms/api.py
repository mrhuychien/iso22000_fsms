"""Whitelisted REST endpoints for the iso22000_fsms app.

Module-specific endpoints live in <module>/api.py. This file is reserved for
cross-cutting endpoints (dashboard aggregation, global search, health checks).
"""

import frappe
from frappe.utils import add_days, today


@frappe.whitelist()
def ping():
	return {"app": "iso22000_fsms", "status": "ok"}


@frappe.whitelist()
def ncr_on_time_closure_rate() -> dict:
	"""Return % of NCRs closed on/before their proposed_completion_date in the last 12 months.

	Used by Number Card 'FSMS NCR On-time Closure Rate'.
	"""
	if not frappe.db.exists("DocType", "FSMS NCR"):
		return {"value": 0}
	cutoff = add_days(today(), -365)
	closed = frappe.db.count("FSMS NCR", filters={
		"workflow_state": "Đã đóng",
		"closed_date": (">=", cutoff),
	})
	if not closed:
		return {"value": 0}
	on_time = frappe.db.sql(
		"""
		SELECT COUNT(*) AS c FROM `tabFSMS NCR`
		WHERE workflow_state = 'Đã đóng'
		  AND closed_date >= %s
		  AND (proposed_completion_date IS NULL OR closed_date <= proposed_completion_date)
		""",
		(cutoff,),
	)[0][0]
	pct = round(100.0 * on_time / closed, 1) if closed else 0
	return {"value": pct, "fieldtype": "Percent"}


@frappe.whitelist()
def audit_findings_closure_rate() -> dict:
	"""Return % of Audit Findings linked to a closed NCR (last 12 months)."""
	if not frappe.db.exists("DocType", "FSMS Audit Finding"):
		return {"value": 0}
	cutoff = add_days(today(), -365)
	rows = frappe.db.sql(
		"""
		SELECT f.linked_ncr, n.workflow_state
		FROM `tabFSMS Audit Finding` f
		LEFT JOIN `tabFSMS NCR` n ON n.name = f.linked_ncr
		WHERE f.creation >= %s
		""",
		(cutoff,),
		as_dict=True,
	)
	if not rows:
		return {"value": 0}
	with_ncr = [r for r in rows if r.linked_ncr]
	if not with_ncr:
		return {"value": 0}
	closed = sum(1 for r in with_ncr if r.workflow_state == "Đã đóng")
	pct = round(100.0 * closed / len(with_ncr), 1)
	return {"value": pct, "fieldtype": "Percent"}
