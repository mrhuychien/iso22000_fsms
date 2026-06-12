# INVESTIGATION — Lần install-app đầu tiên thất bại (test.localhost)

Ngày: 2026-06-11 · Phạm vi: `bench --site test.localhost install-app iso22000_fsms`
Stack: frappe v16 + erpnext + hrms + erpnextvn · Branch fix: `claude/quirky-euler-ezqtns`

---

## 1. Root cause

**Bug 1 — `patches.txt`:** Frappe v16 parse patches.txt theo section; thiếu
`[pre_model_sync]` → `KeyError` chết cả install lẫn migrate.

**Bug 2 — `KeyError: 'name'` tại `custom_docperm.json`:**
`frappe/modules/import_file.py:123` đọc `doc["name"]` **vô điều kiện cho mọi
record fixture, trước mọi logic autoname**:

```python
db_modified_timestamp = frappe.db.get_value(doc["doctype"], doc["name"], "modified")
```

→ **bất kỳ** record fixture nào không có key `name` đều nổ, không riêng
Custom DocPerm. `custom_docperm.json` chỉ là file nổ **đầu tiên** vì
`import_fixtures()` (`frappe/utils/fixtures.py`) duyệt thư mục `fixtures/`
theo **thứ tự alphabet của tên file** (không theo list `fixtures` trong
hooks.py — list đó chỉ dùng cho `bench export-fixtures`). **14/21 file** dính
cùng lỗi; nếu chỉ fix custom_docperm thì lần cài sau chết ở
`custom_field.json`, rồi `dashboard_chart.json`, v.v.

`import_fixtures()` chỉ bắt `ImportError`/`DoesNotExistError` — `KeyError`
xuyên thẳng ra ngoài làm chết install.

## 2. Evidence chính (Frappe v16 source)

| Kết luận | Bằng chứng |
|---|---|
| `doc["name"]` đọc vô điều kiện | `frappe/modules/import_file.py:123` |
| Fixture import theo alphabet tên file, mọi `.json` trong `fixtures/` đều bị import | `frappe/utils/fixtures.py::import_fixtures` (`sorted(os.listdir)`) |
| `name` đặt sẵn được giữ nguyên khi import (mọi kiểu autoname, kể cả hash/child) | `frappe/model/naming.py:158` — `if ... not frappe.flags.in_import: doc.name = None`; `import_doc` bật `frappe.flags.in_import` |
| Fixtures chạy **trước** `after_install` → roles đã có khi cấp quyền | `frappe/installer.py::install_app`: `sync_for` → `sync_fixtures` → `after_install` |
| `add_permission` idempotent + copy DocPerm chuẩn sang Custom DocPerm trước (không mất quyền core) | `frappe/permissions.py::add_permission` → `setup_custom_perms` + check tồn tại `(parent, role, permlevel, if_owner)` |
| Module trong modules.txt được tạo Module Def tự động, **nhưng `sync_for` import package Python của từng module vô điều kiện** → mỗi module trong modules.txt BẮT BUỘC có thư mục package (`<scrub(module)>/__init__.py`) | `frappe/installer.py:321→723 add_module_defs`; `frappe/model/sync.py:117` (`frappe.get_module(app + "." + module)`) — vỡ thực tế ở lần cài thứ 2, đã fix bằng package `iso_22000_fsms/` |
| Luật docstatus workflow: cấm `2→*`, `1→0`, `0→2`; validate chạy **ngay lúc import fixture** (data_import=True không tắt validate) | `frappe/workflow/doctype/workflow/workflow.py::validate_docstatus`; `import_file.py::import_doc` |
| `allow_edit`/`allowed` là Link 1 role; client gộp allow_edit của **mọi row trùng state**; transition match theo từng row | `frappe/public/js/frappe/model/workflow.js::is_read_only`, `frappe/model/workflow.py::get_transitions` |
| Print Format `standard=Yes` import được trên site không developer_mode | `print_format.py::validate` miễn khi `in_install`/`in_migrate` |
| Lỗi log `Error creating icons 'list' object is not callable` **không phải do app** | v16 tạo icon từ hook `add_to_apps_screen` (app không khai báo → nhánh bị bỏ qua); `config/desktop.py` không còn được v16 dùng. Non-fatal, phát sinh từ core/app khác. |

## 3. Fix đã giao (mỗi fix một commit)

