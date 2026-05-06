# 06 — Fixtures Plan

> **App**: `iso22000_fsms` · Frappe v16 · ERPNext v16 (đã chạy)
> **Trạng thái**: Draft v0.1 — file cuối series. Sau khi approve → handoff `nextcode-build`.
> **Phụ thuộc**: 01–05 đã được duyệt

---

## 0. Mục tiêu file này

Quy định **TẤT CẢ** fixtures (data ship cùng app, load vào DB khi `bench install-app iso22000_fsms`). Đây là cốt lõi của "boot configuration" — app cài xong là dùng được ngay, không cần admin cấu hình thủ công 10 ngày trời.

Frappe fixtures cơ chế:
- `hooks.py` declares `fixtures = [...]`
- Khi install: `bench export-fixtures` (dev side) ↔ `bench install-app` (prod side) auto-load JSON files trong `iso22000_fsms/fixtures/`
- Idempotent: re-install không nhân đôi data

---

## 1. Fixtures inventory tổng quan

| # | File | Số records | Mô tả |
|---|------|-----------|-------|
| 1 | `role.json` | 14 | 10 FSMS roles + 4 Department Head roles |
| 2 | `custom_field.json` | 6 | Custom Fields trên ERPNext core |
| 3 | `custom_docperm.json` | ~30 | Custom Permission trên ERPNext core (read-only access) |
| 4 | `workflow_state.json` | ~25 | Shared workflow states |
| 5 | `workflow.json` | 28 | Workflows per DocType |
| 6 | `workflow_action_master.json` | ~40 | Action labels (button text) |
| 7 | `notification.json` | 12 | Email + in-app notifications |
| 8 | `email_template.json` | 12 | Jinja templates |
| 9 | `print_format.json` | 21+ | Per-BM Print Formats (giống Word) |
| 10 | `fsms_document_category.json` | 6 | QT, BM, HD, PL, QĐ, KH |
| 11 | `fsms_ncr_source.json` | 7 | Audit, CCP Fail, Customer Complaint, ... |
| 12 | `fsms_risk_score_reference.json` | 16 | A/B/C/D × 1–4 = 16 entries |
| 13 | `fsms_supplier_category.json` | 2 | Loại 1 / Loại 2 |
| 14 | `fsms_emergency_scenario.json` | 5 | PL.03.01 → PL.03.05 |
| 15 | `fsms_prp_item_template.json` | 11 | PRP1 → PRP11 (ISO/TS 22002-1) |
| 16 | `dashboard_chart.json` | 6 | Charts cho GD Dashboard |
| 17 | `number_card.json` | 4 | KPI cards cho GD Dashboard |
| 18 | `workspace.json` | 1 | "Bảng điều khiển ATTP" workspace |
| 19 | `report.json` | 14 | Custom Reports |
| 20 | `dashboard.json` | 1 | "FSMS Director Dashboard" |

→ **Tổng ~205 records ship cùng app**.

---

## 2. Roles (`fixtures/role.json`)

```json
[
  {
    "doctype": "Role",
    "role_name": "FSMS Director",
    "desk_access": 1,
    "two_factor_auth": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Manager",
    "desk_access": 1,
    "two_factor_auth": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Team Member",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Planning Lead",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Production Lead",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Accounting Lead",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Sales Lead",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Internal Auditor",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS QC Officer",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "FSMS Employee",
    "desk_access": 1,
    "is_custom": 1
  },
  {
    "doctype": "Role",
    "role_name": "Production Department Head",
    "desk_access": 1,
    "is_custom": 1,
    "description": "OR-logic approval cho NCR — gán cho TBP_SX"
  },
  {
    "doctype": "Role",
    "role_name": "Sales Department Head",
    "desk_access": 1,
    "is_custom": 1,
    "description": "OR-logic approval cho NCR — gán cho TBP_KD"
  },
  {
    "doctype": "Role",
    "role_name": "Planning Department Head",
    "desk_access": 1,
    "is_custom": 1,
    "description": "OR-logic approval cho NCR — gán cho TBP_KH"
  },
  {
    "doctype": "Role",
    "role_name": "Accounting Department Head",
    "desk_access": 1,
    "is_custom": 1,
    "description": "OR-logic approval cho NCR — gán cho TBP_KT"
  }
]
```

---

## 3. Custom Fields (`fixtures/custom_field.json`)

6 fields đã spec đầy đủ ở `05_integration_plan.md` §1.2 — em không lặp lại JSON. `nextcode-build` đọc thẳng từ đó.

---

## 4. Custom Permissions (`fixtures/custom_docperm.json`)

Bổ sung quyền `read` cho FSMS roles trên ERPNext core DocTypes (đã spec ở `03_permission_matrix.md` §4):

