"""Script report: FSMS Training Compliance Matrix.

Employee × Course × Status
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Employee', 'fieldtype': 'Link', 'options': 'Employee', 'width': 130}, {'label': 'Course', 'fieldtype': 'Link', 'options': 'FSMS Training Course', 'width': 150}, {'label': 'Last Session', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Score', 'fieldtype': 'Float', 'options': '', 'width': 100}, {'label': 'Passed', 'fieldtype': 'Check', 'options': '', 'width': 80}]
	data = fsms_training_compliance_matrix(filters)
	return columns, data


def fsms_training_compliance_matrix(filters):

	rows = frappe.db.sql("""
		SELECT a.employee, s.course, MAX(s.session_date) AS last_session,
		       MAX(a.post_test_score) AS score, MAX(a.passed) AS passed
		FROM `tabFSMS Training Attendance` a
		JOIN `tabFSMS Training Session` s ON a.parent = s.name
		WHERE s.docstatus = 1
		GROUP BY a.employee, s.course
		ORDER BY a.employee, s.course
		""", as_dict=True)
	return [[r.employee, r.course, r.last_session, r.score or 0, r.passed or 0] for r in rows]

