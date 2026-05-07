"""Controller for FSMS Customer Complaint — khiếu nại khách hàng."""

import frappe
from frappe import _
from frappe.model.document import Document


class FSMSCustomerComplaint(Document):
	def validate(self):
		self._auto_suggest_recall_for_severe_complaints()

	def _auto_suggest_recall_for_severe_complaints(self):
		"""Cấp 1 (life-threatening) auto-flags `auto_create_recall_event`."""
		if self.severity == "Cấp 1" and not self.auto_create_recall_event:
			self.auto_create_recall_event = 1

	def on_submit(self):
		"""Cascade to NCR / Recall via api.handle_complaint (already wired in hooks).
		This controller method just ensures workflow_state defaults."""
		if not self.workflow_state:
			self.db_set("workflow_state", "Đang xử lý")