| Parent DocType | Role added | Permissions |
|----------------|------------|-------------|
| `Item` | FSMS Manager, FSMS QC Officer, FSMS Internal Auditor | read, print, email, report, export |
| `Batch` | All FSMS roles | read, print |
| `Customer` | FSMS Manager, FSMS Sales Lead, FSMS QC Officer | read, print, email |
| `Supplier` | FSMS Manager, FSMS Planning Lead, FSMS QC Officer | read, print, email |
| `Employee` | FSMS Manager, all 4 TBP roles | read, print |
| `Department` | All FSMS roles | read |
| `Asset` | FSMS Manager, FSMS Production Lead, FSMS QC Officer | read, print |
| `Work Order` | FSMS Manager, FSMS Production Lead, FSMS QC Officer | read, print |
| `Purchase Receipt` | FSMS Manager, FSMS Production Lead, FSMS Planning Lead, FSMS QC Officer | read, print |
| `Delivery Note` | FSMS Manager, FSMS Sales Lead | read, print |
| `Stock Ledger Entry` | FSMS Manager, FSMS QC Officer | read |

→ ~30 Custom Permission entries.

---

## 5. Workflow States (`fixtures/workflow_state.json`)

Shared states — dùng đi dùng lại giữa nhiều workflows. Style guide:
- `style = "Primary"` cho terminal/closed states
- `style = "Warning"` cho pending states
- `style = "Success"` cho approved/closed-positive
- `style = "Danger"` cho rejected/failed

| State name (workflow_state_name) | Style | Reused by |
|----------------------------------|-------|-----------|
| `Draft` | Primary | Manual, Policy, HACCP Plan, Audit Program/Plan, Verification Plan, Calibration Plan, Training Plan, Supplier Evaluation, Sanitation Report, Material Inspection Log, Risk Register, Objective |
| `Reviewed` | Warning | Manual, Policy, HACCP Plan, Sanitation Report, Supplier Evaluation, Verification Report |
| `Pending Approval` | Warning | Manual, Policy, HACCP Plan, Audit Program, Recall Plan, Recall Report |
| `Approved` | Success | Manual, Policy, HACCP Plan, Audit Program, Recall Plan, Verification Plan, Calibration Plan, Risk Register, Supplier Evaluation, Training Plan, Verification Report, Sanitation Report |
| `Published` | Success | Manual, Policy, HACCP Plan |
| `Under Revision` | Warning | HACCP Plan |
| `Obsolete` | Primary | Manual, Policy, HACCP Plan |
| `Closed` (English) | Primary | Audit Program, Verification Plan, Calibration Plan, Verification Report |
| `Đóng` (Vietnamese) | Primary | Recall Event, Customer Complaint, Emergency Event, Management Review, Document Change Request, Traceability Drill, Traceability Trace |
| `Đề xuất` | Primary | NCR, Document Change Request |
| `Phân tích` | Warning | NCR |
| `Chờ phê duyệt` | Warning | NCR, Document Change Request |
| `Đang thực hiện` | Success | NCR |
| `Đang xác minh` | Warning | NCR |
| `Đã đóng` | Success | NCR |
| `Chuyển tiếp` | Danger | NCR |
| `Phát sinh` | Primary | Recall Event |
| `Lập kế hoạch` | Warning | Recall Event |
| `Đang thu hồi` | Danger | Recall Event |
| `Bảo quản` | Warning | Recall Event |
| `Báo cáo` | Warning | Recall Event |
| `Notified` | Warning | Audit Plan |
| `Executing` | Success | Audit Plan, Recall Plan, Audit Program, Verification Plan, Calibration Plan, Training Plan |
| `Reported` | Warning | Audit Plan |
| `Submitted` | Warning | Audit Execution, Calibration Record, Material Inspection Log |
| `Verified` | Success | Calibration Record, Material Inspection Log |
| `Hoàn thành` | Success | Audit Execution |

→ ~27 unique states, share rộng giữa 28 workflows.

---

## 6. Workflows (`fixtures/workflow.json`)

28 workflows — em không lặp đầy đủ JSON, blueprint ở `04_workflow_blueprint.md` đã chi tiết. `nextcode-build` đọc transitions table và chuyển thẳng sang JSON.

Format chuẩn (ví dụ workflow NCR):

