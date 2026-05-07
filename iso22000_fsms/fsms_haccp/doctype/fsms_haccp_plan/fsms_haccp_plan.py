"""Controller for FSMS HACCP Plan — kế hoạch HACCP per QT 14."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class FSMSHACCPPlan(Document):
	"""HACCP Plan — 1 plan per Item.

	Workflow: Draft → Reviewed → Approved → Published → Under Revision → Obsolete.
	"""

	def validate(self):
		self._compute_hazard_risk_levels()
		self._derive_ccp_oprp_flags()

	def _compute_hazard_risk_levels(self):
		for h in (self.hazard_analysis or []):
			s = flt(h.severity) or 0
			l = flt(h.likelihood) or 0
			h.risk_level = int(s * l)
			h.is_significant = 1 if h.risk_level >= 6 else 0

	def _derive_ccp_oprp_flags(self):
		"""Codex-style 4-question decision tree determines CCP vs OPRP.

		Simplified rule:
			Q1=No → not significant
			Q1=Yes,Q2=Yes → CCP
			Q1=Yes,Q2=No,Q3=Yes → OPRP
		"""
		for h in (self.hazard_analysis or []):
			if not h.decision_tree_q1:
				h.is_ccp = 0
				h.is_oprp = 0
				continue
			if h.decision_tree_q2:
				h.is_ccp = 1
				h.is_oprp = 0
			elif h.decision_tree_q3:
				h.is_ccp = 0
				h.is_oprp = 1
			else:
				h.is_ccp = 0
				h.is_oprp = 0

	def on_submit(self):
		if not self.workflow_state:
			self.db_set("workflow_state", "Approved")

	@frappe.whitelist()
	def list_active_ccps(self) -> list:
		"""Helper for CCP Monitoring Log autocomplete."""
		return [{"ccp_no": c.ccp_no, "critical_limit": c.critical_limit,
		         "monitoring_frequency": c.monitoring_frequency}
		        for c in (self.ccps or [])]
