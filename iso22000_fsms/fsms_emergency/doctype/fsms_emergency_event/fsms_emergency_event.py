"""Controller for FSMS Emergency Event."""

import frappe
from frappe import _
from frappe.model.document import Document


class FSMSEmergencyEvent(Document):
	def validate(self):
		if self.casualties and int(self.casualties) > 0 and not self.actions_taken:
			frappe.throw(_("Phải ghi rõ hành động đã thực hiện khi có thương tật/tử vong"))

	def on_submit(self):
		if not self.workflow_state:
			self.db_set("workflow_state", "Đã xử lý")