```json
{
  "doctype": "Workflow",
  "name": "FSMS NCR Workflow",
  "document_type": "FSMS NCR",
  "is_active": 1,
  "send_email_alert": 1,
  "workflow_state_field": "workflow_state",
  "states": [
    {"state": "Đề xuất", "doc_status": "0", "allow_edit": "FSMS Manager,FSMS Team Member,FSMS Employee"},
    {"state": "Phân tích", "doc_status": "0", "allow_edit": "FSMS Manager,FSMS Team Member"},
    {"state": "Chờ phê duyệt", "doc_status": "0", "allow_edit": "FSMS Manager,FSMS Director,Production Department Head,Sales Department Head,Planning Department Head,Accounting Department Head"},
    {"state": "Đang thực hiện", "doc_status": "1", "allow_edit": "FSMS Manager,FSMS Team Member,FSMS Employee"},
    {"state": "Đang xác minh", "doc_status": "1", "allow_edit": "FSMS Manager,FSMS Internal Auditor"},
    {"state": "Đã đóng", "doc_status": "1", "allow_edit": "FSMS Manager,FSMS Internal Auditor"},
    {"state": "Chuyển tiếp", "doc_status": "1", "allow_edit": ""}
  ],
  "transitions": [
    {"state": "Đề xuất", "action": "Gửi phân tích", "next_state": "Phân tích",
     "allowed": "FSMS Manager,FSMS Team Member,FSMS Employee",
     "condition": "doc.nonconformity_description"},
    {"state": "Phân tích", "action": "Gửi phê duyệt", "next_state": "Chờ phê duyệt",
     "allowed": "FSMS Manager,FSMS Team Member",
     "condition": "doc.root_cause_analysis and doc.proposed_action and doc.assigned_to and doc.proposed_completion_date"},
    {"state": "Chờ phê duyệt", "action": "Phê duyệt", "next_state": "Đang thực hiện",
     "allowed": "FSMS Manager,FSMS Director,Production Department Head,Sales Department Head,Planning Department Head,Accounting Department Head"},
    {"state": "Chờ phê duyệt", "action": "Yêu cầu sửa", "next_state": "Phân tích",
     "allowed": "FSMS Manager,Production Department Head,Sales Department Head,Planning Department Head,Accounting Department Head",
     "condition": "doc.approver_remarks"},
    {"state": "Đang thực hiện", "action": "Hoàn thành thực hiện", "next_state": "Đang xác minh",
     "allowed": "FSMS Manager,FSMS Team Member,FSMS Employee",
     "condition": "doc.actual_completion_date"},
    {"state": "Đang xác minh", "action": "Đạt - đóng phiếu", "next_state": "Đã đóng",
     "allowed": "FSMS Manager,FSMS Internal Auditor",
     "condition": "doc.verification_outcome == 'Đạt yêu cầu'"},
    {"state": "Đang xác minh", "action": "Không đạt - chuyển tiếp", "next_state": "Chuyển tiếp",
     "allowed": "FSMS Manager,FSMS Internal Auditor",
     "condition": "doc.verification_outcome == 'Không đạt'"}
  ]
}
```

→ Apply pattern này cho 28 workflows.

---

## 7. Workflow Action Master (`fixtures/workflow_action_master.json`)

~40 unique action labels. Highlight reusable ones:

| Action label (workflow_action_name) | Used by |
|---|---|
| `Gửi phân tích` | NCR |
| `Gửi phê duyệt` | NCR |
| `Phê duyệt` | NCR, DCR, Recall Plan, Manual, ... |
| `Yêu cầu sửa` | NCR, DCR, ... |
| `Approve` (English) | Manual, Policy, HACCP Plan, Audit Program, Recall Plan |
| `Reject` | Manual, Policy, ... |
| `Hoàn thành thực hiện` | NCR |
| `Đạt - đóng phiếu` | NCR |
| `Không đạt - chuyển tiếp` | NCR |
| `Submit for Review` | Manual, Policy, ... |
| `Publish` | Manual, Policy, HACCP Plan |
| `Mark Obsolete` | Manual, Policy, HACCP Plan |
| `Initiate Revision` | HACCP Plan |
| `GD phê duyệt thu hồi` | Recall Event |
| `Đã thu hồi vật lý` | Recall Event |
| `Bắt đầu báo cáo` | Recall Event |
| `GD ký duyệt báo cáo` | Recall Event |
| ... (~25 more) | |

---

## 8. Notifications (`fixtures/notification.json`)

12 notifications đã spec ở `05_integration_plan.md` §8. Format:

```json
{
  "doctype": "Notification",
  "name": "FSMS NCR Pending Approval",
  "subject": "[FSMS] NCR {{ doc.name }} chờ phê duyệt — {{ doc.severity }}",
  "document_type": "FSMS NCR",
  "event": "Value Change",
  "value_changed": "workflow_state",
  "condition": "doc.workflow_state == 'Chờ phê duyệt'",
  "channel": "Email",
  "send_to_all_assignees": 0,
  "recipients": [
    {"receiver_by_role": "FSMS Manager"},
    {"receiver_by_document_field": "affected_department"}
  ],
  "message": "{% include 'iso22000_fsms/templates/notifications/ncr_pending_approval.html' %}"
}
```

---

## 9. Email Templates (`fixtures/email_template.json`)

12 templates với Jinja. Stored as separate files trong `iso22000_fsms/templates/notifications/*.html` rồi reference từ Notification fixture.

Sample structure (`ncr_pending_approval.html`):
```html
<p>Kính gửi {{ doc.affected_department }},</p>
<p>Phiếu yêu cầu hành động khắc phục số <b>{{ doc.name }}</b> đang chờ phê duyệt phương án.</p>
<table>
  <tr><td><b>Mức độ:</b></td><td>{{ doc.severity }}</td></tr>
  <tr><td><b>Nguồn:</b></td><td>{{ doc.ncr_source }}</td></tr>
  <tr><td><b>Mô tả:</b></td><td>{{ doc.nonconformity_description }}</td></tr>
  <tr><td><b>Người đề xuất:</b></td><td>{{ doc.requestor }}</td></tr>
  <tr><td><b>Ngày đề xuất:</b></td><td>{{ frappe.utils.formatdate(doc.requestor_date) }}</td></tr>
</table>
<p><a href="{{ frappe.utils.get_url() }}/app/fsms-ncr/{{ doc.name }}">Mở phiếu →</a></p>
```

---

## 10. Print Formats (`fixtures/print_format.json` + asset files)

Theo decision Q7 của anh: Print Format **giống Word hiện tại**.

