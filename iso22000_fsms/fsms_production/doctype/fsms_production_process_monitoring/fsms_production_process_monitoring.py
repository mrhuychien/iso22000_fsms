"""Controller for FSMS Production Process Monitoring (BM.08.02)."""

import frappe
from frappe.model.document import Document


class FSMSProductionProcessMonitoring(Document):
	def validate(self):
		self._compute_violation_counts()
		self._compute_within_limit_per_step()

	def _compute_within_limit_per_step(self):
		from frappe.utils import flt
		for step in (self.step_records or []):
			val = flt(step.parameter_value)
			lo = flt(step.acceptance_min) if step.acceptance_min not in (None, "") else None
			hi = flt(step.acceptance_max) if step.acceptance_max not in (None, "") else None
			ok = True
			if lo is not None and val < lo:
				ok = False
			if hi is not None and val > hi:
				ok = False
			step.is_within_limit = 1 if ok else 0

	def _compute_violation_counts(self):
		ccp = sum(1 for s in (self.step_records or []) if s.is_ccp and not s.is_within_limit)
		oprp = sum(1 for s in (self.step_records or []) if s.is_oprp and not s.is_within_limit)
		self.total_ccp_violations = ccp
		self.total_oprp_violations = oprp
