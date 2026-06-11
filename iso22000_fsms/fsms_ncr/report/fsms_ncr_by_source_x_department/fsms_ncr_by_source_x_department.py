"""Script report: FSMS NCR by Source × Department.

Pivot table NCR theo nguồn × bộ phận
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Source', 'fieldtype': 'Data', 'options': '', 'width': 150}, {'label': 'Department', 'fieldtype': 'Link', 'options': 'Department', 'width': 150}, {'label': 'Count', 'fieldtype': 'Int', 'options': '', 'width': 80}]
	data = fsms_ncr_by_source_x_department(filters)
	return columns, data


def fsms_ncr_by_source_x_department(filters):

	rows = frappe.db.sql("""
		SELECT ncr_source AS src, affected_department AS dept, COUNT(*) AS c
		FROM `tabFSMS NCR`
		GROUP BY ncr_source, affected_department
		ORDER BY c DESC
		""", as_dict=True)
	return [[r.src or '(không có)', r.dept or '(không có)', r.c] for r in rows]

