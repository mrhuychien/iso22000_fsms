from frappe.model.document import Document


class FSMSManual(Document):
	def validate(self):
		# Workflow: Draft → Reviewed → Approved → Published → Obsolete (§04 5.1)
		pass
