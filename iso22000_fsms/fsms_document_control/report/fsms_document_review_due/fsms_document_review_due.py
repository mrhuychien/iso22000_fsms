"""Script report: FSMS Document Review Due.

List tài liệu đến hạn review
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Doc Code', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Doc Name', 'fieldtype': 'Data', 'options': '', 'width': 200}, {'label': 'Owner', 'fieldtype': 'Link', 'options': 'Employee', 'width': 130}, {'label': 'Next Review', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Days to Due', 'fieldtype': 'Int', 'options': '', 'width': 100}]
	data = fsms_document_review_due(filters)
	return columns, data


def fsms_document_review_due(filters):

	rows = frappe.db.sql("""
		SELECT doc_code, doc_name, owner_employee AS owner_emp,
		       next_review_date AS due,
		       DATEDIFF(next_review_date, CURDATE()) AS days
		FROM `tabFSMS Document Register Internal`
		WHERE obsolete = 0 AND next_review_date IS NOT NULL
		ORDER BY next_review_date ASC
		""", as_dict=True)
	return [[r.doc_code, r.doc_name, r.owner_emp, r.due, r.days or 0] for r in rows]

