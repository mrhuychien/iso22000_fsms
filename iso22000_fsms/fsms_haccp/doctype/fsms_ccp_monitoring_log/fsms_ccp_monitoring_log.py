"""Controller for FSMS CCP Monitoring Log — sổ giám sát CCP.

The validate hook is also wired through `iso22000_fsms.fsms_haccp.api.check_ccp_limits`
which sets `is_within_limit` from the parent HACCP CCP row's acceptance bounds.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class FSMSCCPMonitoringLog(Document):
	def validate(self):
		# Parent api.check_ccp_limits already runs via hooks. This local check is a
		# safety net for cases where the log is created directly via API call.
		if self.measurement_value is None or self.measurement_value == "":
			frappe.throw(_("Phải nhập giá trị đo"))

	def on_submit(self):
		# When out-of-limit, the api.escalate_if_breach hook auto-creates an NCR.
		# Here we verify the user filled in corrective_action_taken.
		if not self.is_within_limit and not self.corrective_action_taken:
			frappe.msgprint(_("Cảnh báo: CCP ngoài giới hạn nhưng chưa ghi hành động khắc phục."), alert=True)
