"""Tests for Traceability Drill outcome computation per §17.1."""

import frappe
from frappe.utils import add_to_date, now_datetime
from frappe.tests.utils import FrappeTestCase


class TestTraceability(FrappeTestCase):
	def _create_drill(self, *, start_offset_min=0, target_offset_min=120, actual_offset_min=90):
		start = now_datetime()
		target = add_to_date(start, minutes=target_offset_min)
		actual = add_to_date(start, minutes=actual_offset_min)
		return frappe.get_doc({
			"doctype": "FSMS Traceability Drill",
			"drill_date": frappe.utils.today(),
			"selected_batch": "DUMMY-BATCH-001",
			"start_time": start,
			"target_completion_time": target,
			"actual_completion_time": actual,
		})

	def test_within_target_when_actual_before_target(self):
		drill = self._create_drill(actual_offset_min=90)  # within 120 target
		drill._compute_time_taken()
		drill._compute_is_within_target()
		self.assertTrue(drill.is_within_target)
		self.assertEqual(drill.time_taken_minutes, 90)

	def test_outcome_full_when_within_target_and_links_present(self):
		drill = self._create_drill(actual_offset_min=80)
		drill.append("backward_links", {"target_batch": "DUMMY-BATCH-001", "material_item": "X"})
		drill.append("forward_links", {"target_batch": "DUMMY-BATCH-001", "customer": "Y"})
		drill._compute_time_taken()
		drill._compute_is_within_target()
		drill._derive_outcome()
		self.assertTrue(drill.drill_outcome.startswith("Đạt"))

	def test_outcome_partial_when_overran_target(self):
		drill = self._create_drill(actual_offset_min=180)  # 60 min overrun
		drill.append("backward_links", {"target_batch": "DUMMY-BATCH-001", "material_item": "X"})
		drill.append("forward_links", {"target_batch": "DUMMY-BATCH-001", "customer": "Y"})
		drill._compute_time_taken()
		drill._compute_is_within_target()
		drill._derive_outcome()
		self.assertEqual(drill.drill_outcome, "Đạt một phần")

	def test_outcome_fail_when_no_links(self):
		drill = self._create_drill(actual_offset_min=80)
		drill._compute_time_taken()
		drill._compute_is_within_target()
		drill._derive_outcome()
		self.assertEqual(drill.drill_outcome, "Không đạt")

	def tearDown(self):
		frappe.db.rollback()