| Print Format name | DocType | Source Word file (RVHG) | Format type |
|---|---|---|---|
| `BM.01.01 - Phieu yeu cau sua doi tai lieu` | FSMS Document Change Request | BM.01.01.doc | Custom HTML |
| `BM.01.02 - Danh muc tai lieu noi bo` | FSMS Document Register Internal | BM.01.02.doc | Custom HTML |
| `BM.01.03 - Danh muc tai lieu ben ngoai` | FSMS Document Register External | BM.01.03.doc | Custom HTML |
| `BM.01.04 - Danh muc ho so` | FSMS Records Register | BM.01.04.doc | Custom HTML |
| `BM.01.05 - Chuong trinh va ke hoach danh gia` | FSMS Audit Plan | BM.01.05.doc | Custom HTML |
| `BM.01.06 - Check list danh gia` | FSMS Audit Execution | BM.01.06.doc | Custom HTML |
| `BM.01.07 - Phieu yeu cau hanh dong khac phuc` | FSMS NCR | BM.01.07.doc | Custom HTML |
| `BM.01.08 - Diem luu y` | FSMS Audit Observation | BM.01.08.doc | Custom HTML |
| `BM.01.09 - Bang tong hop ket qua danh gia` | FSMS Audit Summary | BM.01.09.doc | Custom HTML |
| `BM.02.01 - Ke hoach thu hoi san pham` | FSMS Recall Plan | BM.02.01.doc | Custom HTML |
| `BM.02.02 - Bao cao thu hoi san pham` | FSMS Recall Report | BM.02.02.doc | Custom HTML |
| `BM.03.01 - So theo doi thiet bi PCCC` | FSMS Fire Equipment Log | BM.03.01.doc | Custom HTML |
| `BM.03.02 - So theo doi tinh trang dich benh` | FSMS Disease Event Log | BM.03.02.doc | Custom HTML |
| `BM.03.03 - So theo doi kiem dinh thiet bi an toan` | FSMS Safety Equipment Inspection | BM.03.03.doc | Custom HTML |
| `BM.04.01 - Ke hoach tham tra` | FSMS Verification Plan | BM.04.01.doc | Custom HTML |
| `BM.04.02 - Bao cao tham tra` | FSMS Verification Report | BM.04.02.doc | Custom HTML |
| `BM.05.01 - Bang xac dinh ben quan tam` | FSMS Interested Party | BM.05.01.doc | Custom HTML |
| `BM.05.02 - Bang xac dinh rui ro` | FSMS Risk Register | BM.05.02.doc | Custom HTML |
| `BM.07.01 - Phieu danh gia nha cung ung` | FSMS Supplier Evaluation | BM.07.01.doc | Custom HTML |
| `BM.07.02 - Danh sach nha cung ung` | FSMS Approved Supplier List | BM.07.02.doc | Custom HTML |
| `BM.07.03 - So kiem tra chat luong vat tu` | FSMS Material Inspection Log | BM.07.03.doc | Custom HTML |
| `BM.06.01 - Ke hoach bao duong thiet bi SX` (mới) | FSMS Equipment Maintenance Plan | (em soạn theo blueprint) | Custom HTML |
| `BM.06.02 - So bao duong sua chua thiet bi` (mới) | FSMS Equipment Maintenance Log | (em soạn theo blueprint) | Custom HTML |
| `BM.06.03 - Ho so thiet bi do` (mới) | FSMS Measurement Equipment | (em soạn theo blueprint) | Custom HTML |
| `BM.06.04 - Ke hoach hieu chuan` (mới) | FSMS Calibration Plan | (em soạn theo blueprint) | Custom HTML |
| `BM.06.05 - Phieu ket qua hieu chuan` (mới) | FSMS Calibration Record | (em soạn theo blueprint) | Custom HTML |
| `BM.08.01 - Lenh san xuat` (mới) | FSMS Production Order | (em soạn theo blueprint) | Custom HTML |
| `BM.08.02 - So giam sat qua trinh SX` (mới) | FSMS Production Process Monitoring | (em soạn theo blueprint) | Custom HTML |
| `BM.08.03 - So theo doi kiem tra thanh pham` | FSMS Finished Product Inspection | SỔ THEO DÕI KIỂM TRA THÀNH PHẨM.doc | Custom HTML |
| `BM.08.04 - Phieu khong phu hop SX` (mới) | FSMS Production Nonconformity | (em soạn theo blueprint) | Custom HTML |
| `BM.09.01 - Phieu ket qua truy xuat nguon goc` (mới) | FSMS Traceability Trace | (em soạn theo QT 09) | Custom HTML |
| `BM.09.02 - Bao cao dien tap truy xuat` (mới) | FSMS Traceability Drill | (em soạn theo QT 09) | Custom HTML |
| `Sổ kiểm tra vệ sinh CN` | FSMS Worker Hygiene Daily | So kiem tra ve sinh Cong nhan hang ngay.doc | Custom HTML |
| `Sổ lưu mẫu` | FSMS Sample Retention Log | Sổ lưu mẫu.doc | Custom HTML |
| `Báo cáo tình hình vệ sinh` | FSMS Sanitation Report | Bao cao tinh hinh ve sinh của Cong ty.doc | Custom HTML |
| `Sổ tay An toàn thực phẩm` | FSMS Manual | So tay an toan thuc pham.doc | Custom HTML |
| `Chính sách ATTP` | FSMS Policy | Chính sách ATTP.doc | Custom HTML |
| `Mục tiêu ATTP` | FSMS Objective | Mục tiêu ATTP.doc | Custom HTML |

