frappe.listview_settings["FSMS Objective"] = {
	get_indicator(doc) {
		const map = {
			"Đang theo dõi": ["Đang theo dõi", "blue"],
			"Đạt": ["Đạt", "green"],
			"Không đạt": ["Không đạt", "red"],
			"Hủy": ["Hủy", "gray"],
		};
		return map[doc.status] || null;
	},
};
