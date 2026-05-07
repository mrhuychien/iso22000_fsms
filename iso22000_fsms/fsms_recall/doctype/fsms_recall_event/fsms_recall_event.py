"""Controller for FSMS Recall Event — sự kiện thu hồi sản phẩm (QT 02 §5.1)."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


SEVERITY_TO_RECALL_LEVEL = {
	"Cấp 1": "A",
	"Cấp 2": "B",
	"Cấp 3": "C",
}


class FSMSRecallEvent(Document):
	"""Recall Event — central object for QT 02.

	Workflow: Phát sinh → Lập kế hoạch → Đang thu hồi → Bảo quản → Báo cáo → Đóng.
	"""

	def validate(self):
		self._auto_suggest_recall_level()
		self._compute_recovery_metrics()
		self._validate_distribution_quantities()

	def _auto_suggest_recall_level(self):
		if self.defect_severity and not self.recall_level:
			self.recall_level = SEVERITY_TO_RECALL_LEVEL.get(self.defect_severity)

	def _compute_recovery_metrics(self):
		for row in (self.affected_batches or []):
			produced = flt(row.total_produced_qty) or 0
			recovered = flt(row.recovered_qty) or 0
			row.recovery_rate_pct = round(100.0 * recovered / produced, 2) if produced else 0

	def _validate_distribution_quantities(self):
		for row in (self.distributions or []):
			distributed = flt(row.distributed_qty)
			recovered = flt(row.recovered_qty)
			if recovered > distributed:
				frappe.throw(_("Phân phối {0}: SL thu hồi không thể lớn hơn SL đã phân phối").format(row.customer))
			row.remaining_qty = distributed - recovered

	def on_submit(self):
		if not self.workflow_state:
			self.db_set("workflow_state", "Lập kế hoạch")

	@frappe.whitelist()
	def aggregate_recovery_summary(self) -> dict:
		"""Used by Print Format / dashboards: total produced/recovered/remaining."""
		total_produced = sum(flt(r.total_produced_qty) for r in self.affected_batches)
		total_recovered = sum(flt(r.recovered_qty) for r in self.affected_batches)
		return {
			"total_produced": total_produced,
			"total_recovered": total_recovered,
			"recovery_rate_pct": round(100.0 * total_recovered / total_produced, 2) if total_produced else 0,
		}
