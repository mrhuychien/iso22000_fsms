"""Script report: FSMS Supplier Performance.

Grade trung bình theo supplier × thời gian
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Supplier', 'fieldtype': 'Link', 'options': 'Supplier', 'width': 150}, {'label': 'Eval Count', 'fieldtype': 'Int', 'options': '', 'width': 80}, {'label': 'Avg Score', 'fieldtype': 'Float', 'options': '', 'width': 100}, {'label': 'Last Grade', 'fieldtype': 'Data', 'options': '', 'width': 80}, {'label': 'Last Eval Date', 'fieldtype': 'Date', 'options': '', 'width': 120}]
	data = fsms_supplier_performance(filters)
	return columns, data


def fsms_supplier_performance(filters):

	rows = frappe.db.sql("""
		SELECT supplier, COUNT(*) AS cnt, AVG(total_score) AS avg_score,
		       MAX(eval_date) AS last_date
		FROM `tabFSMS Supplier Evaluation`
		WHERE docstatus = 1
		GROUP BY supplier
		ORDER BY avg_score DESC
		""", as_dict=True)
	out = []
	for r in rows:
		last_grade = frappe.db.get_value("FSMS Supplier Evaluation",
			{"supplier": r.supplier, "eval_date": r.last_date}, "grade") or ''
		out.append([r.supplier, r.cnt, round(r.avg_score or 0, 2), last_grade, r.last_date])
	return out

