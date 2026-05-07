"""Jinja helpers + utility functions exposed via hooks.jinja and used in
Print Formats / email templates."""

import frappe
from frappe.utils import flt, formatdate


def format_vnd(value) -> str:
	"""Format a number as Vietnamese currency: 1.234.567 ₫"""
	if value is None or value == "":
		return ""
	try:
		v = flt(value)
	except (TypeError, ValueError):
		return str(value)
	# Vietnamese: dot as thousand separator, no decimals.
	s = f"{int(round(v)):,}".replace(",", ".")
	return f"{s} ₫"


def format_vn_date(date_value) -> str:
	"""Format a date as 'ngày DD tháng MM năm YYYY' for Vietnamese print formats."""
	if not date_value:
		return ""
	try:
		formatted = formatdate(date_value, "dd/MM/yyyy")
		d, m, y = formatted.split("/")
		return f"ngày {d} tháng {m} năm {y}"
	except Exception:
		return str(date_value)


def signature_or_blank(employee_id: str | None) -> str:
	"""Return the FSMS signature image URL for an Employee, or empty string."""
	if not employee_id:
		return ""
	# Prefer custom field added via fixtures, fall back to standard `signature` field
	value = frappe.db.get_value("Employee", employee_id, "fsms_signature_image")
	if not value:
		value = frappe.db.get_value("Employee", employee_id, "signature")
	return value or ""


def employee_full_name(employee_id: str | None) -> str:
	"""Return employee_name (Vietnamese full name) or the ID itself if not found."""
	if not employee_id:
		return ""
	return frappe.db.get_value("Employee", employee_id, "employee_name") or employee_id
