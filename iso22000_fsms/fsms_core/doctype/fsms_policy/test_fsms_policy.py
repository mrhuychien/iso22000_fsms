import frappe
from frappe.tests.utils import FrappeTestCase


class TestFSMSPolicy(FrappeTestCase):
	def test_singleton_loads(self):
		policy = frappe.get_single("FSMS Policy")
		self.assertIsNotNone(policy)
