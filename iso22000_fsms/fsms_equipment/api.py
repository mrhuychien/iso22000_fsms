"""Doc-event handlers for fsms_equipment (hooks.doc_events)."""

import frappe
from frappe.utils import today


def escalate_failed_calibration(doc, method=None):
	"""On Calibration Record submit — open NCR if cal_result == 'Không đạt'."""
	if doc.get("cal_result") != "Không đạt" or doc.get("linked_ncr"):
		return
	ncr = frappe.get_doc({
		"doctype": "FSMS NCR",
		"ncr_date": today(),
		"ncr_source": "CAL_FAIL",
		"source_reference_doctype": "FSMS Calibration Record",
		"source_reference_name": doc.name,
		"severity": "Major",
		"ncr_type": "Khắc phục",
		"nonconformity_description": frappe._("Hiệu chuẩn không đạt cho {0}").format(doc.equipment),
	})
	ncr.insert(ignore_permissions=True)
	doc.db_set("linked_ncr", ncr.name)
