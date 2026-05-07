"""Script report: FSMS Customer Complaint Analysis.

Complaint theo channel × severity × resolution time
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Channel', 'fieldtype': 'Data', 'options': '', 'width': 150}, {'label': 'Severity', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Count', 'fieldtype': 'Int', 'options': '', 'width': 80}, {'label': 'Avg Resolution Days', 'fieldtype': 'Float', 'options': '', 'width': 130}]
	data = fsms_customer_complaint_analysis(filters)
	return columns, data


def fsms_customer_complaint_analysis(filters):

	rows = frappe.db.sql("""
		SELECT complaint_channel AS ch, severity AS sev, COUNT(*) AS c,
		       AVG(DATEDIFF(resolution_date, complaint_date)) AS avg_res
		FROM `tabFSMS Customer Complaint`
		WHERE complaint_date IS NOT NULL
		GROUP BY complaint_channel, severity
		ORDER BY c DESC
		""", as_dict=True)
	return [[r.ch or '', r.sev or '', r.c, round(r.avg_res or 0, 1)] for r in rows]