1. `fix(patches)` — thêm `[pre_model_sync]` (đồng bộ hotfix trên server vào repo).
2. `fix(install)` — bỏ fixture Custom DocPerm; `_setup_core_permissions()` trong
   `install.py` tái tạo **đúng 48 rule** (11 DocType core × role FSMS, permlevel 0,
   đã đối chiếu máy 1:1 không thêm không bớt) bằng `add_permission` +
   `update_permission_property`, idempotent; gỡ entry khỏi `hooks.py`; xóa
   `fixtures/custom_docperm.json`. Giữ nguyên seed FSMS Settings + `before_uninstall`.
3. `fix(fixtures)` — thêm `name` tường minh cho **mọi** record của 13 file còn
   lại (suy từ chính luật autoname của từng doctype → re-import mỗi migrate
   idempotent); đổi `fsms_prp_item_template.json` → `fsms_prp_item.json` khớp
   scrub(doctype); bổ sung master bị thiếu: Workflow State `Phát hành`,
   Workflow Action Master `Submit`, `Verify`.
4. `fix(modules)` — đăng ký module ô dù `ISO 22000 FSMS` (7 file fixture trỏ tới)
   + package `iso_22000_fsms/__init__.py` (sync_for import package của mọi module).
5. `fix(reports)` — 14 Script Report nằm ở `iso22000_fsms/iso22000_fsms/report/`
   (không khớp module nào → không bao giờ sync, chạy là ImportError) → chuyển về
   đúng thư mục module khai trong JSON; đổi tên report chứa ký tự unicode `×`
   (scrub không thay → lệch dotted-path); xóa `fixtures/report.json` trùng lặp
   + entry hooks (report chuẩn ship bằng module file).
6. `fix(workflow)` — tách 16 state + 17 transition có role CSV thành 1 row/role
   (OR-logic đúng cách Frappe hỗ trợ); HACCP `Reviewed` 0→1 vì cạnh
   `Under Revision(1)→Reviewed(0)` vi phạm luật docstatus **và sẽ chết ngay lúc
   import fixture**; chuẩn hóa `doc_status` thành string.

Sweep tĩnh sau fix: **0 ERROR** (đã kiểm: JSON parse, py_compile, 43 dotted
path trong hooks, 123 DocType — module/folder/controller/__init__/fieldtype/
Link-Table target/autoname, 28 workflow — docstatus/state/action/role, chart
& number card & notification field refs, patches, print format).

## 3b. Vòng 3 — lớp lỗi "JSON không khớp schema doctype đích"

Lần cài thứ 3 chết ở **sync module files** (`'str' object does not support item
assignment`, `base_document.py:448 _init_child`): `Report.columns` là **child
table** (`Report Column`) nhưng 14 report JSON scaffold ghi nó thành **chuỗi
JSON** → Frappe duyệt từng ký tự của chuỗi để tạo child row. Đây là cả một lớp
lỗi: giá trị field trong document JSON không khớp schema thật của doctype đích.

Đã xây `scripts/validate_shipped_docs.py` — tải schema thật của 27 doctype
core (frappe version-16) + schema doctype của chính app, validate **từng key
của từng record** ship trong fixtures + module files: shape Table, options
Select, field reqd (đường fixture chạy validate + mandatory đầy đủ), key không
tồn tại, guard `is_standard`. Kết quả bắt thêm 7 nhóm lỗi **chưa kịp nổ**:

| Lỗi | Hậu quả nếu không sửa | Fix |
|---|---|---|
| 14 report json: `columns` là string | TypeError chết sync (lỗi vòng 3) | `columns: []` — Script Report lấy cột từ `execute()` |
| `dashboard_chart.json`: `is_standard=1` ×6 | `DashboardChart.validate:390` throw "Cannot edit Standard charts" (không miễn trừ in_install, site không developer_mode) | `is_standard: 0` |
| `dashboard.json`: `is_standard=1` | Guard y hệt tại `dashboard.py:47` | `is_standard: 0` |
| `dashboard_chart.json`: thiếu `filters_json` (reqd, không default) | MandatoryError ở fixture import | thêm `filters_json: "[]"` |
| `workflow.json`: 27 state terminal `allow_edit` rỗng (reqd) | MandatoryError ở fixture import | `allow_edit: "System Manager"` (state đóng ≈ read-only nghiệp vụ) |
| `number_card.json`: `function='Custom'` ngoài options Select; thiếu `type` | ValidationError (`_validate_selects`); card không biết nguồn dữ liệu | bỏ `function`, set `type: Custom` (card có `method`) / `type: Document Type` |
| `notification.json`: `is_standard=1` ×12 | Runtime load message template từ **file module** (app không ship) thay vì DB | `is_standard: 0` |
| `email_template.json`: key `module` không tồn tại trong schema; `role.json`: key `description` | Bị drop im lặng khi import; nhưng hooks filter Email Template theo `module` sẽ vỡ `export-fixtures` | bỏ key; hooks filter đổi sang `name like FSMS%` |

