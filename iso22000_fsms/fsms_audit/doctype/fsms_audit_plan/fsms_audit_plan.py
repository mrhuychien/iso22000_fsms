"""Controller for FSMS Audit Plan (BM.01.05)."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class FSMSAuditPlan(Document):
	def validate(self):
		self._validate_date_range()

	def _validate_date_range(self):
		if self.audit_date_from and self.audit_date_to:
			if getdate(self.audit_date_to) < getdate(self.audit_date_from):
				frappe.throw(_("Đến ngày phải sau Từ ngày"))
		if self.kickoff_meeting_date and self.audit_date_from:
			if getdate(self.kickoff_meeting_date) > getdate(self.audit_date_from):
				frappe.throw(_("Ngày họp khai mạc không được sau ngày bắt đầu đánh giá"))
