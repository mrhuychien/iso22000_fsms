"""Permission query conditions for fsms_context_risk."""

import frappe


PRIVILEGED_ROLES = {"FSMS Manager", "FSMS Director", "System Manager"}


def get_query_conditions(user: str | None = None) -> str:
	"""Risk Register: scope by risk_owner department for non-privileged users."""
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if roles & PRIVILEGED_ROLES:
		return ""
	departments = frappe.defaults.get_user_permissions(user).get("Department") or []
	if not departments:
		return f"`tabFSMS Risk Register`.owner = {frappe.db.escape(user)}"
	dept_list = ", ".join(frappe.db.escape(d) for d in departments)
	return f"`tabFSMS Risk Register`.risk_owner IN ({dept_list})"
