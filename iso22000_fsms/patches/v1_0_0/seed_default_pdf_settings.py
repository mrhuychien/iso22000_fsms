"""Idempotent: ensure Print Settings allows wide-table A4 layout for FSMS print formats."""

import frappe


def execute():
	if not frappe.db.exists("DocType", "Print Settings"):
		return
	ps = frappe.get_single("Print Settings")
	dirty = False
	if not ps.get("pdf_page_size") or ps.pdf_page_size not in ("A4", "Letter"):
		ps.pdf_page_size = "A4"
		dirty = True
	if not ps.get("font_size"):
		ps.font_size = 12
		dirty = True
	if dirty:
		ps.flags.ignore_permissions = True
		ps.save()
