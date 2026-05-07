"""Script report: FSMS Audit Findings Trend.

Trend NC Major/Minor theo quý
"""

import frappe


def execute(filters=None):
	"""Frappe report entry point — return (columns, data)."""
	columns = [{'label': 'Quarter', 'fieldtype': 'Data', 'options': '', 'width': 100}, {'label': 'NC Major', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'NC Minor', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Observation', 'fieldtype': 'Int', 'options': '', 'width': 100}, {'label': 'Total', 'fieldtype': 'Int', 'options': '', 'width': 100}]
	data = fsms_audit_findings_trend(filters)
	return columns, data


def fsms_audit_findings_trend(filters):

	rows = frappe.db.sql("""
		SELECT CONCAT(YEAR(creation), '-Q', QUARTER(creation)) AS q,
		       finding_type AS ft, COUNT(*) AS c
		FROM `tabFSMS Audit Finding`
		GROUP BY YEAR(creation), QUARTER(creation), finding_type
		ORDER BY q
		""", as_dict=True)
	buckets = {}
	for r in rows:
		b = buckets.setdefault(r.q, {"NC Major": 0, "NC Minor": 0, "Observation": 0, "OFI": 0})
		b[r.ft or "OFI"] = r.c
	return [[q, b["NC Major"], b["NC Minor"], b["Observation"], sum(b.values())] for q, b in sorted(buckets.items())]

