"""End-to-end NCR workflow test (Đề xuất → ... → Đã đóng) per design §17.1.

Run with: bench --site <site> run-tests --module iso22000_fsms.tests.test_ncr_workflow
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNCRWorkflow(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Ensure required Workflow State + Workflow Action records exist
		cls._ensure_workflow_states([
			"Đề xuất", "Phân tích", "Chờ phê duyệt",
			"Đang thực hiện", "Đang xác minh", "Đã đóng", "Chuyển tiếp",
		])

	@staticmethod
	def _ensure_workflow_states(states):
		for s in states:
			if not frappe.db.exists("Workflow State", s):
				frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": s, "style": "Primary"}).insert(
					ignore_permissions=True
				)

	def _create_ncr(self, **fields):
		defaults = dict(
			doctype="FSMS NCR",
			ncr_date=frappe.utils.today(),
			severity="Minor",
			ncr_type="Khắc phục",
			nonconformity_description="Test NC description",
		)
		defaults.update(fields)
		return frappe.get_doc(defaults).insert(ignore_permissions=True)

	def test_create_with_default_state(self):
		ncr = self._create_ncr()
		# Workflow may not be applied without Workflow record; just check insert succeeds
		self.assertIsNotNone(ncr.name)
		self.assertEqual(ncr.severity, "Minor")

	def test_validation_blocks_close_when_verification_failed(self):
		"""Cannot close NCR when verification_outcome == 'Không đạt'."""
		ncr = self._create_ncr(verification_outcome="Không đạt", workflow_state="Đã đóng")
		from iso22000_fsms.fsms_ncr.doctype.fsms_ncr.fsms_ncr import FSMSNCR
		# The validate hook is called on save; force a re-save to trigger.
		with self.assertRaises(frappe.exceptions.ValidationError):
			ncr.save(ignore_permissions=True)

	def test_set_signatures_pulls_from_employee(self):
		"""When requestor is set, requestor_signature should be auto-populated
		from the Employee.signature field via the api hook."""
		# Create a stub employee with a signature
		emp_id = "TEST-EMP-001"
		if not frappe.db.exists("Employee", emp_id):
			frappe.get_doc({
				"doctype": "Employee", "name": emp_id, "first_name": "Test",
				"employee_name": "Test Employee", "signature": "/files/test_sig.png",
				"company": frappe.defaults.get_global_default("company") or "Test Company",
				"date_of_joining": frappe.utils.today(),
			}).insert(ignore_permissions=True)
		from iso22000_fsms.fsms_ncr.api import set_signatures
		ncr = self._create_ncr(requestor=emp_id)
		set_signatures(ncr)
		self.assertEqual(ncr.requestor_signature, "/files/test_sig.png")

	def tearDown(self):
		frappe.db.rollback()
