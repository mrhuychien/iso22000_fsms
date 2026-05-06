import frappe
from frappe import _
from frappe.model.document import Document


class FSMSSettings(Document):
	def validate(self):
		if not self.company_name:
			frappe.throw(_("Tên công ty không được để trống"))
		if (self.retention_years_default or 0) < 1:
			frappe.throw(_("Số năm lưu hồ sơ mặc định phải >= 1"))
		if (self.mandatory_drill_frequency_months or 0) < 1:
			frappe.throw(_("Tần suất diễn tập phải >= 1 tháng"))
