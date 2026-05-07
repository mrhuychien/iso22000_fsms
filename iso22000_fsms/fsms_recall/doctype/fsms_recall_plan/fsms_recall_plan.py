"""Controller for FSMS Recall Plan — Kế hoạch thu hồi (BM.02.01)."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class FSMSRecallPlan(Document):
	def validate(self):
		self._validate_target_completion()
		self._sequence_plan_items()

	def _validate_target_completion(self):
		if self.target_completion_date and getdate(self.target_completion_date) < getdate(today()):
			frappe.msgprint(
				_("Cảnh báo: Hạn hoàn thành đã ở quá khứ. Hãy xác nhận anh muốn lưu."),
				alert=True,
			)

	def _sequence_plan_items(self):
		for idx, row in enumerate(self.plan_items or [], start=1):
			if not row.seq:
				row.seq = idx

	def on_submit(self):
		if self.recall_event:
			frappe.db.set_value("FSMS Recall Event", self.recall_event, "recall_plan", self.name)