Bài học cho scaffold offline: **mọi record ship đi phải validate chống schema
thật của Frappe đúng version**, không dựa vào trí nhớ về cấu trúc doctype.
Chạy `python3 scripts/validate_shipped_docs.py` trước mỗi lần commit fixture.

## 3c. Vòng 4 — thứ tự installer của build server + chart trỏ child table

Log vòng 4 (site sạch) chứng minh: **build Frappe trên server chạy
`after_install` TRƯỚC `sync_fixtures`** (installer.py: add_module_defs:321 →
sync_for:323 → after_install → sync_fixtures:339) — ngược với nhánh
version-16 public. Hệ quả: `_setup_core_permissions()` chạy khi role.json
chưa import → 28/48 rule bị bỏ qua ("Role chưa tồn tại"; các role thoát nạn
là nhờ `make_module_and_roles` tự tạo từ DocType permissions lúc sync).

Fix: `_setup_core_permissions` tự tạo Role còn thiếu (desk_access=1,
is_custom=1); role.json import sau ghi đè bằng thuộc tính đầy đủ. An toàn vì
`delete_old_doc` của fixture dùng `delete_doc(for_reload=True)` — **bỏ qua
on_trash** (delete_doc.py docstring 50–52) nên Custom DocPerm vừa cấp không
bị cascade xóa khi Role bị delete+reinsert.

Crash thật vòng 4: chart "FSMS Audit Findings by Department" có
`document_type = FSMS Audit Finding` — **child table** →
`DashboardChart.check_required_field` (dashboard_chart.py:404) đòi
`parent_document_type`. Fix: `parent_document_type = FSMS Audit Execution`
(bảng cha chứa field `findings`). Card cùng doctype thoát check vì
`type=Custom`. Validator đã thêm rule này (`check_controller_rules`).

Noise vô hại của build mới trong log: "Creating Sidebar Items for Nga"
(workspace app khác) và "Error creating icons 'list' object is not callable"
(core tự catch, install chạy tiếp — không phải code app).

## 3d. Vòng 5 — 3 fixture còn nổ ở runtime validate (cùng loại schema-mismatch)

Vòng 5 (đã chạy đúng code mới): after_install + 4 fixture đầu qua sạch, chết ở
`fsms_prp_item.json`. Soi sâu các controller-validate còn lại, gỡ luôn 3 quả:

| Fixture | Validate ném ở đâu | Fix |
|---|---|---|
| `fsms_prp_item.json` | `FSMS PRP Item` là **child table** (istable=1); insert standalone → `_validate_mandatory` đòi parent/parenttype | Bỏ fixture; seed 11 PRP chuẩn thành child rows của 1 `FSMS PRP Program` mẫu trong `after_install` (`_seed_prp_templates`, bọc try/except, idempotent theo program_version) |
| `workspace.json` | `content=""` → `json.loads("")` lỗi → `Workspace.validate` throw "Content data shoud be a list" | Dựng `content` là JSON list hợp lệ (header + 2 shortcut + 1 card) + thêm 1 row "Card Break" gom 12 link |
| `notification.json` | 3 record `event="Days Before"` thiếu `date_changed` → `Notification.validate` throw "Please specify which date field" | Điền `date_changed` = field ngày thật (next_review_date / kickoff_meeting_date) + `days_in_advance` |

Validator thêm 3 rule: child-table-as-fixture, Workspace.content-phải-list,
Notification.event-cần-field-đồng-hành. Đã kiểm Jinja syntax mọi subject/
message (hợp lệ). Còn lại: 3 notification `event=Method` thiếu `method` —
KHÔNG chặn install (validate không bắt), chức năng đã do scheduler task trong
`tasks.py` lo; để nguyên.

