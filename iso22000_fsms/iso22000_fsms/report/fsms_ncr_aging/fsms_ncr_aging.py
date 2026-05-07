"""Script report: FSMS NCR Aging.

NCR mở theo độ tuổi (0-7 / 7-30 / 30+ ngày)
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'NCR', 'fieldtype': 'Link', 'options': 'FSMS NCR', 'width': 130}, {'label': 'Severity', 'fieldtype': 'Data', 'options': '', 'width': 80}, {'label': 'Department', 'fieldtype': 'Link', 'options': 'Department', 'width': 150}, {'label': 'Age (days)', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Bucket', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Workflow State', 'fieldtype': 'Data', 'options': '', 'width': 130}]
	data = fsms_ncr_aging(filters)
	return columns, data


def fsms_ncr_aging(filters):

	filters = filters or {}
	rows = frappe.db.sql("""
		SELECT name AS ncr,
		       severity,
		       affected_department AS department,
		       DATEDIFF(CURDATE(), ncr_date) AS age_days,
		       workflow_state
		FROM `tabFSMS NCR`
		WHERE workflow_state NOT IN ('Đã đóng', 'Chuyển tiếp')
		""", as_dict=True)
	out = []
	for r in rows:
		age = r.age_days or 0
		bucket = '0-7' if age <= 7 else ('7-30' if age <= 30 else '30+')
		out.append([r.ncr, r.severity, r.department, age, bucket, r.workflow_state])
	return out

