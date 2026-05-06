"""Doc-event handlers for fsms_traceability (hooks.doc_events)."""

import frappe


def register_batch(doc, method=None):
	"""On Batch.after_insert — register the batch in the trace index (placeholder)."""
	# Real implementation would maintain an indexed trace materialization table.
	# For now this is a stable hook surface so Frappe boots without errors.
	return