→ **38 Print Formats**. Mỗi cái cần cấu trúc:
1. Header table 3 cột (logo + tên BM + số/lần/ngày — clone từ Word gốc)
2. Body — render từ DocType data
3. Footer chữ ký 3 cột (soạn / soát / duyệt) với signature image
4. CSS class prefix `fsms-` (theo guideline ERPNext anh đã có)

→ Mỗi Print Format khoảng 200–400 dòng HTML/Jinja. `nextcode-build` sẽ generate dựa trên Word file gốc + DocType field map.

---

## 11. Property Setters

Override behavior của ERPNext core DocTypes mà không sửa source. Em xác định 4 property setters cần:

| Parent DocType | Field | Property | Value | Lý do |
|---|---|---|---|---|
| `Item` | `is_stock_item` | `default` | `1` | RVHG SX bánh đậu xanh — mọi item dạng stock |
| `Batch` | `batch_id` | `unique` | `1` | Batch code phải unique toàn hệ thống cho traceability |
| `Supplier` | `supplier_group` | `mandatory` | `1` | Để FSMS Supplier Profile có thể link đúng |
| `Customer` | `territory` | `mandatory` | `1` | Để recall theo địa lý hoạt động |

→ 4 entries trong `property_setter.json`.

---

## 12. Master data fixtures

### 12.1 `fsms_document_category.json` (6 records)

```json
[
  {"doctype": "FSMS Document Category", "category_code": "QT", "category_name": "Quy trình hệ thống", "default_retention_years": 10, "review_frequency_months": 12},
  {"doctype": "FSMS Document Category", "category_code": "BM", "category_name": "Biểu mẫu", "default_retention_years": 5, "review_frequency_months": 24},
  {"doctype": "FSMS Document Category", "category_code": "HD", "category_name": "Hướng dẫn công việc", "default_retention_years": 5, "review_frequency_months": 24},
  {"doctype": "FSMS Document Category", "category_code": "PL", "category_name": "Phụ lục", "default_retention_years": 5, "review_frequency_months": 24},
  {"doctype": "FSMS Document Category", "category_code": "QĐ", "category_name": "Quy định / Quyết định", "default_retention_years": 10, "review_frequency_months": 12},
  {"doctype": "FSMS Document Category", "category_code": "KH", "category_name": "Kế hoạch", "default_retention_years": 10, "review_frequency_months": 12}
]
```

### 12.2 `fsms_ncr_source.json` (7 records)

```json
[
  {"doctype": "FSMS NCR Source", "source_code": "AUDIT", "source_name_vi": "Đánh giá nội bộ", "source_doctype": "FSMS Audit Execution", "default_severity": "Major"},
  {"doctype": "FSMS NCR Source", "source_code": "CCP_FAIL", "source_name_vi": "CCP vượt giới hạn", "source_doctype": "FSMS CCP Monitoring Log", "default_severity": "Critical"},
  {"doctype": "FSMS NCR Source", "source_code": "COMPLAINT", "source_name_vi": "Khiếu nại khách hàng", "source_doctype": "FSMS Customer Complaint", "default_severity": "Major"},
  {"doctype": "FSMS NCR Source", "source_code": "MATERIAL_REJECT", "source_name_vi": "NL/VT bị loại", "source_doctype": "FSMS Material Inspection Log", "default_severity": "Minor"},
  {"doctype": "FSMS NCR Source", "source_code": "CAL_FAIL", "source_name_vi": "Hiệu chuẩn thiết bị không đạt", "source_doctype": "FSMS Calibration Record", "default_severity": "Major"},
  {"doctype": "FSMS NCR Source", "source_code": "PROD_NC", "source_name_vi": "Sự không phù hợp trong SX", "source_doctype": "FSMS Production Nonconformity", "default_severity": "Minor"},
  {"doctype": "FSMS NCR Source", "source_code": "INTERNAL", "source_name_vi": "Báo cáo nội bộ", "source_doctype": null, "default_severity": "Minor"}
]
```

### 12.3 `fsms_risk_score_reference.json` (16 records)

A/B/C/D × 1/2/3/4 — bảng tham chiếu chấm điểm rủi ro cho QT 05. Em không lặp 16 dòng, format mẫu:

```json
{"doctype": "FSMS Risk Score Reference", "score_dimension": "A", "score_value": 1, "description": "Hiếm xảy ra (≥1 năm 1 lần hoặc ít hơn)", "examples": "Sự cố thiên tai lớn, dịch bệnh quốc gia"},
{"doctype": "FSMS Risk Score Reference", "score_dimension": "A", "score_value": 4, "description": "Xảy ra rất thường xuyên (hàng ngày)", "examples": "Sự cố thiết bị nhỏ, lỗi tem nhãn lẻ"},
...
```

### 12.4 `fsms_supplier_category.json` (2 records)

