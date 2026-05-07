"""Controller for FSMS Audit Execution — phiên đánh giá thực tế (BM.01.06 filled)."""

import frappe
from frappe import _
from frappe.model.document import Document


class FSMSAuditExecution(Document):
	def validate(self):
		self._validate_findings_have_descriptions()
		self._copy_template_questions_if_empty()

	def _validate_findings_have_descriptions(self):
		for f in (self.findings or []):
			if f.finding_type and not f.finding_description:
				frappe.throw(_("Finding row #{0}: phải nhập mô tả").format(f.idx))

	def _copy_template_questions_if_empty(self):
		"""Pull checklist questions from the linked template into `responses`
		on first save (when responses is empty)."""
		if self.checklist_used and not self.responses:
			tpl = frappe.get_doc("FSMS Audit Checklist Template", self.checklist_used)
			for item in (tpl.items or []):
				self.append("responses", {
					"seq": item.seq,
					"clause": item.clause,
					"question": item.question,
					"expected_evidence": item.expected_evidence,
				})
