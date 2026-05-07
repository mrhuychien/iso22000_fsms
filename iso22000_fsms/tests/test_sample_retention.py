"""Tests for Sample Retention Log expected_disposal_date computation per §13."""

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_months


class TestSampleRetention(FrappeTestCase):
	def test_expected_disposal_date_from_policy(self):
		# Ensure FSMS Sample Retention Policy Single has retention_period_months
		if frappe.db.exists("DocType", "FSMS Sample Retention Policy"):
			policy = frappe.get_single("FSMS Sample Retention Policy")
			policy.retention_period_months = 6
			policy.flags.ignore_validate = True
			policy.flags.ignore_permissions = True
			policy.save()

		log = frappe.new_doc("FSMS Sample Retention Log")
		log.sample_date = "2026-01-10"
		log.batch = "DUMMY-BATCH-001"
		log.item = "DUMMY-ITEM-001"
		log._compute_expected_disposal_date()
		# Expected: 2026-07-10 (6 months later)
		self.assertEqual(getdate(log.expected_disposal_date), getdate("2026-07-10"))

	def test_expected_disposal_date_skipped_when_already_set(self):
		log = frappe.new_doc("FSMS Sample Retention Log")
		log.sample_date = "2026-01-10"
		log.expected_disposal_date = "2027-01-10"
		log._compute_expected_disposal_date()
		# Should not overwrite existing value
		self.assertEqual(getdate(log.expected_disposal_date), getdate("2027-01-10"))

	def tearDown(self):
		frappe.db.rollback()
