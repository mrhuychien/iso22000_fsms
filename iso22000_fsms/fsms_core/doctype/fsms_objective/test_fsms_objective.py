import frappe
from frappe.tests.utils import FrappeTestCase


class TestFSMSObjective(FrappeTestCase):
	def test_create_objective(self):
		doc = frappe.get_doc(
			{
				"doctype": "FSMS Objective",
				"naming_series": "OBJ.{YYYY}.-.###",
				"objective_year": 2026,
				"objective_text": "Test objective",
				"status": "Đang theo dõi",
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertTrue(doc.name.startswith("OBJ"))
		doc.delete(ignore_permissions=True)
