"""Whitelisted REST endpoints for the iso22000_fsms app.

Module-specific endpoints live in <module>/api.py. This file is reserved for
cross-cutting endpoints (dashboard aggregation, global search, health checks).
"""

import frappe


@frappe.whitelist()
def ping():
	return {"app": "iso22000_fsms", "status": "ok"}
