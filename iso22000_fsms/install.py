"""Lifecycle hooks: after_install + before_uninstall (registered in hooks.py)."""

import frappe


def after_install():
	"""Called once after `bench install-app iso22000_fsms`.

	Frappe auto-loads the `fixtures = [...]` declared in hooks.py before this
	runs, so fixtures are already in the DB when we get here. We use this hook
	for tasks that need actual SQL (rather than fixture JSON):
	1. Ensure FSMS Settings has its sole record
	2. Print a friendly banner
	"""
	if frappe.db.exists("DocType", "FSMS Settings") and not frappe.db.exists("FSMS Settings"):
		frappe.get_doc({"doctype": "FSMS Settings", "company_name": "(Chưa cấu hình)"}).insert(
			ignore_permissions=True
		)
	print("✓ ISO 22000 FSMS installed. Mở `Bảng điều khiển ATTP` từ menu chính.")


def before_uninstall():
	"""Pre-uninstall guardrail: warn if there is real production data."""
	risky_doctypes = ["FSMS NCR", "FSMS Recall Event", "FSMS HACCP Plan", "FSMS Audit Execution"]
	for dt in risky_doctypes:
		if frappe.db.exists("DocType", dt):
			count = frappe.db.count(dt)
			if count > 0:
				frappe.msgprint(
					f"⚠️  {dt} còn {count} bản ghi. Hãy chắc chắn anh đã backup trước khi uninstall.",
					alert=True,
				)
