import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class FSMSPolicy(Document):
	"""Chính sách ATTP (Single).

	Workflow: Draft → Reviewed → Approved → Published → Obsolete (§04 5.2 — giống Manual).
	"""

	def validate(self):
		if self.effective_date and self.next_review_date:
			if getdate(self.next_review_date) < getdate(self.effective_date):
				frappe.throw(_("Ngày soát xét tiếp theo phải sau ngày hiệu lực"))

	def on_update(self):
		if self.has_value_changed("workflow_state") and self.workflow_state == "Published":
			self.revision_no = (self.revision_no or 0) + 1
			if not self.effective_date:
				self.effective_date = today()
