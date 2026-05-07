"""Tests for Jinja helpers in iso22000_fsms.utils."""

from frappe.tests.utils import FrappeTestCase
from iso22000_fsms.utils import format_vnd, format_vn_date, signature_or_blank


class TestUtils(FrappeTestCase):
	def test_format_vnd_basic(self):
		self.assertEqual(format_vnd(1234567), "1.234.567 ₫")
		self.assertEqual(format_vnd(0), "0 ₫")
		self.assertEqual(format_vnd(1500), "1.500 ₫")

	def test_format_vnd_empty(self):
		self.assertEqual(format_vnd(None), "")
		self.assertEqual(format_vnd(""), "")

	def test_format_vnd_handles_string_input(self):
		self.assertEqual(format_vnd("12345"), "12.345 ₫")

	def test_format_vnd_invalid_input(self):
		# Non-numeric string returns the string itself
		self.assertEqual(format_vnd("not-a-number"), "not-a-number")

	def test_format_vn_date_basic(self):
		# Output format: "ngày DD tháng MM năm YYYY"
		result = format_vn_date("2026-05-07")
		self.assertIn("năm 2026", result)
		self.assertIn("tháng 05", result)
		self.assertIn("ngày 07", result)

	def test_format_vn_date_empty(self):
		self.assertEqual(format_vn_date(None), "")
		self.assertEqual(format_vn_date(""), "")

	def test_signature_or_blank_no_employee(self):
		self.assertEqual(signature_or_blank(None), "")
		self.assertEqual(signature_or_blank(""), "")

	def test_signature_or_blank_unknown_employee(self):
		# Non-existent Employee returns empty string (not raise)
		self.assertEqual(signature_or_blank("DOES-NOT-EXIST-12345"), "")
