"""Controller for FSMS Traceability Drill — diễn tập truy xuất (QT 09)."""

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class FSMSTraceabilityDrill(Document):
	def validate(self):
		self._compute_time_taken()
		self._compute_is_within_target()
		self._derive_outcome()

	def _compute_time_taken(self):
		if not (self.start_time and self.actual_completion_time):
			return
		delta = get_datetime(self.actual_completion_time) - get_datetime(self.start_time)
		self.time_taken_minutes = int(delta.total_seconds() // 60)

	def _compute_is_within_target(self):
		if not (self.start_time and self.target_completion_time and self.actual_completion_time):
			return
		self.is_within_target = (
			get_datetime(self.actual_completion_time) <= get_datetime(self.target_completion_time)
		)

	def _derive_outcome(self):
		"""Outcome = Đạt iff within target AND has both backward + forward links."""
		if self.drill_outcome:  # respect manual override
			return
		has_links = bool(self.backward_links and self.forward_links)
		if self.is_within_target and has_links:
			self.drill_outcome = "Đạt — đúng giờ + đầy đủ"
		elif has_links:
			self.drill_outcome = "Đạt một phần"
		else:
			self.drill_outcome = "Không đạt"

	def on_submit(self):
		"""Update Traceability Settings.last_drill_date + result."""
		if not frappe.db.exists("DocType", "FSMS Traceability Settings"):
			return
		frappe.db.set_value("FSMS Traceability Settings", "FSMS Traceability Settings", {
			"last_drill_date": self.drill_date,
			"last_drill_result": "Đạt" if self.drill_outcome.startswith("Đạt") else "Không đạt",
		})
