"""Controller for FSMS Fire Equipment master."""

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class FSMSFireEquipment(Document):
	def validate(self):
		self._auto_status_from_dates()

	def _auto_status_from_dates(self):
		if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			self.status = "Hết hạn"
		elif self.next_inspection_date and getdate(self.next_inspection_date) < getdate(today()):
			self.status = "Cần kiểm tra"
