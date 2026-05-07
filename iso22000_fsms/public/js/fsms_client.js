// FSMS — client-side helpers (auto-included via hooks.app_include_js)
// Exposes window.fsms for use in form scripts.

frappe.provide("fsms");

fsms.format_workflow_tag = function (state) {
	const map = {
		"Draft": "fsms-state-draft",
		"Đề xuất": "fsms-state-draft",
		"Pending Approval": "fsms-state-pending",
		"Chờ phê duyệt": "fsms-state-pending",
		"Phân tích": "fsms-state-pending",
		"Approved": "fsms-state-approved",
		"Đang thực hiện": "fsms-state-approved",
		"Đã đóng": "fsms-state-closed",
		"Closed": "fsms-state-closed",
		"Đóng": "fsms-state-closed",
		"Chuyển tiếp": "fsms-state-rejected",
	};
	const cls = map[state] || "fsms-state-draft";
	return `<span class="fsms-workflow-tag ${cls}">${frappe.utils.escape_html(state || "")}</span>`;
};

fsms.fetch_signature_for_employee = async function (employee_id) {
	if (!employee_id) return null;
	const r = await frappe.db.get_value("Employee", employee_id, "fsms_signature_image");
	return r && r.message ? r.message.fsms_signature_image : null;
};

fsms.confirm_workflow_action = function (action_label, on_confirm) {
	frappe.confirm(
		__('Bạn chắc chắn muốn thực hiện hành động "{0}"?', [action_label]),
		on_confirm
	);
};
