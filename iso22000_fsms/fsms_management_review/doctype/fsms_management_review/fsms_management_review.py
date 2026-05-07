"""Controller for FSMS Management Review (clause 9.3)."""

import frappe
from frappe import _
from frappe.model.document import Document


class FSMSManagementReview(Document):
	def validate(self):
		self._require_chairperson()
		self._validate_period()

	def _require_chairperson(self):
		if not self.chairperson:
			frappe.msgprint(_("Cảnh báo: chưa có chủ trì cuộc họp"), alert=True)

	def _validate_period(self):
		if self.reviewed_period_from and self.reviewed_period_to:
			from frappe.utils import getdate
			if getdate(self.reviewed_period_to) < getdate(self.reviewed_period_from):
				frappe.throw(_("Kỳ xem xét: 'đến' phải sau 'từ'"))
