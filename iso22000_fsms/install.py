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

	Frappe auto-loads fixtures (fixtures/*.json) before this runs, so các Role
	FSMS đã tồn tại trong DB khi tới đây. Hook này lo các việc cần SQL thật:
	1. Ensure FSMS Settings has its sole record
	2. Cấp quyền DocType core cho role FSMS (thay cho custom_docperm.json cũ)
	3. Print a friendly banner
	"""
	if frappe.db.exists("DocType", "FSMS Settings") and not frappe.db.exists("FSMS Settings"):
		frappe.get_doc({"doctype": "FSMS Settings", "company_name": "(Chưa cấu hình)"}).insert(
			ignore_permissions=True
		)
	_setup_core_permissions()
	print("✓ ISO 22000 FSMS installed. Mở `Bảng điều khiển ATTP` từ menu chính.")


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
				print(f"⚠ iso22000_fsms: bỏ qua quyền {doctype}/{role} — Role chưa tồn tại")
				continue
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
