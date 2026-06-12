"""Lifecycle hooks: after_install + before_uninstall (registered in hooks.py)."""

import frappe
from frappe.permissions import add_permission, update_permission_property

# ============================================================================
# Quyền truy cập DocType core (Item, Batch, ...) cho các role FSMS.
#
# Trước đây ship qua fixtures/custom_docperm.json nhưng Custom DocPerm được
# đặt tên bằng hash — không thể khai báo `name` tĩnh trong fixture, và
# frappe/modules/import_file.py truy cập doc["name"] vô điều kiện khi import
# → KeyError: 'name' làm chết install. Ship Custom DocPerm qua fixture cũng
# là anti-pattern (hash đổi giữa các site, vỡ ở migrate sau).
#
# Tái tạo chính xác 48 rule cũ bằng API chính thức của Frappe:
#   add_permission(doctype, role, 0)        -> tạo Custom DocPerm với read=1
#   update_permission_property(...)          -> bật từng cờ bổ sung
# add_permission tự gọi setup_custom_perms() nên các DocPerm chuẩn của core
# được copy sang Custom DocPerm trước khi thêm rule mới (không mất quyền gốc).
#
# Cấu trúc: doctype -> (tuple roles, tuple ptypes bổ sung ngoài "read").
# Tất cả rule đều permlevel 0, if_owner 0 — đúng như fixture cũ.
# ============================================================================
CORE_DOCTYPE_PERMISSIONS = {
	"Item": (
		("FSMS Manager", "FSMS QC Officer", "FSMS Internal Auditor"),
		("print", "email", "report", "export"),
	),
	"Batch": (
		(
			"FSMS Manager",
			"FSMS Director",
			"FSMS Internal Auditor",
			"FSMS Production Lead",
			"FSMS Planning Lead",
			"FSMS Sales Lead",
			"FSMS Accounting Lead",
			"FSMS QC Officer",
			"FSMS Team Member",
			"FSMS Employee",
		),
		("print",),
	),
	"Customer": (
		("FSMS Manager", "FSMS Sales Lead", "FSMS QC Officer"),
		("print", "email"),
	),
	"Supplier": (
		("FSMS Manager", "FSMS Planning Lead", "FSMS QC Officer"),
		("print", "email"),
	),
	"Employee": (
		(
			"FSMS Manager",
			"Production Department Head",
			"Sales Department Head",
			"Planning Department Head",
			"Accounting Department Head",
		),
		("print",),
	),
	"Department": (
		(
			"FSMS Manager",
			"FSMS Director",
			"FSMS Internal Auditor",
			"FSMS Production Lead",
			"FSMS Planning Lead",
			"FSMS Sales Lead",
			"FSMS Accounting Lead",
			"FSMS QC Officer",
			"FSMS Team Member",
			"FSMS Employee",
		),
		(),
	),
	"Asset": (
		("FSMS Manager", "FSMS Production Lead", "FSMS QC Officer"),
		("print",),
	),
	"Work Order": (
		("FSMS Manager", "FSMS Production Lead", "FSMS QC Officer"),
		("print",),
	),
	"Purchase Receipt": (
		("FSMS Manager", "FSMS Production Lead", "FSMS Planning Lead", "FSMS QC Officer"),
		("print",),
	),
	"Delivery Note": (
		("FSMS Manager", "FSMS Sales Lead"),
		("print",),
	),
	"Stock Ledger Entry": (
		("FSMS Manager", "FSMS QC Officer"),
		(),
	),
}


def after_install():
	"""Called once after `bench install-app iso22000_fsms`.

	LƯU Ý thứ tự: trên Frappe v16 bản mới, after_install chạy TRƯỚC
	sync_fixtures (installer.py: add_module_defs → sync_for → after_install
	→ ... → sync_fixtures), nên KHÔNG được giả định role.json đã vào DB.
	_setup_core_permissions tự tạo Role còn thiếu; fixture role.json import
	sau đó sẽ ghi đè bằng thuộc tính đầy đủ (delete_old_doc dùng
	for_reload=True nên không chạy on_trash — Custom DocPerm không bị mất).
	"""
	if frappe.db.exists("DocType", "FSMS Settings") and not frappe.db.exists("FSMS Settings"):
		frappe.get_doc({"doctype": "FSMS Settings", "company_name": "(Chưa cấu hình)"}).insert(
			ignore_permissions=True
		)
	_setup_core_permissions()
	_seed_prp_templates()
	print("✓ ISO 22000 FSMS installed. Mở `Bảng điều khiển ATTP` từ menu chính.")


