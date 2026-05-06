frappe.listview_settings["FSMS NCR"] = {
	get_indicator(doc) {
		const map = {
			"Đề xuất": ["Đề xuất", "blue"],
			"Phân tích": ["Phân tích", "orange"],
			"Chờ phê duyệt": ["Chờ phê duyệt", "yellow"],
			"Đang thực hiện": ["Đang thực hiện", "green"],
			"Đang xác minh": ["Đang xác minh", "purple"],
			"Đã đóng": ["Đã đóng", "gray"],
			"Chuyển tiếp": ["Chuyển tiếp", "red"],
		};
		return map[doc.workflow_state] || null;
	},
};
