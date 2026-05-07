"""Controller for FSMS Material Inspection Log (BM.07.03)."""

import frappe
from frappe.model.document import Document


class FSMSMaterialInspectionLog(Document):
	def validate(self):
		self._auto_pull_supplier_from_pr()

	def _auto_pull_supplier_from_pr(self):
		if self.purchase_receipt and not self.supplier:
			self.supplier = frappe.db.get_value("Purchase Receipt", self.purchase_receipt, "supplier")
