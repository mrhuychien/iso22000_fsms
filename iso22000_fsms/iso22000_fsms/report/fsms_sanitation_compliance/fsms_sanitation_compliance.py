"""Script report: FSMS Sanitation Compliance.

% vệ sinh đạt theo ngày × ca
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Date', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Shift', 'fieldtype': 'Data', 'options': '', 'width': 80}, {'label': 'Total', 'fieldtype': 'Int', 'options': '', 'width': 80}, {'label': 'Passed', 'fieldtype': 'Int', 'options': '', 'width': 80}, {'label': 'Failed', 'fieldtype': 'Int', 'options': '', 'width': 80}, {'label': 'Pass %', 'fieldtype': 'Float', 'options': '', 'width': 80}]
	data = fsms_sanitation_compliance(filters)
	return columns, data


def fsms_sanitation_compliance(filters):

	rows = frappe.db.sql("""
		SELECT inspection_date AS d, shift, total_workers AS tot, total_passed AS pas, total_failed AS fail
		FROM `tabFSMS Worker Hygiene Daily`
		ORDER BY inspection_date DESC, shift
		""", as_dict=True)
	out = []
	for r in rows:
		pct = round(100.0 * (r.pas or 0) / r.tot, 1) if r.tot else 0
		out.append([r.d, r.shift or '', r.tot or 0, r.pas or 0, r.fail or 0, pct])
	return out

