"""Script report: FSMS HACCP Plan Status.

List HACCP Plans + last review date
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Plan', 'fieldtype': 'Link', 'options': 'FSMS HACCP Plan', 'width': 150}, {'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 130}, {'label': 'Version', 'fieldtype': 'Data', 'options': '', 'width': 80}, {'label': 'Effective', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Next Review', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'State', 'fieldtype': 'Data', 'options': '', 'width': 130}]
	data = fsms_haccp_plan_status(filters)
	return columns, data


def fsms_haccp_plan_status(filters):

	rows = frappe.db.sql("""
		SELECT name, item, plan_version, effective_date, next_review_date, workflow_state
		FROM `tabFSMS HACCP Plan`
		ORDER BY item
		""", as_dict=True)
	return [[r.name, r.item, r.plan_version, r.effective_date, r.next_review_date, r.workflow_state] for r in rows]