```json
[
  {"doctype": "FSMS Supplier Category", "category_code": "Loai_1", "description": "NCC nguyên liệu trực tiếp ảnh hưởng ATTP (đậu xanh, đường, bao bì tiếp xúc thực phẩm)", "evaluation_required": 1, "evaluation_frequency_months": 12},
  {"doctype": "FSMS Supplier Category", "category_code": "Loai_2", "description": "NCC vật tư phụ trợ không trực tiếp ảnh hưởng ATTP (văn phòng phẩm, dụng cụ vệ sinh)", "evaluation_required": 1, "evaluation_frequency_months": 24}
]
```

### 12.5 `fsms_emergency_scenario.json` (5 records)

Mapping PL.03.01 → PL.03.05:

```json
[
  {"doctype": "FSMS Emergency Scenario", "scenario_code": "PL.03.01", "scenario_name": "Ứng phó bão lũ", "scenario_type": "Thiên tai", "response_procedure": "Tham khảo PL.03.01"},
  {"doctype": "FSMS Emergency Scenario", "scenario_code": "PL.03.02", "scenario_name": "Phương án chữa cháy", "scenario_type": "Cháy nổ", "response_procedure": "Tham khảo PL.03.02"},
  {"doctype": "FSMS Emergency Scenario", "scenario_code": "PL.03.03", "scenario_name": "Ứng phó với điện", "scenario_type": "Mất điện", "response_procedure": "Tham khảo PL.03.03"},
  {"doctype": "FSMS Emergency Scenario", "scenario_code": "PL.03.04", "scenario_name": "Ứng phó dịch bệnh", "scenario_type": "Dịch bệnh", "response_procedure": "Tham khảo PL.03.04"},
  {"doctype": "FSMS Emergency Scenario", "scenario_code": "PL.03.05", "scenario_name": "Sản phẩm bị nhầm thông tin", "scenario_type": "Thông tin SP", "response_procedure": "Tham khảo PL.03.05"}
]
```

### 12.6 `fsms_prp_item_template.json` (11 records)

Theo ISO/TS 22002-1:2009 — 11 PRP groups:

| PRP code | Tên |
|---|---|
| PRP1 | Construction and layout of buildings |
| PRP2 | Layout of premises and workspace |
| PRP3 | Utilities — air, water, energy |
| PRP4 | Waste disposal |
| PRP5 | Equipment suitability, cleaning, maintenance |
| PRP6 | Management of purchased materials |
| PRP7 | Measures for prevention of cross-contamination |
| PRP8 | Cleaning and sanitizing |
| PRP9 | Pest control |
| PRP10 | Personnel hygiene and employee facilities |
| PRP11 | Rework |

Mỗi record có thêm `description_vi` + `monitoring_method_default` + `frequency_default`.

---

## 13. Dashboard fixtures

### 13.1 `dashboard.json` (1 record)

```json
{
  "doctype": "Dashboard",
  "name": "FSMS Director Dashboard",
  "module": "ISO 22000 FSMS",
  "is_default": 0,
  "is_standard": 1,
  "charts": [
    {"chart": "FSMS NCR Trend 12 Months", "width": "Half"},
    {"chart": "FSMS Audit Findings by Department", "width": "Half"},
    {"chart": "FSMS Risk Heatmap", "width": "Full"}
  ],
  "cards": [
    {"card": "FSMS Open NCR Count"},
    {"card": "FSMS NCR On-time Closure Rate"},
    {"card": "FSMS Recall Events YTD"},
    {"card": "FSMS Audit Findings Closure Rate"}
  ]
}
```

### 13.2 `dashboard_chart.json` (6 charts)
- FSMS NCR Trend 12 Months (Bar, stacked by severity)
- FSMS Audit Findings by Department (Donut)
- FSMS Risk Heatmap (Heatmap — Likelihood × Severity)
- FSMS Calibration Compliance (Gauge)
- FSMS Training Compliance (Gauge)
- FSMS Supplier Grade Distribution (Pie)

### 13.3 `number_card.json` (4 cards)
- FSMS Open NCR Count
- FSMS NCR On-time Closure Rate (computed via Server Script)
- FSMS Recall Events YTD
- FSMS Audit Findings Closure Rate (computed)

### 13.4 `workspace.json` (1 workspace)

```json
{
  "doctype": "Workspace",
  "name": "Bảng điều khiển ATTP",
  "label": "Bảng điều khiển ATTP",
  "module": "ISO 22000 FSMS",
  "icon": "shield",
  "for_user": "",
  "restrict_to_domain": "",
  "links": [
    {"label": "Phiếu yêu cầu hành động khắc phục", "type": "DocType", "link_to": "FSMS NCR"},
    {"label": "Sự kiện thu hồi", "type": "DocType", "link_to": "FSMS Recall Event"},
    {"label": "Kế hoạch HACCP", "type": "DocType", "link_to": "FSMS HACCP Plan"},
    {"label": "Đăng ký rủi ro", "type": "DocType", "link_to": "FSMS Risk Register"},
    ...
  ]
}
```

---

## 14. Reports (`fixtures/report.json`)

14 Custom Reports đã spec ở `05_integration_plan.md` §6. Mỗi cái có file `.py` riêng trong `iso22000_fsms/iso22000_fsms/report/<report_name>/` (theo Frappe convention).

---

## 15. Folder structure cuối cùng

Đây là layout mà `nextcode-build` sẽ scaffold:

