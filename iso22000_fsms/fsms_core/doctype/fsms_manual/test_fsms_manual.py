import frappe
from frappe.tests.utils import FrappeTestCase


class TestFSMSManual(FrappeTestCase):
	def test_singleton_loads(self):
		manual = frappe.get_single("FSMS Manual")
		self.assertIsNotNone(manual)
