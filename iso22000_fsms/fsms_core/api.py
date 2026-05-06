"""Module-level whitelisted endpoints for fsms_core.

Covers FSMS Settings, FSMS Manual, FSMS Policy, FSMS Objective.
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_active_manual():
	"""Return the currently published FSMS Manual (Single)."""
	if not frappe.has_permission("FSMS Manual", ptype="read"):
		frappe.throw(_("Không có quyền đọc FSMS Manual"), frappe.PermissionError)
	return frappe.get_cached_doc("FSMS Manual")


@frappe.whitelist()
def get_active_policy():
	"""Return the currently published FSMS Policy (Single)."""
	if not frappe.has_permission("FSMS Policy", ptype="read"):
		frappe.throw(_("Không có quyền đọc FSMS Policy"), frappe.PermissionError)
	return frappe.get_cached_doc("FSMS Policy")


@frappe.whitelist()
def get_objectives_for_year(year: int):
	"""List FSMS Objective records for a given year, respecting permissions."""
	if not frappe.has_permission("FSMS Objective", ptype="read"):
		frappe.throw(_("Không có quyền đọc FSMS Objective"), frappe.PermissionError)
	return frappe.get_all(
		"FSMS Objective",
		filters={"objective_year": int(year)},
		fields=[
			"name",
			"objective_code",
			"objective_text",
			"kpi_metric",
			"target_value",
			"actual_value",
			"status",
			"responsible_department",
			"responsible_employee",
			"last_review_date",
			"next_review_date",
		],
		order_by="objective_code asc",
	)