```
iso22000_fsms/
├── README.md
├── LICENSE.txt
├── setup.py
├── requirements.txt
├── pyproject.toml
├── iso22000_fsms/
│   ├── __init__.py                      # __version__ = "1.0.0"
│   ├── hooks.py                         # đã spec ở §05
│   ├── modules.txt                      # 18 module names
│   ├── patches.txt                      # (empty initially; for future migrations)
│   ├── boot.py                          # extend_bootinfo
│   ├── workflow_validation.py           # OR-logic approval validator
│   ├── api.py                           # whitelisted REST endpoints
│   │
│   ├── fsms_core/
│   │   ├── doctype/
│   │   │   ├── fsms_settings/
│   │   │   ├── fsms_manual/
│   │   │   ├── fsms_policy/
│   │   │   ├── fsms_objective/
│   │   │   └── fsms_manual_revision/    # child table
│   │   └── api.py
│   │
│   ├── fsms_document_control/
│   │   ├── doctype/...
│   │   ├── api.py
│   │   └── tasks.py
│   │
│   ├── fsms_audit/
│   ├── fsms_ncr/
│   │   ├── doctype/
│   │   │   ├── fsms_ncr/
│   │   │   │   ├── fsms_ncr.json
│   │   │   │   ├── fsms_ncr.py        # validate, hooks
│   │   │   │   ├── fsms_ncr.js        # client-side hooks
│   │   │   │   ├── fsms_ncr_list.js   # list view customization
│   │   │   │   └── test_fsms_ncr.py
│   │   │   ├── fsms_ncr_source/
│   │   │   └── fsms_ncr_action_item/  # child
│   │   ├── api.py
│   │   ├── tasks.py
│   │   └── permissions.py
│   │
│   ├── fsms_recall/
│   ├── fsms_emergency/
│   ├── fsms_verification/
│   ├── fsms_context_risk/
│   ├── fsms_equipment/
│   ├── fsms_supplier/
│   ├── fsms_production/
│   ├── fsms_prp/
│   ├── fsms_sample/
│   ├── fsms_haccp/
│   ├── fsms_management_review/
│   ├── fsms_training/
│   ├── fsms_communication/
│   ├── fsms_traceability/
│   │
│   ├── fixtures/
│   │   ├── role.json
│   │   ├── custom_field.json
│   │   ├── custom_docperm.json
│   │   ├── property_setter.json
│   │   ├── workflow_state.json
│   │   ├── workflow.json
│   │   ├── workflow_action_master.json
│   │   ├── notification.json
│   │   ├── email_template.json
│   │   ├── print_format.json
│   │   ├── dashboard.json
│   │   ├── dashboard_chart.json
│   │   ├── number_card.json
│   │   ├── workspace.json
│   │   ├── report.json
│   │   ├── fsms_document_category.json
│   │   ├── fsms_ncr_source.json
│   │   ├── fsms_risk_score_reference.json
│   │   ├── fsms_supplier_category.json
│   │   ├── fsms_emergency_scenario.json
│   │   └── fsms_prp_item_template.json
│   │
│   ├── templates/
│   │   ├── notifications/
│   │   │   ├── ncr_pending_approval.html
│   │   │   ├── ncr_overdue.html
│   │   │   ├── recall_event_initiated.html
│   │   │   └── ... (12 templates)
│   │   └── pages/                       # Web Pages nếu cần
│   │
│   ├── public/
│   │   ├── css/
│   │   │   └── fsms.css                 # CSS prefix `fsms-` per ERPNext guideline
│   │   ├── js/
│   │   │   └── fsms_client.js           # Client-side helpers
│   │   └── images/
│   │       └── logo.png
│   │
│   ├── config/
│   │   ├── desktop.py
│   │   └── docs.py
│   │
│   └── translations/
│       └── vi.csv                       # Vietnamese translations (mặc định Frappe vẫn cần)
│
└── tests/
    ├── test_ncr_workflow.py
    ├── test_recall_fast_track.py
    ├── test_traceability.py
    ├── test_haccp_ccp_breach.py
    └── test_audit_to_ncr_chain.py
```

---

## 16. Install / Uninstall behavior

### 16.1 Install command

```bash
# On RVHG production v16
bench --site rvhg.local install-app iso22000_fsms
```

Kết quả:
1. Run `before_install` hook (check Frappe + ERPNext version compatibility)
2. Create DocType schemas (auto from JSON)
3. Run `after_install` hook → load fixtures sequentially:
   - Stage 1: Roles + Workflow States (no dependencies)
   - Stage 2: Custom Fields + Custom Permissions + Property Setters
   - Stage 3: Master data (Document Categories, NCR Sources, etc.)
   - Stage 4: Workflows + Workflow Actions + Workflow Action Masters
   - Stage 5: Notifications + Email Templates
   - Stage 6: Print Formats + Reports
   - Stage 7: Dashboards + Workspaces

### 16.2 Post-install manual setup

Anh sẽ cần làm thủ công 4 bước sau install:
1. Tạo `FSMS Settings` Single record (tên công ty, MST, scope, retention default)
2. Gán role cho từng User existing (BAT_HEAD = ai, TBP_xx = ai, ...)
3. Tạo `FSMS Department` mapping với Department core hiện có
4. Upload signature image cho Employee qua field `fsms_signature_image`

