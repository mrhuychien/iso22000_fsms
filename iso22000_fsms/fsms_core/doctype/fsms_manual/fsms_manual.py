import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class FSMSManual(Document):
	"""Sổ tay ATTP (Single).

	Workflow: Draft → Reviewed → Approved → Published → Obsolete (§04 5.1).
	Mỗi lần publish, snapshot fields hiện tại vào row mới của revision_history.
	"""

	def validate(self):
		self._validate_review_dates()

	def _validate_review_dates(self):
		if self.effective_date and self.next_review_date:
			if getdate(self.next_review_date) < getdate(self.effective_date):
				frappe.throw(_("Ngày soát xét tiếp theo phải sau ngày hiệu lực"))

	def on_update(self):
		# Workflow handler: khi state chuyển sang Published, đẩy snapshot vào revision_history.
		if self.has_value_changed("workflow_state") and self.workflow_state == "Published":
			self._snapshot_revision()

	def _snapshot_revision(self):
		self.revision_no = (self.revision_no or 0) + 1
		if not self.effective_date:
			self.effective_date = today()
		self.append("revision_history", {
			"revision_no": self.revision_no,
			"revision_date": self.effective_date,
			"summary": _("Phát hành phiên bản {0}").format(self.version_no or self.revision_no),
			"prepared_by": self.prepared_by,
			"reviewed_by": self.reviewed_by,
			"approved_by": self.approved_by,
		})
