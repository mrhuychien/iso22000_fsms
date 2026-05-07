"""Controller for FSMS Communication Log."""

import frappe
from frappe.model.document import Document


class FSMSCommunicationLog(Document):
	def validate(self):
		# If counterparty_link is provided but type missing, infer from doctype name
		if self.counterparty_link_doctype and not self.counterparty_type:
			self.counterparty_type = self._infer_counterparty_type(self.counterparty_link_doctype)

	@staticmethod
	def _infer_counterparty_type(dt: str) -> str:
		m = {"Customer": "KH", "Supplier": "NCC", "Employee": "NV nội bộ"}
		return m.get(dt, "Khác")
