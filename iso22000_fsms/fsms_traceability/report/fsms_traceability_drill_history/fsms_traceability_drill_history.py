"""Script report: FSMS Traceability Drill History.

Drill outcomes + average completion time
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Drill', 'fieldtype': 'Link', 'options': 'FSMS Traceability Drill', 'width': 150}, {'label': 'Date', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Batch', 'fieldtype': 'Link', 'options': 'Batch', 'width': 130}, {'label': 'Time (min)', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Within Target', 'fieldtype': 'Check', 'options': '', 'width': 100}, {'label': 'Outcome', 'fieldtype': 'Data', 'options': '', 'width': 200}]
	data = fsms_traceability_drill_history(filters)
	return columns, data


def fsms_traceability_drill_history(filters):

	rows = frappe.db.sql("""
		SELECT name, drill_date, selected_batch AS batch,
		       time_taken_minutes, is_within_target, drill_outcome
		FROM `tabFSMS Traceability Drill`
		ORDER BY drill_date DESC
		""", as_dict=True)
	return [[r.name, r.drill_date, r.batch, r.time_taken_minutes or 0, r.is_within_target or 0, r.drill_outcome or ''] for r in rows]

