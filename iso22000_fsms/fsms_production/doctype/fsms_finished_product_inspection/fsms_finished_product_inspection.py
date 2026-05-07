"""Controller for FSMS Finished Product Inspection (BM.08.03)."""

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FSMSFinishedProductInspection(Document):
	def validate(self):
		self._validate_quantities()
		self._auto_set_decision()

	def _validate_quantities(self):
		inspected = flt(self.qty_inspected)
		passed = flt(self.qty_passed)
		failed = flt(self.qty_failed)
		if passed + failed > inspected and inspected:
			frappe.msgprint("SL đạt + SL loại > SL kiểm tra — kiểm tra lại số liệu", alert=True)

	def _auto_set_decision(self):
		if self.decision:
			return
		failed = flt(self.qty_failed)
		inspected = flt(self.qty_inspected)
		if not inspected:
			return
		fail_pct = 100.0 * failed / inspected
		if fail_pct == 0:
			self.decision = "Đạt"
		elif fail_pct < 5:
			self.decision = "Treo"
		else:
			self.decision = "Loại"
