import frappe


def boot_fsms_session(bootinfo):
	"""Inject FSMS Settings + per-user FSMS context into the client bootinfo."""
	bootinfo.fsms = frappe._dict()

	settings = frappe.get_cached_doc("FSMS Settings") if frappe.db.exists("DocType", "FSMS Settings") else None
	if settings:
		bootinfo.fsms.settings = {
			"company_name": settings.get("company_name"),
			"std_version": settings.get("std_version"),
			"retention_years_default": settings.get("retention_years_default"),
			"fiscal_year_cycle": settings.get("fiscal_year_cycle"),
		}
