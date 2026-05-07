"""Controller for FSMS Recall Report — Báo cáo thu hồi (BM.02.02)."""

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FSMSRecallReport(Document):
	def validate(self):
		self._compute_recovery_rate()
		self._aggregate_from_event()

	def _compute_recovery_rate(self):
		affected = flt(self.total_affected_qty)
		recovered = flt(self.total_recovered_qty)
		self.total_recovery_rate_pct = round(100.0 * recovered / affected, 2) if affected else 0

	def _aggregate_from_event(self):
		"""Pre-fill totals from the linked Recall Event's affected_batches."""
		if not (self.recall_event and not (self.total_affected_qty or self.total_recovered_qty)):
			return
		event = frappe.get_doc("FSMS Recall Event", self.recall_event)
		self.total_affected_qty = sum(flt(r.total_produced_qty) for r in event.affected_batches)
		self.total_recovered_qty = sum(flt(r.recovered_qty) for r in event.affected_batches)
		self._compute_recovery_rate()

	def on_submit(self):
		if self.recall_event:
			frappe.db.set_value("FSMS Recall Event", self.recall_event, "recall_report", self.name)
