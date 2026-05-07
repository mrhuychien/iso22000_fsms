"""Controller for FSMS Calibration Record — phiếu kết quả hiệu chuẩn (BM.06.05)."""

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate


class FSMSCalibrationRecord(Document):
	def validate(self):
		self._compute_next_due_date()

	def _compute_next_due_date(self):
		if not self.cal_date or not self.validity_period_months:
			return
		self.next_cal_due_date = add_months(getdate(self.cal_date), int(flt(self.validity_period_months)))

	def on_submit(self):
		"""Update Measurement Equipment with new last/next calibration date."""
		if not self.equipment:
			return
		frappe.db.set_value("FSMS Measurement Equipment", self.equipment, {
			"last_calibration_date": self.cal_date,
			"next_calibration_date": self.next_cal_due_date,
			"current_status": "Hợp chuẩn" if self.cal_result == "Đạt" else (
				"Hết hạn" if self.cal_result == "Không đạt" else "Hợp chuẩn"
			),
		})
