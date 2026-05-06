import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate, today


REVIEW_FREQ_MONTHS = {
	"Hàng tháng": 1,
	"Hàng quý": 3,
	"Năm": 12,
}


class FSMSObjective(Document):
	"""Mục tiêu ATTP — multi-record có review định kỳ.

	Workflow: Draft → Pending Review → Approved → Closed (§04 5.3).
	"""

	def validate(self):
		self._validate_year()
		self._validate_target_actual()
		self._compute_next_review_date()

	def _validate_year(self):
		if self.objective_year and self.objective_year < 2000:
			frappe.throw(_("Năm mục tiêu không hợp lệ"))

	def _validate_target_actual(self):
		if self.target_value is not None and flt(self.target_value) < 0:
			frappe.throw(_("Giá trị mục tiêu không được âm"))
		if self.actual_value is not None and flt(self.actual_value) < 0:
			frappe.throw(_("Giá trị thực tế không được âm"))

	def _compute_next_review_date(self):
		# Suy ra ngày soát xét tiếp theo từ tần suất + ngày soát xét gần nhất
		if not (self.review_frequency and self.last_review_date):
			return
		months = REVIEW_FREQ_MONTHS.get(self.review_frequency)
		if not months:
			return
		self.next_review_date = add_months(getdate(self.last_review_date), months)

	def mark_reviewed(self):
		"""Helper được gọi từ Workflow Action 'Review pass'.

		Stamp last_review_date = today và auto đánh giá Đạt/Không đạt theo target.
		"""
		self.last_review_date = today()
		if self.target_value is not None and self.actual_value is not None:
			self.status = "Đạt" if flt(self.actual_value) >= flt(self.target_value) else "Không đạt"
