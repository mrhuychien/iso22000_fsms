"""Script report: FSMS Risk Heatmap.

Risk × Likelihood × Severity, color-coded
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Risk', 'fieldtype': 'Link', 'options': 'FSMS Risk Register', 'width': 150}, {'label': 'Category', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Likelihood', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Severity', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Total Score', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Risk Level', 'fieldtype': 'Data', 'options': '', 'width': 130}]
	data = fsms_risk_heatmap(filters)
	return columns, data


def fsms_risk_heatmap(filters):

	rows = frappe.db.sql("""
		SELECT name, risk_category AS cat,
		       score_a_likelihood AS lk, score_c_severity AS sv,
		       total_score, risk_level
		FROM `tabFSMS Risk Register`
		ORDER BY total_score DESC
		""", as_dict=True)
	return [[r.name, r.cat, r.lk or 0, r.sv or 0, r.total_score or 0, r.risk_level or ''] for r in rows]

