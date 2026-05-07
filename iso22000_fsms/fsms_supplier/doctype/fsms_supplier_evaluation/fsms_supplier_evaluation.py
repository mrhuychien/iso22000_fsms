"""Controller for FSMS Supplier Evaluation — Phiếu đánh giá NCC (BM.07.01)."""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


GRADE_THRESHOLDS = (
	(80, "A"),
	(65, "B"),
	(50, "C"),
)


class FSMSSupplierEvaluation(Document):
	def validate(self):
		self._compute_weighted_scores()
		self._compute_total_and_grade()

	def _compute_weighted_scores(self):
		for c in (self.criteria or []):
			c.weighted_score = round(flt(c.score) * flt(c.weight), 2)

	def _compute_total_and_grade(self):
		total = sum(flt(c.weighted_score) for c in (self.criteria or []))
		self.total_score = round(total, 2)
		self.grade = self._grade_for(total)

	@staticmethod
	def _grade_for(total: float) -> str:
		for threshold, label in GRADE_THRESHOLDS:
			if total >= threshold:
				return label
		return "D"

	def on_submit(self):
		# Reflect the new score onto the linked Supplier Profile (also done by hooks
		# api.update_supplier_profile, but we keep it idempotent here for safety).
		profile = frappe.db.exists("FSMS Supplier Profile", {"supplier": self.supplier})
		if profile:
			frappe.db.set_value("FSMS Supplier Profile", profile, {
				"last_evaluation_date": self.eval_date,
				"last_evaluation_score": self.total_score,
				"last_evaluation_grade": self.grade,
			})
