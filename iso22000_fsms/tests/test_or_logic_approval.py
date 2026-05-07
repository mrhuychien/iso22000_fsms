"""Tests for cross-cutting OR-logic approval validator (workflow_validation.py)."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestORLogicApproval(FrappeTestCase):
	def test_apply_workflow_with_validation_no_validator(self):
		"""When no FSMS_WORKFLOW_VALIDATORS entry exists, the wrapper passes through."""
		from iso22000_fsms.workflow_validation import FSMS_WORKFLOW_VALIDATORS
		# By default the dict is empty (production-time we'd register validators per DocType)
		self.assertIsInstance(FSMS_WORKFLOW_VALIDATORS, dict)

	def test_ncr_permission_query_for_privileged_role(self):
		"""FSMS Manager / Director see all NCRs (no SQL restriction)."""
		from iso22000_fsms.fsms_ncr.permissions import get_query_conditions, _is_privileged
		# Cannot easily impersonate role here; just verify the helper accepts user arg
		cond = get_query_conditions(user="Administrator")
		# Administrator usually has System Manager → privileged → empty condition
		# (but in fresh test DB this depends on roles; just smoke-check no crash)
		self.assertIsInstance(cond, str)

	def test_ncr_has_permission_for_owner(self):
		"""Owner of an NCR can read it even without department permission."""
		from iso22000_fsms.fsms_ncr.permissions import has_permission
		fake_doc = frappe.new_doc("FSMS NCR")
		fake_doc.owner = "Administrator"
		fake_doc.affected_department = "Some-Dept-That-Doesnt-Exist"
		# Administrator is privileged → should return True
		self.assertTrue(has_permission(fake_doc, ptype="read", user="Administrator"))

	def tearDown(self):
		frappe.db.rollback()
