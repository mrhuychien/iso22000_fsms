"""Controller for FSMS Audit Summary (BM.01.09) — auto-aggregate from Audit Executions."""

import frappe
from frappe.model.document import Document


class FSMSAuditSummary(Document):
	def validate(self):
		self._aggregate_from_executions()

	def _aggregate_from_executions(self):
		if not self.summary_year:
			return
		year_start = f"{self.summary_year}-01-01"
		year_end = f"{self.summary_year}-12-31"
		executions = frappe.get_all(
			"FSMS Audit Execution",
			filters={"audit_date": ("between", [year_start, year_end]), "docstatus": 1},
			fields=["name"],
		)
		total = len(executions)
		major = minor = obs = 0
		for exec_row in executions:
			findings = frappe.get_all(
				"FSMS Audit Finding",
				filters={"parent": exec_row.name, "parenttype": "FSMS Audit Execution"},
				fields=["finding_type", "linked_ncr"],
			)
			for f in findings:
				if f.finding_type == "NC Major":
					major += 1
				elif f.finding_type == "NC Minor":
					minor += 1
				elif f.finding_type == "Observation":
					obs += 1
		self.total_audits = total
		self.total_nc_major = major
		self.total_nc_minor = minor
		self.total_obs = obs
		self._compute_closure_status()

	def _compute_closure_status(self):
		"""Count linked NCRs that are closed on time / late / still open."""
		if not self.summary_year:
			return
		year_start = f"{self.summary_year}-01-01"
		ncrs = frappe.get_all(
			"FSMS NCR",
			filters={"ncr_source": "AUDIT", "ncr_date": (">=", year_start)},
			fields=["name", "workflow_state", "proposed_completion_date", "closed_date"],
		)
		on_time = late = still_open = 0
		for n in ncrs:
			if n.workflow_state in ("Đã đóng", "Chuyển tiếp"):
				if n.proposed_completion_date and n.closed_date:
					if frappe.utils.getdate(n.closed_date) <= frappe.utils.getdate(n.proposed_completion_date):
						on_time += 1
					else:
						late += 1
				else:
					on_time += 1
			else:
				still_open += 1
		self.closed_on_time_count = on_time
		self.closed_late_count = late
		self.still_open_count = still_open
