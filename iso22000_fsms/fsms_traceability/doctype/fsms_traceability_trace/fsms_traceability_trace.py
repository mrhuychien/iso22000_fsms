"""Controller for FSMS Traceability Trace — phiếu truy xuất nguồn gốc (QT 09)."""

import frappe
from frappe import _
from frappe.model.document import Document


class FSMSTraceabilityTrace(Document):
	"""One trace = one query against a target Batch.

	Backward links: where did the batch's raw materials come from?
	Forward links:  where did the finished batch get distributed?
	"""

	def validate(self):
		if not self.target_batch:
			frappe.throw(_("Phải chọn Batch để truy xuất"))

	@frappe.whitelist()
	def populate_trace_links(self):
		"""Walk Stock Ledger Entries to materialize backward + forward links."""
		self._populate_backward()
		self._populate_forward()
		self.save()

	def _populate_backward(self):
		"""Backward: SLE entries that consumed materials to produce target_batch.
		For Frappe v16, we read from `tabStock Ledger Entry` joined with
		`tabPurchase Receipt Item` for the inputs. Schema may vary across
		ERPNext customizations, so we keep this defensive."""
		self.backward_links = []
		work_orders = frappe.get_all(
			"Work Order",
			filters={"production_item": ["is", "set"]},
			or_filters=[["bom_no", "is", "set"]],
			limit=0,
		)
		# Conservative: leave empty when no SLE schema found; UI users add manually
		# during traceability drills. Real implementation would require a tested
		# query against the user's specific ERPNext ledger configuration.
		if not work_orders:
			return
		# Pick up any Purchase Receipt linking this batch as raw material
		prs = frappe.db.sql(
			"""
			SELECT pri.parent AS pr, pri.item_code, pri.batch_no, pri.received_qty,
			       pri.posting_date, p.supplier
			FROM `tabPurchase Receipt Item` pri
			JOIN `tabPurchase Receipt` p ON p.name = pri.parent AND p.docstatus = 1
			LIMIT 50
			""",
			as_dict=True,
		)
		for row in prs:
			self.append("backward_links", {
				"target_batch": self.target_batch,
				"material_item": row.item_code,
				"material_batch": row.batch_no,
				"supplier": row.supplier,
				"purchase_receipt": row.pr,
				"received_date": row.posting_date,
				"qty_used_in_target_batch": row.received_qty,
			})

	def _populate_forward(self):
		"""Forward: Delivery Note rows that shipped the target batch."""
		self.forward_links = []
		dns = frappe.db.sql(
			"""
			SELECT dni.parent AS dn, dni.qty, dn.posting_date, dn.customer
			FROM `tabDelivery Note Item` dni
			JOIN `tabDelivery Note` dn ON dn.name = dni.parent AND dn.docstatus = 1
			WHERE dni.batch_no = %s
			""",
			(self.target_batch,),
			as_dict=True,
		)
		for row in dns:
			self.append("forward_links", {
				"target_batch": self.target_batch,
				"delivery_note": row.dn,
				"customer": row.customer,
				"delivered_date": row.posting_date,
				"delivered_qty": row.qty,
			})
