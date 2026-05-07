"""Tests for FSMS Supplier Evaluation grade calculation per design §10."""

import frappe
from frappe.tests.utils import FrappeTestCase
from iso22000_fsms.fsms_supplier.doctype.fsms_supplier_evaluation.fsms_supplier_evaluation import FSMSSupplierEvaluation


class TestSupplierEvaluation(FrappeTestCase):
	def test_grade_a_threshold(self):
		self.assertEqual(FSMSSupplierEvaluation._grade_for(85), "A")
		self.assertEqual(FSMSSupplierEvaluation._grade_for(80), "A")

	def test_grade_b_threshold(self):
		self.assertEqual(FSMSSupplierEvaluation._grade_for(70), "B")
		self.assertEqual(FSMSSupplierEvaluation._grade_for(65), "B")

	def test_grade_c_threshold(self):
		self.assertEqual(FSMSSupplierEvaluation._grade_for(55), "C")

	def test_grade_d_threshold(self):
		self.assertEqual(FSMSSupplierEvaluation._grade_for(40), "D")
		self.assertEqual(FSMSSupplierEvaluation._grade_for(0), "D")

	def test_weighted_score_calculation(self):
		eval_doc = frappe.new_doc("FSMS Supplier Evaluation")
		eval_doc.eval_date = frappe.utils.today()
		eval_doc.append("criteria", {"criterion_name": "Quality", "weight": 10, "score": 8})
		eval_doc.append("criteria", {"criterion_name": "Delivery", "weight": 5, "score": 6})
		eval_doc._compute_weighted_scores()
		self.assertEqual(eval_doc.criteria[0].weighted_score, 80.0)
		self.assertEqual(eval_doc.criteria[1].weighted_score, 30.0)

	def test_total_and_grade_assignment(self):
		eval_doc = frappe.new_doc("FSMS Supplier Evaluation")
		eval_doc.eval_date = frappe.utils.today()
		eval_doc.append("criteria", {"criterion_name": "Q", "weight": 1, "score": 70})
		eval_doc._compute_weighted_scores()
		eval_doc._compute_total_and_grade()
		self.assertEqual(eval_doc.total_score, 70.0)
		self.assertEqual(eval_doc.grade, "B")

	def tearDown(self):
		frappe.db.rollback()
