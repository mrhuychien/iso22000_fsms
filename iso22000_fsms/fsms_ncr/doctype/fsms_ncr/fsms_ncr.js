frappe.ui.form.on("FSMS NCR", {
	refresh(frm) {
		// Lifecycle helpers: only show "Open new NCR" when this one is in Chuyển tiếp.
		if (frm.doc.workflow_state === "Chuyển tiếp" && !frm.doc.reissued_to_ncr) {
			frm.add_custom_button(__("Mở phiếu mới"), () => {
				frappe.new_doc("FSMS NCR", {
					reissued_from_ncr: frm.doc.name,
					ncr_source: frm.doc.ncr_source,
					severity: frm.doc.severity,
					affected_department: frm.doc.affected_department,
				});
			});
		}
	},
});
