"""Tests for Recall Event auto-suggestion + recovery rate calculation per §17.1."""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestRecallFastTrack(FrappeTestCase):
	def _create_event(self, **fields):
		defaults = dict(
			doctype="FSMS Recall Event",
			event_date=frappe.utils.today(),
			trigger_source="Phát hiện nội bộ",
			defect_severity="Cấp 2",
			recall_level="B",
			defect_description="Test recall — minor contamination",
		)
		defaults.update(fields)
		return frappe.get_doc(defaults).insert(ignore_permissions=True)

	def test_auto_suggest_recall_level_from_severity(self):
		"""Cấp 1 → A, Cấp 2 → B, Cấp 3 → C (when recall_level not yet set)."""
		from iso22000_fsms.fsms_recall.doctype.fsms_recall_event.fsms_recall_event import FSMSRecallEvent
		# Build a doc but bypass insertion
		event = frappe.new_doc("FSMS Recall Event")
		event.defect_severity = "Cấp 1"
		event.event_date = frappe.utils.today()
		event.trigger_source = "Khiếu nại KH"
		event.defect_description = "T1"
		event._auto_suggest_recall_level()
		self.assertEqual(event.recall_level, "A")

		event2 = frappe.new_doc("FSMS Recall Event")
		event2.defect_severity = "Cấp 3"
		event2.event_date = frappe.utils.today()
		event2.trigger_source = "Phát hiện nội bộ"
		event2.defect_description = "T3"
		event2._auto_suggest_recall_level()
		self.assertEqual(event2.recall_level, "C")

	def test_recovery_rate_calculation(self):
		event = self._create_event()
		event.append("affected_batches", {
			"batch": "DUMMY-BATCH-001",
			"total_produced_qty": 1000,
			"recovered_qty": 750,
		})
		event.save(ignore_permissions=True)
		self.assertEqual(event.affected_batches[0].recovery_rate_pct, 75.0)

	def test_distribution_validation_blocks_overrecovery(self):
		event = self._create_event()
		event.append("distributions", {"customer": "DUMMY-CUST", "distributed_qty": 100, "recovered_qty": 200})
		with self.assertRaises(frappe.exceptions.ValidationError):
			event.save(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()
