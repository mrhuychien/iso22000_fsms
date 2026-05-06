from frappe.model.document import Document


class FSMSObjective(Document):
	def validate(self):
		# Workflow: Draft → Reviewed → Approved → Closed (§04 5.3 — 4 states)
		pass
