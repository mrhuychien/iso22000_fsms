#!/usr/bin/env python3
"""Validate mọi document JSON app ship (fixtures + report module files) chống schema THẬT của Frappe v16.

Bắt lớp lỗi đã làm chết install vòng 3:
- Table field (vd Report.columns) nhận string thay vì list-of-dict -> TypeError lúc sync
- Select value ngoài options (vd Number Card function='Custom') -> ValidationError lúc import fixture
- Thiếu field reqd không có default (vd Dashboard Chart.filters_json, Workflow Document State.allow_edit)
  -> MandatoryError (đường fixture chạy validate + mandatory đầy đủ)
- is_standard=1 trên Dashboard/Dashboard Chart -> "Cannot edit Standard ..." khi site không bật developer_mode
- Key không tồn tại trong schema (bị drop im lặng khi import, nhưng vỡ export-fixtures nếu hooks filter theo key đó)

Chạy từ repo root:  python3 scripts/validate_shipped_docs.py
Schema core được tải 1 lần từ GitHub (frappe version-16) và cache ở /tmp/frappe_schemas.
"""
import glob
import json
import os
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(REPO, "iso22000_fsms")
CACHE = "/tmp/frappe_schemas"
BASE = "https://raw.githubusercontent.com/frappe/frappe/version-16/frappe"

CORE_SCHEMAS = {
	"report": "core/doctype/report/report.json",
	"report_column": "core/doctype/report_column/report_column.json",
	"report_filter": "core/doctype/report_filter/report_filter.json",
	"has_role": "core/doctype/has_role/has_role.json",
	"role": "core/doctype/role/role.json",
	"custom_field": "custom/doctype/custom_field/custom_field.json",
	"property_setter": "custom/doctype/property_setter/property_setter.json",
	"workflow": "workflow/doctype/workflow/workflow.json",
	"workflow_document_state": "workflow/doctype/workflow_document_state/workflow_document_state.json",
	"workflow_transition": "workflow/doctype/workflow_transition/workflow_transition.json",
	"workflow_state": "workflow/doctype/workflow_state/workflow_state.json",
	"workflow_action_master": "workflow/doctype/workflow_action_master/workflow_action_master.json",
	"notification": "email/doctype/notification/notification.json",
	"notification_recipient": "email/doctype/notification_recipient/notification_recipient.json",
	"email_template": "email/doctype/email_template/email_template.json",
	"print_format": "printing/doctype/print_format/print_format.json",
	"dashboard": "desk/doctype/dashboard/dashboard.json",
	"dashboard_chart_link": "desk/doctype/dashboard_chart_link/dashboard_chart_link.json",
	"number_card_link": "desk/doctype/number_card_link/number_card_link.json",
	"dashboard_chart": "desk/doctype/dashboard_chart/dashboard_chart.json",
	"number_card": "desk/doctype/number_card/number_card.json",
	"workspace": "desk/doctype/workspace/workspace.json",
	"workspace_link": "desk/doctype/workspace_link/workspace_link.json",
	"workspace_shortcut": "desk/doctype/workspace_shortcut/workspace_shortcut.json",
	"workspace_chart": "desk/doctype/workspace_chart/workspace_chart.json",
	"workspace_number_card": "desk/doctype/workspace_number_card/workspace_number_card.json",
	"workspace_quick_list": "desk/doctype/workspace_quick_list/workspace_quick_list.json",
}

META_KEYS = {
	"doctype", "name", "owner", "creation", "modified", "modified_by", "docstatus", "idx",
	"parent", "parentfield", "parenttype", "__islocal", "_user_tags", "_comments", "_assign", "_liked_by",
}
TABLE_FT = ("Table", "Table MultiSelect")
LAYOUT_FT = ("Section Break", "Column Break", "Tab Break", "HTML", "Heading", "Button", "Fold")
# doctype có guard "Cannot edit Standard ..." không miễn trừ lúc install
STANDARD_GUARDED = {"Dashboard", "Dashboard Chart"}

E, W = [], []


def fetch_schemas():
	os.makedirs(CACHE, exist_ok=True)
	for key, path in CORE_SCHEMAS.items():
		target = os.path.join(CACHE, key + ".json")
		if os.path.exists(target):
			continue
		urllib.request.urlretrieve(f"{BASE}/{path}", target)


def load_schemas():
	schemas = {}
	for f in glob.glob(f"{CACHE}/*.json"):
		d = json.load(open(f))
		schemas[d["name"]] = d
	for f in glob.glob(f"{APP}/*/doctype/*/*.json"):
		try:
			d = json.load(open(f))
		except Exception:
			continue
		if isinstance(d, dict) and d.get("doctype") == "DocType":
			schemas[d["name"]] = d
	return schemas


