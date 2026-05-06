"""Doc-event handlers for fsms_haccp (hooks.doc_events)."""

import frappe
from frappe.utils import flt, today


def check_ccp_limits(doc, method=None):
	"""Validate hook on FSMS CCP Monitoring Log — flag out-of-limit measurements."""
	if not doc.get("ccp"):
		return
	value = flt(doc.get("measurement_value"))
	limit_min, limit_max = frappe.db.get_value(
		"FSMS HACCP CCP", doc.ccp, ["acceptance_min", "acceptance_max"]
	) or (None, None)
	within = True
	if limit_min is not None and value < flt(limit_min):
		within = False
	if limit_max is not None and value > flt(limit_max):
		within = False
	doc.is_within_limit = 1 if within else 0


def escalate_if_breach(doc, method=None):
	"""On CCP Monitoring Log submit — auto-create NCR if outside critical limit."""
	if doc.get("is_within_limit") or doc.get("linked_ncr"):
		return
	ncr = frappe.get_doc({
		"doctype": "FSMS NCR",
		"ncr_date": today(),
		"ncr_source": "CCP_FAIL",
		"source_reference_doctype": "FSMS CCP Monitoring Log",
		"source_reference_name": doc.name,
		"severity": "Critical",
		"ncr_type": "Khắc phục",
		"nonconformity_description": frappe._("CCP {0} ngoài giới hạn ({1}").format(
			doc.ccp, doc.measurement_value
		),
	})
	ncr.insert(ignore_permissions=True)
	doc.db_set("linked_ncr", ncr.name)


def sync_to_item_on_publish(doc, method=None):
	"""When HACCP Plan moves to Published — flag the linked Item as HACCP-controlled."""
	if doc.workflow_state == "Published" and doc.get("item"):
		frappe.db.set_value("Item", doc.item, "fsms_haccp_plan", doc.name)


def sync_haccp_plan_link(doc, method=None):
	"""Item before_save hook — keep `Item.fsms_haccp_plan` consistent."""
	# Placeholder — real reverse-lookup happens on HACCP Plan publish.
	return
