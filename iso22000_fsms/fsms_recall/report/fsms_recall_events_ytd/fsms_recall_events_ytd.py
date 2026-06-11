"""Script report: FSMS Recall Events YTD.

List recall events trong năm + cost impact
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Event', 'fieldtype': 'Link', 'options': 'FSMS Recall Event', 'width': 150}, {'label': 'Date', 'fieldtype': 'Date', 'options': '', 'width': 120}, {'label': 'Severity', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Recall Level', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'Cost Impact', 'fieldtype': 'Currency', 'options': '', 'width': 130}, {'label': 'Status', 'fieldtype': 'Data', 'options': '', 'width': 130}]
	data = fsms_recall_events_ytd(filters)
	return columns, data


def fsms_recall_events_ytd(filters):

	from frappe.utils import getdate
	year_start = f"{getdate().year}-01-01"
	rows = frappe.db.sql("""
		SELECT e.name AS event, e.event_date, e.defect_severity AS sev,
		       e.recall_level, e.workflow_state AS state,
		       COALESCE(r.cost_impact, 0) AS cost
		FROM `tabFSMS Recall Event` e
		LEFT JOIN `tabFSMS Recall Report` r ON r.recall_event = e.name AND r.docstatus = 1
		WHERE e.event_date >= %s
		ORDER BY e.event_date DESC
		""", (year_start,), as_dict=True)
	return [[r.event, r.event_date, r.sev, r.recall_level, r.cost, r.state] for r in rows]

