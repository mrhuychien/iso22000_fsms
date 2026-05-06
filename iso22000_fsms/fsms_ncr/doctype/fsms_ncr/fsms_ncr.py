"""Controller for FSMS NCR — Phiếu yêu cầu hành động khắc phục (BM.01.07)."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class FSMSNCR(Document):
	"""NCR — central CAR/CAP DocType per design §4.1.

	Workflow: Đề xuất → Phân tích → Chờ phê duyệt → Đang thực hiện →
	          Đang xác minh → Đã đóng | Chuyển tiếp.
	"""

	def validate(self):
		self._fill_default_dates()
		self._validate_completion_dates()
		self._enforce_reissue_link_when_failed()

	def fsms_validate(self):
		"""Hook used by `iso22000_fsms.fsms_ncr.api.validate_ncr`."""
		self.validate()

	def _fill_default_dates(self):
		if self.requestor and not self.requestor_date:
			self.requestor_date = self.ncr_date or today()

	def _validate_completion_dates(self):
		if self.proposed_completion_date and self.ncr_date:
			if getdate(self.proposed_completion_date) < getdate(self.ncr_date):
				frappe.throw(_("Ngày đề xuất hoàn thành phải sau ngày phát sinh"))
		if self.actual_completion_date and self.proposed_completion_date:
			# Inform-only: allow late completion but flag in comments below.
			pass

	def _enforce_reissue_link_when_failed(self):
		# When verification fails, the auto-reissue is created by the workflow
		# state-change hook in api.handle_state_changes; here we just guard saves.
		if self.verification_outcome == "Không đạt" and self.workflow_state == "Đã đóng":
			frappe.throw(_("Không thể đóng phiếu khi kết quả xác minh là 'Không đạt'"))

	def on_submit(self):
		# Default the workflow_state if not set yet (Frappe sometimes saves before workflow apply).
		if not self.workflow_state:
			self.db_set("workflow_state", "Đang thực hiện")
