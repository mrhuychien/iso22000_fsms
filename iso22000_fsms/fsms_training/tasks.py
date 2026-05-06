"""Scheduled tasks for fsms_training."""

import frappe


def training_compliance_digest():
	"""Weekly — email digest of employees missing required courses."""
	# Placeholder — full Competency Matrix join is implemented when the matrix DocType is finalized.
	frappe.publish_realtime(
		event="fsms_training_digest",
		message={"note": "Weekly training compliance digest tick"},
	)
