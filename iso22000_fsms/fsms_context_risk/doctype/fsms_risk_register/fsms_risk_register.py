"""Controller for FSMS Risk Register — Bảng xác định rủi ro (BM.05.02 / QT 05).

Total = A + B + C + D where each dimension is 1–4. Risk level mapping per QT 05:
   ≤ 9: Theo dõi (low)
   10–11: Kiểm soát (medium)
   ≥ 12: Ứng phó kịp thời (high)
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, today


def risk_level_for(total: int) -> str:
	if total >= 12:
		return "Ứng phó kịp thời"
	if total >= 10:
		return "Kiểm soát"
	return "Theo dõi"


class FSMSRiskRegister(Document):
	def validate(self):
		self._validate_score_dimensions()
		self._compute_total_and_level()
		self._compute_review_dates()

	def _validate_score_dimensions(self):
		for f in ("score_a_likelihood", "score_b_consequence", "score_c_severity", "score_d_detectability"):
			v = self.get(f)
			if v is None or v == "":
				continue
			v = int(flt(v))
			if v < 1 or v > 4:
				frappe.throw(_("{0} phải nằm trong khoảng 1–4").format(f))

	def _compute_total_and_level(self):
		total = sum(flt(self.get(f)) for f in (
			"score_a_likelihood", "score_b_consequence",
			"score_c_severity", "score_d_detectability",
		))
		self.total_score = int(total)
		self.risk_level = risk_level_for(self.total_score)

	def _compute_review_dates(self):
		"""Annual cadence by default; high-risk → 6 months."""
		if not self.last_review_date:
			return
		months = 6 if self.risk_level == "Ứng phó kịp thời" else 12
		self.next_review_date = add_months(getdate(self.last_review_date), months)
