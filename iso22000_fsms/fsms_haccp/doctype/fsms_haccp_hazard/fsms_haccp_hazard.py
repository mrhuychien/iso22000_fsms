"""Controller for FSMS HACCP Hazard child — risk_level computation."""

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FSMSHACCPHazard(Document):
	def validate(self):
		s = flt(self.severity) or 0
		l = flt(self.likelihood) or 0
		self.risk_level = int(s * l)
		self.is_significant = 1 if self.risk_level >= 6 else 0