# 11 PRP chuẩn theo ISO/TS 22002-1 — seed làm child rows của 1 PRP Program mẫu.
# KHÔNG ship qua fixtures: FSMS PRP Item là child table (istable=1), Frappe cấm
# insert child row đứng một mình (parent/parenttype bắt buộc) → MandatoryError.
PRP_TEMPLATE_PROGRAM_VERSION = "MẪU CHUẨN — 11 PRP (ISO/TS 22002-1)"
PRP_TEMPLATE_ITEMS = [
	("PRP1-Construction", "Construction and layout of buildings", "Quan sát hạ tầng, ghi chép hiện trạng", "Năm"),
	("PRP2-Layout", "Layout of premises and workspace", "Sơ đồ + checklist", "Năm"),
	("PRP3-Utilities", "Utilities — air, water, energy", "Test mẫu nước, đo độ ẩm, áp suất", "Tuần"),
	("PRP4-Waste", "Waste disposal", "Quan sát + ghi sổ chất thải", "Ngày"),
	("PRP5-Equipment", "Equipment suitability, cleaning, maintenance", "Kiểm tra thiết bị + lịch BD", "Tuần"),
	("PRP6-Material", "Management of purchased materials", "Kiểm tra COA + nhập kho", "Mỗi đợt nhập"),
	("PRP7-Cross-contam", "Measures for prevention of cross-contamination", "Quan sát + GMP audit", "Tuần"),
	("PRP8-Cleaning", "Cleaning and sanitizing", "Sổ vệ sinh + ATP swab", "Ngày"),
	("PRP9-Pest", "Pest control", "Sổ diệt côn trùng + bẫy", "Tuần"),
	("PRP10-Personnel", "Personnel hygiene and employee facilities", "Sổ vệ sinh CN + sức khỏe", "Ngày"),
	("PRP11-Rework", "Rework", "Sổ rework + truy xuất", "Mỗi lần rework"),
]


def _seed_prp_templates():
	"""Tạo 1 FSMS PRP Program mẫu chứa 11 PRP chuẩn (thay cho fixture child-table cũ).

	Idempotent qua program_version (FSMS PRP Program đặt tên bằng hash nên không
	check theo name được). Bọc try/except: dữ liệu mẫu không tới hạn — lỗi seed
	không được phép làm chết install.
	"""
	if not frappe.db.exists("DocType", "FSMS PRP Program"):
		return
	if frappe.db.exists("FSMS PRP Program", {"program_version": PRP_TEMPLATE_PROGRAM_VERSION}):
		return
	try:
		frappe.get_doc(
			{
				"doctype": "FSMS PRP Program",
				"program_version": PRP_TEMPLATE_PROGRAM_VERSION,
				"effective_date": frappe.utils.today(),
				"prp_items": [
					{
						"prp_code": code,
						"description": desc,
						"monitoring_method": method,
						"frequency": freq,
						"is_template": 1,
					}
					for code, desc, method, freq in PRP_TEMPLATE_ITEMS
				],
			}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="iso22000_fsms: seed PRP templates failed")


def _setup_core_permissions():
	"""Cấp quyền đọc/in/email/report/export trên DocType core cho role FSMS.

	Idempotent: add_permission tự bỏ qua (msgprint, không raise) nếu rule
	(parent, role, permlevel, if_owner=0) đã tồn tại; update_permission_property
	chỉ SET giá trị cờ nên chạy lại không nhân đôi.
	"""
	for doctype, (roles, extra_ptypes) in CORE_DOCTYPE_PERMISSIONS.items():
		if not frappe.db.exists("DocType", doctype):
			# Stack thiếu app cung cấp doctype này (vd: Asset cần erpnext assets)
			print(f"⚠ iso22000_fsms: bỏ qua quyền cho DocType không tồn tại: {doctype}")
			continue
		for role in roles:
			if not frappe.db.exists("Role", role):
				# after_install chạy trước fixtures trên build mới — tạo tối thiểu,
				# role.json sẽ ghi đè bằng thuộc tính đầy đủ khi fixtures sync.
				frappe.get_doc(
					{"doctype": "Role", "role_name": role, "desk_access": 1, "is_custom": 1}
				).insert(ignore_permissions=True, ignore_if_duplicate=True)
			add_permission(doctype, role, 0)
			for ptype in extra_ptypes:
				update_permission_property(doctype, role, 0, ptype, 1)


def before_uninstall():
	"""Pre-uninstall guardrail: warn if there is real production data."""
	risky_doctypes = ["FSMS NCR", "FSMS Recall Event", "FSMS HACCP Plan", "FSMS Audit Execution"]
	for dt in risky_doctypes:
		if frappe.db.exists("DocType", dt):
			count = frappe.db.count(dt)
			if count > 0:
				frappe.msgprint(
					f"⚠️  {dt} còn {count} bản ghi. Hãy chắc chắn anh đã backup trước khi uninstall.",
					alert=True,
				)
