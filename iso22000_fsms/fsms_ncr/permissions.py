"""Permission query conditions + has_permission for fsms_ncr.

Registered in hooks.permission_query_conditions and hooks.has_permission.
NCR is scoped by `affected_department`: regular users only see NCRs in
departments they hold User Permission for, while FSMS Manager / Director /
Internal Auditor / System Manager have global visibility.
"""

import frappe


PRIVILEGED_ROLES = {
	"FSMS Manager",
	"FSMS Director",
	"FSMS Internal Auditor",
	"System Manager",
}


def _is_privileged(user: str | None = None) -> bool:
	roles = set(frappe.get_roles(user or frappe.session.user))
	return bool(roles & PRIVILEGED_ROLES)


def get_query_conditions(user: str | None = None) -> str:
	"""Return SQL WHERE clause restricting NCR list view by department scope."""
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	departments = frappe.defaults.get_user_permissions(user).get("Department") or []
	if not departments:
		return f"`tabFSMS NCR`.owner = {frappe.db.escape(user)}"
	dept_list = ", ".join(frappe.db.escape(d) for d in departments)
	return (
		f"(`tabFSMS NCR`.affected_department IN ({dept_list}) "
		f"OR `tabFSMS NCR`.owner = {frappe.db.escape(user)})"
	)


def has_permission(doc, ptype: str | None = None, user: str | None = None) -> bool:
	"""Per-document permission check for FSMS NCR."""
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	if doc.owner == user:
		return True
	allowed_depts = frappe.defaults.get_user_permissions(user).get("Department") or []
	return doc.get("affected_department") in allowed_depts
