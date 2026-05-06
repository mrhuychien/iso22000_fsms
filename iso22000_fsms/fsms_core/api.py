"""Module-level whitelisted endpoints for fsms_core.

Covers FSMS Settings, FSMS Manual, FSMS Policy, FSMS Objective.
"""

import frappe


@frappe.whitelist()
def get_active_manual():
	"""Return the currently published FSMS Manual (Single)."""
	return frappe.get_cached_doc("FSMS Manual")


@frappe.whitelist()
def get_active_policy():
	"""Return the currently published FSMS Policy (Single)."""
	return frappe.get_cached_doc("FSMS Policy")