→ Em sẽ ship 1 wizard `FSMS Initial Setup Wizard` (Web Form) hỗ trợ 4 bước trên.

### 16.3 Uninstall

```bash
bench --site rvhg.local uninstall-app iso22000_fsms
```

→ Frappe auto-drop tables. Custom Fields trên ERPNext core sẽ được giữ trong database đến khi `bench migrate` chạy lần kế (theo Frappe behavior).

⚠️ **Cẩn trọng**: KHÔNG uninstall trên prod nếu có data thật → mất data. Test luôn trên staging trước.

---

## 17. Test plan (cho `nextcode-build` thực hiện)

### 17.1 Unit tests bắt buộc

| Test file | Cover |
|---|---|
| `test_ncr_workflow.py` | 7 transitions + auto-create reissued NCR + permlevel L2 enforcement |
| `test_recall_fast_track.py` | Phone approval flow + 24h SLA + audit trail completeness |
| `test_traceability.py` | Backward + forward trace correctness + drill outcome computation |
| `test_haccp_ccp_breach.py` | CCP out-of-limit auto creates NCR + severity mapping |
| `test_audit_to_ncr_chain.py` | Audit Finding → NCR auto-create + finding linkage |
| `test_supplier_evaluation.py` | Evaluation submit updates Supplier Profile + Approved List |
| `test_calibration_breach.py` | Failed calibration → NCR auto-create |
| `test_or_logic_approval.py` | TBP_dept can approve NCR for own dept; cannot for others; BAT_HEAD overrides |

### 17.2 Integration tests

| Test | Cover |
|---|---|
| End-to-end NCR lifecycle | Đề xuất → ... → Đã đóng + effectiveness check |
| End-to-end Recall (standard) | Recall Event → Plan → Report → Closed |
| End-to-end Recall (fast-track) | Phone approval → execute → retroactive GD |
| Audit cycle | Plan → Execution → Findings → NCRs → Summary |
| Document publish | DCR → approve → update Register Internal |

### 17.3 Performance tests

| Test | Target |
|---|---|
| Traceability backward query | ≤ 2 giây cho batch có ≤ 50 NL inputs |
| Traceability forward query | ≤ 2 giây cho batch giao ≤ 100 KH |
| GD Dashboard load | ≤ 3 giây với 1000 NCR records |
| NCR list view filter | ≤ 1 giây với 5000 records |

---

## 18. Acceptance criteria cuối cùng

Em handoff sang `nextcode-build` khi:

- [x] 01–06 design files đã được anh approve
- [x] QT 09 docx đã handover
- [x] Anh xác nhận RVHG đang chạy v16 (✓ done)
- [ ] Anh approve folder structure §15
- [ ] Anh approve install/uninstall flow §16
- [ ] Anh approve test plan §17
- [ ] Anh có repo Git để `nextcode-build` push code (hoặc em scaffold local rồi anh tạo repo)

---

## 19. Trạng thái + bước tiếp theo

- **Hoàn thành toàn bộ series 01–06 design**:
  - `00_document_inventory.md`
  - `01_business_model.md`
  - `02_doctype_blueprint.md`
  - `03_permission_matrix.md`
  - `04_workflow_blueprint.md`
  - `05_integration_plan.md`
  - **`06_fixtures_plan.md`** (file này)
  - + `QT 09 - Quy trinh Truy xuat Nguon goc.docx` (deliverable phụ, ban hành ngay được)
- **Đang chờ**: anh review file này + approve toàn bộ design package
- **Sau khi approve**: handoff sang `nextcode-build` để scaffold:
  - bench commands tạo app + tạo các module + tạo từng DocType
  - DocType JSON files (~64 chính + 28 child = 92 schema)
  - Python controller + hooks (~30 file `.py`)
  - JavaScript client hooks (~15 file `.js`)
  - 21 Print Format HTML/Jinja files (clone Word) + 17 Print Format mới (em soạn)
  - Fixtures JSON (~205 records)
  - Test files (~10 unit + integration)
  - Documentation (README, CHANGELOG, install guide)
  - Estimate: với `nextcode-build` chạy 4–6 phiên dài, scaffold xong code base đầu (anh review từng module trước khi mở tiếp)

---

**End of `06_fixtures_plan.md` — chờ anh review.**

---

## ✅ Final design summary

| File | Lines | Mục đích |
|---|---|---|
| 00_document_inventory.md | 235 | Map 52 file → tier |
| 01_business_model.md | 237 | Actors + 18 use cases + decisions |
| 02_doctype_blueprint.md | 1190 | 47 doctype + 28 child + ERPNext links |
| 03_permission_matrix.md | 670 | Role × DocType × permlevel × ifowner |
| 04_workflow_blueprint.md | 648 | 28 state machines + cross-cutting rules |
| 05_integration_plan.md | 940 | hooks + scheduled + GD dashboard + fast-track |
| 06_fixtures_plan.md | 720 | Complete fixtures specification |
| **Tổng** | **~4640 lines** | Đủ chi tiết để `nextcode-build` scaffold không cần đoán |

+ QT 09 (16.8 KB docx, 196 paragraph, 5 table, validated) — sẵn sàng ban hành chính thức.

Dự án đã sẵn sàng cho phase build.
