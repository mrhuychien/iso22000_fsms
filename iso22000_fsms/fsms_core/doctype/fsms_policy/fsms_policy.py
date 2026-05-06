from frappe.model.document import Document


class FSMSPolicy(Document):
	def validate(self):
		# Workflow giống FSMS Manual (§04 5.2)
		pass
