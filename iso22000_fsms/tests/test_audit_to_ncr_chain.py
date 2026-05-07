"""Test that an Audit Execution with NC findings auto-creates linked NCRs per §17.1."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAuditToNCRChain(FrappeTestCase):
	def test_audit_execution_creates_ncr_for_nc_findings(self):
		from iso22000_fsms.fsms_audit.api import create_ncr_from_findings
		# Build an Audit Execution doc in memory (don't insert — test the hook directly)
		exec_doc = frappe.new_doc("FSMS Audit Execution")
		exec_doc.audit_date = frappe.utils.today()
		exec_doc.auto_create_ncr = 1
		exec_doc.name = "BB.ĐG.TEST.001"
		# Append two findings — one NC Major, one Observation
		exec_doc.append("findings", {
			"finding_type": "NC Major",
			"finding_description": "Critical hygiene gap in mixing area",
			"clause_violated": "ISO 22000 §8.5",
		})
		exec_doc.append("findings", {
			"finding_type": "Observation",
			"finding_description": "Minor labeling inconsistency",
		})
		# Mock db_set on child rows so the hook can stamp linked_ncr.
		# In real usage, the parent must be saved first; here we just verify
		# that the hook walks `findings` and creates NCRs of correct severity.
		create_ncr_from_findings(exec_doc)
		# Findings should have linked_ncr only on the NC Major row
		nc_major_row = exec_doc.findings[0]
		obs_row = exec_doc.findings[1]
		self.assertIsNotNone(nc_major_row.linked_ncr)
		self.assertFalse(obs_row.linked_ncr)
		# Verify the created NCR has correct severity mapping
		ncr = frappe.get_doc("FSMS NCR", nc_major_row.linked_ncr)
		self.assertEqual(ncr.severity, "Major")
		self.assertEqual(ncr.ncr_source, "AUDIT")
		self.assertEqual(ncr.source_reference_doctype, "FSMS Audit Execution")

	def tearDown(self):
		frappe.db.rollback()