def check_record(schemas, rec, dt, ctx, mandatory_enforced):
	s = schemas.get(dt)
	if not s:
		W.append(f"{ctx}: không có schema cho '{dt}'")
		return
	fm = {f["fieldname"]: f for f in s.get("fields", []) if f.get("fieldname")}
	if dt in STANDARD_GUARDED and rec.get("is_standard"):
		E.append(f"{ctx}: is_standard=1 trên {dt} -> throw 'Cannot edit Standard' khi site không bật developer_mode")
	for k, v in rec.items():
		if k in META_KEYS:
			continue
		f = fm.get(k)
		if not f:
			E.append(f"{ctx}: key '{k}' KHÔNG tồn tại trong schema {dt}")
			continue
		ft = f.get("fieldtype")
		if ft in TABLE_FT:
			if not isinstance(v, list):
				E.append(f"{ctx}: '{k}' là {ft}->{f.get('options')} nhưng giá trị {type(v).__name__} (phải list-of-dict)")
				continue
			for i, row in enumerate(v):
				if not isinstance(row, dict):
					E.append(f"{ctx}: '{k}[{i}]' không phải dict")
					continue
				check_record(schemas, row, f.get("options"), f"{ctx}.{k}[{i}]", mandatory_enforced)
		else:
			if isinstance(v, (list, dict)):
				E.append(f"{ctx}: '{k}' ({ft}) nhận {type(v).__name__} — phải là scalar")
				continue
			if ft == "Select" and v not in (None, "") and f.get("options"):
				opts = [o.strip() for o in str(f["options"]).split("\n")]
				if str(v) not in opts:
					E.append(f"{ctx}: '{k}'='{v}' ngoài options Select {opts} của {dt}")
	if mandatory_enforced:
		for fn, f in fm.items():
			if f.get("reqd") and f.get("fieldtype") not in LAYOUT_FT:
				if rec.get(fn, f.get("default")) in (None, ""):
					E.append(f"{ctx}: thiếu field bắt buộc '{fn}' ({dt}, không có default) — MandatoryError ở fixture import")


def check_controller_rules(schemas, rec, ctx):
	"""Luật validate đặc thù của controller core (chạy đầy đủ ở đường fixture)."""
	dt = rec.get("doctype")
	target = rec.get("document_type")
	target_istable = bool(schemas.get(target, {}).get("istable")) if target else False
	# DashboardChart.check_required_field / NumberCard.validate:
	# document_type là child table -> bắt buộc parent_document_type
	if dt == "Dashboard Chart" and rec.get("chart_type") not in ("Custom", "Report"):
		if target_istable and not rec.get("parent_document_type"):
			E.append(f"{ctx}: document_type '{target}' là child table — thiếu parent_document_type (DashboardChart.check_required_field throw)")
	if dt == "Number Card" and rec.get("type") == "Document Type":
		if target_istable and not rec.get("parent_document_type"):
			E.append(f"{ctx}: document_type '{target}' là child table — thiếu parent_document_type (NumberCard.validate throw)")


def main():
	fetch_schemas()
	schemas = load_schemas()
	# fixtures: data_import=True -> validate + mandatory BẬT
	for f in sorted(glob.glob(f"{APP}/fixtures/*.json")):
		for i, rec in enumerate(json.load(open(f))):
			ctx = f"{os.path.basename(f)}[{i} {rec.get('name', '?')}]"
			check_record(schemas, rec, rec.get("doctype"), ctx, True)
			check_controller_rules(schemas, rec, ctx)
	# module-file sync (report, ...): validate/mandatory TẮT -> chỉ cần shape
	for f in sorted(glob.glob(f"{APP}/*/report/*/*.json")):
		check_record(schemas, json.load(open(f)), "Report", os.path.relpath(f, APP), False)
	# DocType json: các key child phải là list
	for f in sorted(glob.glob(f"{APP}/*/doctype/*/*.json")):
		d = json.load(open(f))
		if not isinstance(d, dict) or d.get("doctype") != "DocType":
			continue
		for k in ("fields", "permissions", "actions", "links", "states", "indexes"):
			if k in d and not isinstance(d[k], list):
				E.append(f"{os.path.relpath(f, APP)}: DocType key '{k}' không phải list")

	print(f"========== VALIDATE SHIPPED DOCS: {len(E)} ERROR / {len(W)} WARN ==========")
	for x in E:
		print("ERROR:", x)
	for x in W:
		print("WARN :", x)
	return 1 if E else 0


if __name__ == "__main__":
	sys.exit(main())
