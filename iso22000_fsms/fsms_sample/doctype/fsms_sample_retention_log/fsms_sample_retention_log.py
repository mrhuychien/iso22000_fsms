"""Controller for FSMS Sample Retention Log — sổ lưu mẫu (QĐ.01)."""

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate


class FSMSSampleRetentionLog(Document):
	def validate(self):
		self._compute_expected_disposal_date()

	def _compute_expected_disposal_date(self):
		"""expected_disposal_date = sample_date + retention_period from policy Single."""
		if self.expected_disposal_date or not self.sample_date:
			return
		if not frappe.db.exists("DocType", "FSMS Sample Retention Policy"):
			return
		months = frappe.db.get_single_value("FSMS Sample Retention Policy", "retention_period_months") or 12
		self.expected_disposal_date = add_months(getdate(self.sample_date), int(months))
