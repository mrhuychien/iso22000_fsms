import frappe
from frappe.tests.utils import FrappeTestCase


class TestFSMSSettings(FrappeTestCase):
	def test_singleton_exists(self):
		settings = frappe.get_single("FSMS Settings")
		self.assertIsNotNone(settings)
