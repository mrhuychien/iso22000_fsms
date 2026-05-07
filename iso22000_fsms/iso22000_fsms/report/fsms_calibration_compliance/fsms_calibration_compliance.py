"""Script report: FSMS Calibration Compliance.

% thiết bị đo còn hợp chuẩn vs quá hạn
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Equipment', 'fieldtype': 'Link', 'options': 'FSMS Measurement Equipment', 'width': 150}, {'label': 'Last Calibration', 'fieldtype': 'Date', 'options': '', 'width': 130}, {'label': 'Next Calibration', 'fieldtype': 'Date', 'options': '', 'width': 130}, {'label': 'Days to Due', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Status', 'fieldtype': 'Data', 'options': '', 'width': 100}]
	data = fsms_calibration_compliance(filters)
	return columns, data


def fsms_calibration_compliance(filters):

	rows = frappe.db.sql("""
		SELECT name, last_calibration_date AS last_cal, next_calibration_date AS next_cal,
		       DATEDIFF(next_calibration_date, CURDATE()) AS days_to_due,
		       current_status
		FROM `tabFSMS Measurement Equipment`
		ORDER BY next_calibration_date ASC
		""", as_dict=True)
	return [[r.name, r.last_cal, r.next_cal, r.days_to_due or 0, r.current_status or ''] for r in rows]

