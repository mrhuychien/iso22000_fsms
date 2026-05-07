"""Tests for FSMS Risk Register scoring per design §08."""

import frappe
from frappe.tests.utils import FrappeTestCase
from iso22000_fsms.fsms_context_risk.doctype.fsms_risk_register.fsms_risk_register import risk_level_for


class TestRiskRegister(FrappeTestCase):
	def test_risk_level_low_threshold(self):
		# total ≤ 9 → "Theo dõi"
		self.assertEqual(risk_level_for(4), "Theo dõi")
		self.assertEqual(risk_level_for(9), "Theo dõi")

	def test_risk_level_medium_threshold(self):
		# 10–11 → "Kiểm soát"
		self.assertEqual(risk_level_for(10), "Kiểm soát")
		self.assertEqual(risk_level_for(11), "Kiểm soát")

	def test_risk_level_high_threshold(self):
		# ≥ 12 → "Ứng phó kịp thời"
		self.assertEqual(risk_level_for(12), "Ứng phó kịp thời")
		self.assertEqual(risk_level_for(16), "Ứng phó kịp thời")

	def test_total_score_computation(self):
		risk = frappe.new_doc("FSMS Risk Register")
		risk.risk_year = 2026
		risk.risk_description = "Test"
		risk.risk_category = "ATTP"
		risk.score_a_likelihood = 3
		risk.score_b_consequence = 2
		risk.score_c_severity = 4
		risk.score_d_detectability = 1
		risk._compute_total_and_level()
		self.assertEqual(risk.total_score, 10)
		self.assertEqual(risk.risk_level, "Kiểm soát")

	def test_score_dimension_validation(self):
		risk = frappe.new_doc("FSMS Risk Register")
		risk.risk_year = 2026
		risk.risk_description = "Test"
		risk.risk_category = "ATTP"
		risk.score_a_likelihood = 5  # invalid (>4)
		with self.assertRaises(frappe.exceptions.ValidationError):
			risk._validate_score_dimensions()

	def tearDown(self):
		frappe.db.rollback()