## 3e. Vòng 6 — workflow gắn lên Single doctype + thiếu is_submittable

Vòng 6 qua sạch tới `workflow.json` (file 15/18), chết với
`(1146, "Table 'tab FSMS Manual' doesn't exist")` tại
`Workflow.on_update → update_default_workflow_status` — hàm này chạy
`UPDATE tab{document_type} SET workflow_state=default ...` **vô điều kiện**.

Hai bug class:

| Lỗi | Doctype | Fix |
|---|---|---|
| Workflow gắn lên **Single doctype** (issingle=1 → không có bảng `tab` → UPDATE vỡ; Single cũng không submit được) | `FSMS Manual`, `FSMS Policy` (đúng là Single — `api.py`/test dùng `get_single`) | Bỏ 2 workflow `FSMS Manual Workflow`, `FSMS Policy Workflow`. Manual/Policy quản lý phê duyệt bằng các field chữ ký prepared/reviewed/approved, không qua Frappe Workflow |
| Workflow có state `doc_status>=1` nhưng doctype **không is_submittable** (apply_workflow vỡ runtime khi submit) | `FSMS Audit Program`, `FSMS Audit Plan`, `FSMS Training Plan` (workflow Draft→Approved(1)→…→Closed(1), không có on_submit code) | Bật `is_submittable=1` trên 3 doctype — đúng ý đồ lifecycle "khoá sau phê duyệt" |

Validator thêm `check_workflow_targets`: workflow trên Single → ERROR; workflow
có doc_status>=1 mà doctype không is_submittable → ERROR. Đã quét: dashboard
chart/number card không trỏ Single (đã import qua ở vòng 6), notification không
Single → hết bug class này.

## 4. Lưu ý còn mở (không chặn install — theo dõi ở vòng test)

- **FSMS PRP Item** là child table được seed 11 row template mồ côi
  (parent NULL) + `FSMS Verification Test.object` Link tới child table —
  chạy được, nhưng là design smell; cân nhắc chuyển template thành DocType
  thường ở bản sau.
- **HACCP `Reviewed` giờ là docstatus 1** — muốn sửa nội dung ở state
  `Under Revision` thì các field cần sửa phải bật `allow_on_submit`.
- **Workspace chỉ có 1** (`FSMS` — Bảng điều khiển ATTP). Không có workspace
  per-module trong codebase → nghiệm thu đếm **1 workspace**, không phải 18
  (18 là số module, không phải số workspace).
- `Error creating icons ...` trong log cũ: noise vô hại từ core, bỏ qua.

## 5. Nghiệm thu Vòng 1 (đã hiệu chỉnh theo thực tế codebase)

```bash
bench --site test.localhost console
>>> frappe.db.count("Workflow")                                            # 28
>>> frappe.db.count("Print Format", {"module": ["like", "%FSMS%"]})        # 38
>>> frappe.db.count("Report", {"module": ["like", "FSMS%"]})               # 14
>>> frappe.db.count("Role", {"name": ["like", "FSMS%"]})                   # 10 (+4 Department Head = 14 role mới)
>>> frappe.db.count("Custom DocPerm", {"role": ["like", "FSMS%"]})         # 44 (+4 rule Department Head trên Employee = 48)
>>> frappe.db.count("Workflow State")                                      # >= 34
>>> frappe.db.exists("Workspace", "FSMS")                                  # 'FSMS'
>>> frappe.db.count("FSMS PRP Item", {"is_template": 1})                   # 11
>>> frappe.db.count("FSMS Risk Score Reference")                           # 16
```

Cộng: mở list view + form New các DocType chính, `bench --site test.localhost doctor` sạch.

## 6. Quy trình test (giữ kỷ luật — KHÔNG đụng production `site1.local`)

```bash
cd apps/iso22000_fsms && git pull
bench drop-site test.localhost --force --db-root-password huychien123
bench new-site test.localhost --admin-password admin --db-root-password huychien123
bench --site test.localhost install-app erpnext
bench --site test.localhost install-app hrms
bench --site test.localhost install-app erpnextvn
bench --site test.localhost install-app iso22000_fsms
```

Sau khi Vòng 1 sạch mới tính tới production: backup + snapshot GCP →
`uninstall-app iso22000_fsms` → cài lại. Văng Duplicate/Workflow/Role trên
production thì **dừng, hỏi lại**.
