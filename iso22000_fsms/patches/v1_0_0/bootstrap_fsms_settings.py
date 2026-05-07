"""Idempotent: ensure FSMS Settings (Single) has a row with sensible defaults."""

import frappe


def execute():
	if not frappe.db.exists("DocType", "FSMS Settings"):
		return
	settings = frappe.get_single("FSMS Settings")
	dirty = False
	defaults = {
		"std_version": "ISO 22000:2018",
		"fiscal_year_cycle": "Calendar",
		"retention_years_default": 3,
		"mandatory_drill_frequency_months": 12,
	}
	for fieldname, value in defaults.items():
		if not settings.get(fieldname):
			settings.set(fieldname, value)
			dirty = True
	if dirty:
		settings.flags.ignore_permissions = True
		settings.flags.ignore_validate = True
		settings.save()
