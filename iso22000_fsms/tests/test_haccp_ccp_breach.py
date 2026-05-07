"""Tests for HACCP Plan hazard analysis + CCP/OPRP derivation per §17.1."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHACCPPlan(FrappeTestCase):
	def _make_plan(self):
		plan = frappe.new_doc("FSMS HACCP Plan")
		plan.item = "DUMMY-ITEM-001"
		plan.plan_version = "1.0"
		plan.effective_date = frappe.utils.today()
		return plan

	def test_risk_level_is_severity_times_likelihood(self):
		plan = self._make_plan()
		plan.append("hazard_analysis", {
			"hazard_type": "Sinh học", "hazard_description": "Salmonella",
			"severity": 4, "likelihood": 3,
		})
		plan._compute_hazard_risk_levels()
		self.assertEqual(plan.hazard_analysis[0].risk_level, 12)
		self.assertEqual(plan.hazard_analysis[0].is_significant, 1)

	def test_decision_tree_q1_no_means_not_significant(self):
		plan = self._make_plan()
		plan.append("hazard_analysis", {"hazard_type": "Sinh học", "hazard_description": "X",
		                                "decision_tree_q1": 0})
		plan._derive_ccp_oprp_flags()
		self.assertEqual(plan.hazard_analysis[0].is_ccp, 0)
		self.assertEqual(plan.hazard_analysis[0].is_oprp, 0)

	def test_decision_tree_q1q2_yes_means_ccp(self):
		plan = self._make_plan()
		plan.append("hazard_analysis", {"hazard_type": "Sinh học", "hazard_description": "X",
		                                "decision_tree_q1": 1, "decision_tree_q2": 1})
		plan._derive_ccp_oprp_flags()
		self.assertEqual(plan.hazard_analysis[0].is_ccp, 1)
		self.assertEqual(plan.hazard_analysis[0].is_oprp, 0)

	def test_decision_tree_q1y_q2n_q3y_means_oprp(self):
		plan = self._make_plan()
		plan.append("hazard_analysis", {"hazard_type": "Hóa học", "hazard_description": "X",
		                                "decision_tree_q1": 1, "decision_tree_q2": 0, "decision_tree_q3": 1})
		plan._derive_ccp_oprp_flags()
		self.assertEqual(plan.hazard_analysis[0].is_ccp, 0)
		self.assertEqual(plan.hazard_analysis[0].is_oprp, 1)

	def tearDown(self):
		frappe.db.rollback()
