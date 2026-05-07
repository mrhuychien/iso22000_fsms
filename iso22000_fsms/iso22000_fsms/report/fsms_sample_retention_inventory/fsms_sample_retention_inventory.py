"""Script report: FSMS Sample Retention Inventory.

Mẫu đang lưu + ngày hủy dự kiến
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Sample', 'fieldtype': 'Link', 'options': 'FSMS Sample Retention Log', 'width': 150}, {'label': 'Batch', 'fieldtype': 'Link', 'options': 'Batch', 'width': 130}, {'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 130}, {'label': 'Sample Date', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Disposal Due', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Days to Disposal', 'fieldtype': 'Int', 'options': '', 'width': 130}]
	data = fsms_sample_retention_inventory(filters)
	return columns, data


def fsms_sample_retention_inventory(filters):

	rows = frappe.db.sql("""
		SELECT name, batch, item, sample_date, expected_disposal_date AS due,
		       DATEDIFF(expected_disposal_date, CURDATE()) AS days
		FROM `tabFSMS Sample Retention Log`
		WHERE actual_disposal_date IS NULL
		ORDER BY expected_disposal_date ASC
		""", as_dict=True)
	return [[r.name, r.batch, r.item, r.sample_date, r.due, r.days or 0] for r in rows]

