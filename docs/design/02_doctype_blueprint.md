# 02 — DocType Blueprint

> **App**: `iso22000_fsms` · Frappe v16 · ERPNext v16 dependency
> **Trạng thái**: Draft v0.1 — chờ review trước khi sang `03_permission_matrix.md`
> **Ngôn ngữ**: Vietnamese only
> **Form policy**: Online-first — Frappe form là source of truth, Print Format chỉ render PDF cuối lưu trữ

---

## 0. Conventions

### 0.1 Naming
- **App slug**: `iso22000_fsms`
- **Module structure** (mỗi module = 1 thư mục Python trong app):

```
iso22000_fsms/
├── fsms_core/                    # Settings, Manual, Objective
├── fsms_document_control/        # QT 01 — Doc + Records
├── fsms_audit/                   # QT 01 — Internal Audit
├── fsms_ncr/                     # QT 01 — NCR/CAR  (TÂM ĐIỂM)
├── fsms_recall/                  # QT 02
├── fsms_emergency/               # QT 03
├── fsms_verification/            # QT 04
├── fsms_context_risk/            # QT 05
├── fsms_equipment/               # QT 06
├── fsms_supplier/                # QT 07
├── fsms_production/              # QT 08
├── fsms_prp/                     # PRP
├── fsms_sample/                  # QĐ.01 lưu mẫu
├── fsms_haccp/                   # KH.HACCP
├── fsms_management_review/       # Họp xem xét lãnh đạo
├── fsms_training/                # GAP-FILL clause 7.2
├── fsms_communication/           # GAP-FILL clause 7.4
└── fsms_traceability/            # GAP-FILL clause 8.3 — QT 09 mới
```

- **DocType prefix**: `FSMS` (English engineering name) + Vietnamese label
  - Ví dụ: `name = "FSMS NCR"`, `label = "Phiếu yêu cầu hành động khắc phục"`
- **Naming series**: theo từng DocType, dạng `<MA>.{YYYY}.{MM}.-.#####` (chốt từng cái ở §1–18)
- **Field prefix tránh xung đột Bootstrap**: theo guideline ERPNext của anh — class CSS phải prefix `fsms-` cho Print Format custom

### 0.2 Common fields cho mọi DocType online-first

Mọi DocType (trừ Master/Settings) có set field chuẩn để hỗ trợ workflow + audit trail + signature:

| Field | Type | Mục đích |
|-------|------|----------|
| `workflow_state` | Link → Workflow State | Frappe workflow engine chuẩn |
| `prepared_by` | Link → Employee | Người soạn / khởi tạo (auto = current user) |
| `prepared_on` | Datetime | auto |
| `prepared_signature` | Attach Image | render Print Format (link `Employee.signature_image`) |
| `reviewed_by` | Link → Employee | Người soát xét |
| `reviewed_on` | Datetime | auto khi action review |
| `reviewed_signature` | Attach Image | auto từ Employee |
| `approved_by` | Link → Employee | Người phê duyệt |
| `approved_on` | Datetime | auto khi action approve |
| `approved_signature` | Attach Image | auto từ Employee |
| `effective_date` | Date | Ngày hiệu lực (cho tài liệu hệ thống) |
| `revision_no` | Int | Lần sửa đổi |

→ Các field này nhúng vào **chuẩn template** của mỗi DocType phù hợp. Em sẽ KHÔNG lặp lại trong từng spec dưới đây — coi như default (DocType nào không cần thì sẽ note rõ).

### 0.3 Print Format policy
- Mỗi DocType có Print Format **giống layout Word hiện tại** (theo yêu cầu Q7).
- Build bằng Jinja + HTML, CSS class prefix `fsms-`.
- File mẫu để generate: 21 BM trong zip → render từ DocType data thay vì giấy điền tay.
- Mặc định khổ A4 dọc, font Times New Roman 12pt (giữ giống bản Word) hoặc DejaVu Serif (fallback Linux).

### 0.4 Single DocType note
- "Single DocType" = chỉ có 1 record duy nhất toàn hệ thống (ví dụ Sổ tay ATTP, FSMS Settings).
- "Master" = nhiều record nhưng không workflow, không signature (ví dụ Document Category).

---

## 1. Module `fsms_core`

| # | DocType | Type | Naming | Mục đích |
|---|---------|------|--------|----------|
| 1.1 | `FSMS Settings` | Single | n/a | Tên công ty, MST, địa chỉ, scope, std version, fiscal year cycle, retention years |
| 1.2 | `FSMS Manual` | Single | n/a | Sổ tay ATTP — replace file Word `So tay an toan thuc pham.doc` |
| 1.3 | `FSMS Policy` | Single | n/a | Chính sách ATTP — replace `Chính sách ATTP.doc` |
| 1.4 | `FSMS Objective` | Doctype | `OBJ.{YYYY}.-.###` | Mục tiêu ATTP — multi-record có review định kỳ |
| 1.5 | `FSMS Department` | Master | n/a | (Có thể tận dụng `Department` core; nếu cần thuộc tính FSMS riêng thì link 1-1) |

### 1.2 `FSMS Manual` — fields chính
- `version_no` (Data), `effective_date`, `next_review_date`
- `scope_organization` (Small Text — phạm vi tổ chức)
- `scope_location` (Small Text)
- `scope_product` (Small Text — "Sản xuất bánh đậu xanh, bột đậu")
- `exclusions` (Long Text)
- `policy_link` → `FSMS Policy`
- `objective_table` (Table → `FSMS Objective Snapshot` — child với year + objective list)
- `revision_history` (Table → `FSMS Manual Revision` — số lần / ngày / nội dung sửa đổi / soạn / soát / duyệt)
- `attached_org_chart` (Attach Image)
- Workflow: `Draft → Reviewed → Approved → Published → Obsolete`

### 1.4 `FSMS Objective` — fields chính
- `objective_code` (Data, naming series)
- `objective_year` (Int)
- `objective_text` (Small Text)
- `kpi_metric` (Data — đơn vị đo, ví dụ "% lô đạt", "số sự cố ATTP")
- `target_value` (Float)
- `actual_value` (Float, update theo dõi)
- `responsible_department` → Department
- `responsible_employee` → Employee
- `review_frequency` (Select: Hàng tháng / Hàng quý / Năm)
- `last_review_date`, `next_review_date`
- `status` (Select: Đang theo dõi / Đạt / Không đạt / Hủy)
- `linked_actions` (Table → mỗi dòng link CAR phát sinh nếu không đạt)

---

## 2. Module `fsms_document_control` (QT 01 phần kiểm soát tài liệu + hồ sơ)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 2.1 | `FSMS Document Register Internal` | Master | `DM-NB.###` | BM.01.02 |
| 2.2 | `FSMS Document Register External` | Master | `DM-BN.###` | BM.01.03 |
| 2.3 | `FSMS Records Register` | Master | `DM-HS.###` | BM.01.04 |
| 2.4 | `FSMS Document Change Request` | Doctype | `YCSDTL.{YYYY}.-.###` | BM.01.01 |
| 2.5 | `FSMS Document Category` | Master | n/a | (Bảng tham chiếu loại tài liệu: QT, BM, HD, PL, QĐ, KH...) |

### 2.4 `FSMS Document Change Request` (BM.01.01)
- `request_no` (auto)
- `request_date` (auto)
- `requestor` → Employee
- `target_document_type` (Select: nội bộ / bên ngoài) → Link `Document Register Internal/External`
- `target_document` → Dynamic Link
- `change_type` (Select: Sửa đổi / Hủy bỏ / Phát hành mới)
- `current_revision` (Int)
- `proposed_revision` (Int)
- `reason` (Long Text)
- `proposed_changes` (Long Text)
- `impact_assessment` (Long Text)
- `attachments` (Attach)
- Workflow: `Đề xuất → Soát xét → Phê duyệt → Phát hành → Đóng | Từ chối`

### 2.1 `FSMS Document Register Internal` fields chính
- `doc_code` (Data, unique — vd "QT 01", "BM.01.07", "HD.07.01")
- `doc_name` (Data — tên đầy đủ)
- `doc_category` → `FSMS Document Category`
- `parent_procedure` → Self link (cho BM thuộc QT)
- `current_revision` (Int)
- `effective_date`
- `next_review_date`
- `owner_department` → Department
- `owner_employee` → Employee
- `retention_years` (Int)
- `attached_file` (Attach)
- `obsolete` (Check)
- `change_history` (Table → mỗi dòng = 1 lần sửa, link `FSMS Document Change Request`)

### 2.2 `FSMS Document Register External` fields chính
*(BM.01.03)*
- `doc_code`, `doc_name`, `issuer` (Data — cơ quan ban hành), `issued_date`, `received_date`, `current_version`, `legal_basis` (Check), `applicable_scope`, `attached_file`, `obsolete`

### 2.3 `FSMS Records Register` fields chính
*(BM.01.04 — danh mục hồ sơ)*
- `record_code`, `record_name`, `responsible_department`, `responsible_position`, `storage_location`, `retention_period_years`, `disposal_method` (Select: Hủy / Lưu trữ vĩnh viễn / Số hóa)

---

## 3. Module `fsms_audit` (QT 01 phần đánh giá nội bộ)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 3.1 | `FSMS Audit Program` | Doctype | `CTĐG.{YYYY}.-.##` | (master kế hoạch năm) |
| 3.2 | `FSMS Audit Plan` | Doctype | `KHĐG.{YYYY}.-.###` | BM.01.05 |
| 3.3 | `FSMS Audit Plan Item` | Child | n/a | (dòng trong audit plan) |
| 3.4 | `FSMS Audit Checklist Template` | Master | `CL-TPL.###` | BM.01.06 (template) |
| 3.5 | `FSMS Audit Checklist Item` | Child | n/a | (câu hỏi checklist) |
| 3.6 | `FSMS Audit Execution` | Doctype | `BB.ĐG.{YYYY}.-.###` | BM.01.06 (filled) |
| 3.7 | `FSMS Audit Finding` | Child | n/a | (mỗi finding trong audit) |
| 3.8 | `FSMS Audit Observation` | Doctype | `LY.{YYYY}.-.###` | BM.01.08 (điểm lưu ý) |
| 3.9 | `FSMS Audit Summary` | Doctype | `TH-ĐG.{YYYY}.-.##` | BM.01.09 |

### 3.1 `FSMS Audit Program` — chương trình đánh giá năm
- `program_year` (Int, unique)
- `program_objective` (Long Text)
- `coverage_scope` (Long Text — bộ phận/quá trình)
- `audit_frequency` (Select: Quý / 6 tháng / Năm)
- `lead_auditor` → Employee
- `audit_plan_table` (Table → list tham chiếu các `Audit Plan` con)
- Workflow: `Draft → Approved → Executing → Closed`

### 3.2 `FSMS Audit Plan` (BM.01.05)
- `plan_no`, `audit_program` → Audit Program, `audit_round` (Int — lần thứ N trong năm)
- `audit_date_from`, `audit_date_to`
- `audit_scope` (Small Text)
- `criteria_documents` (Table → ISO 22000 clauses + internal procedures)
- `audit_team` (Table → `FSMS Audit Plan Item` — auditor + auditee + clause + slot time)
- `kickoff_meeting_date`, `closing_meeting_date`
- Workflow: `Draft → Notified → Executing → Reported → Closed`

### 3.3 `FSMS Audit Plan Item` (Child)
- `auditor` → Employee, `auditee_department` → Department, `auditee_employee` → Employee, `clause` (Data — vd "ISO 22000 §8.5"), `time_slot` (Data), `notes`

### 3.4 `FSMS Audit Checklist Template` (BM.01.06 dạng template)
- `template_name`, `template_clause` (Data), `version`, `items` (Table → `FSMS Audit Checklist Item`)

### 3.5 `FSMS Audit Checklist Item` (Child)
- `seq` (Int), `clause` (Data), `question` (Small Text), `expected_evidence` (Small Text), `compliance_level` (Select: C / NC Major / NC Minor / Obs / N/A — chỉ có khi đã filled), `evidence_observed` (Long Text), `attached_evidence` (Attach)

### 3.6 `FSMS Audit Execution` — instance đánh giá thực tế
- `audit_plan` → Audit Plan, `auditee_department`, `auditor` → Employee, `auditee_signature`, `auditor_signature`
- `checklist_used` → `FSMS Audit Checklist Template`
- `responses` (Table → `FSMS Audit Checklist Item` filled — copy từ template)
- `findings` (Table → `FSMS Audit Finding`)
- `auto_create_ncr` (Check — checkbox: với mỗi finding NC Major/Minor, tự sinh `FSMS NCR` link)
- Workflow: `Đang thực hiện → Hoàn thành → Đã đóng`

### 3.7 `FSMS Audit Finding` (Child)
- `finding_type` (Select: NC Major / NC Minor / Observation / OFI), `finding_description` (Long Text), `clause_violated` (Data), `responsible_department`, `linked_ncr` → `FSMS NCR` (tự fill khi auto_create_ncr)

### 3.8 `FSMS Audit Observation` (BM.01.08)
*(Điểm lưu ý — không phải finding, nhẹ hơn)*
- `observation_date`, `observed_by` → Employee, `area`, `description`, `recommendation`, `follow_up_required` (Check), `linked_ncr` → NCR (nếu escalate)

### 3.9 `FSMS Audit Summary` (BM.01.09)
*(Bảng tổng hợp kết quả đánh giá — dạng aggregate report)*
- `summary_year`, `audit_program` → Audit Program
- `audit_executions` (Table → list `Audit Execution`)
- `total_audits`, `total_nc_major`, `total_nc_minor`, `total_obs`
- `closed_on_time_count`, `closed_late_count`, `still_open_count`
- `recurring_issues` (Long Text)
- `improvement_recommendations` (Long Text)
- (Single per year hoặc Doctype tự generate)

---

## 4. Module `fsms_ncr` — TÂM ĐIỂM (QT 01 phần CAR + clause 10)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 4.1 | `FSMS NCR` | Doctype | `KP.{YYYY}.-.####` | BM.01.07 |
| 4.2 | `FSMS NCR Source` | Master | n/a | Bảng tham chiếu nguồn NCR |
| 4.3 | `FSMS NCR Action Item` | Child | n/a | Hành động con |

### 4.1 `FSMS NCR` (BM.01.07) — workflow trung tâm

**Fields chính:**

| Section | Field | Type | Notes |
|---------|-------|------|-------|
| Header | `ncr_no` | Auto-naming | KP.YYYY.-.#### |
| Header | `ncr_date` | Date | Ngày phát sinh |
| Header | `ncr_source` | Select | Audit / Customer Complaint / CCP Fail / PRP Fail / Supplier Reject / Equipment Fail / Internal Report |
| Header | `source_reference_doctype` | Dynamic Link | Liên kết về object trigger (Audit Execution, Recall Event...) |
| Header | `source_reference_name` | Dynamic Link |  |
| Header | `severity` | Select | Major / Minor / Critical |
| Header | `ncr_type` | Select | Khắc phục (Corrective) / Phòng ngừa (Preventive) |
| **Phần 1** | `nonconformity_description` | Long Text | "1. Nội dung đề xuất hành động" |
| **Phần 1** | `evidence_attachment` | Attach | "Hồ sơ kèm theo số:" |
| **Phần 1** | `affected_department` | Link → Department | "Bộ phận / Người nhận" |
| **Phần 1** | `affected_employee` | Link → Employee |  |
| **Phần 1** | `requestor` | Link → Employee | "Người đề xuất" |
| **Phần 1** | `requestor_signature` | Image | auto from Employee |
| **Phần 1** | `requestor_date` | Date | auto |
| **Phần 2** | `root_cause_analysis` | Long Text | "2. Phân tích nguyên nhân" |
| **Phần 2** | `proposed_action` | Long Text | "biện pháp đề xuất" |
| **Phần 2** | `analyzer` | Link → Employee | "Người phân tích và đề xuất" |
| **Phần 2** | `analyzer_signature` | Image |  |
| **Phần 2** | `analyzer_date` | Date |  |
| **Phần 2** | `assigned_to` | Link → Employee | "Người thực hiện" |
| **Phần 2** | `proposed_completion_date` | Date | "Ngày đề xuất hoàn thành" |
| **Phần 3** | `approver_remarks` | Long Text | "3. Phê duyệt — Nhận xét" |
| **Phần 3** | `actual_completion_date` | Date | "Ngày hoàn thành" |
| **Phần 3** | `approver` | Link → Employee | "Trưởng ban ISO/trưởng bộ phận" |
| **Phần 3** | `approver_signature` | Image |  |
| **Phần 3** | `approver_date` | Date |  |
| Action items | `action_items` | Table → `FSMS NCR Action Item` | Sub-tasks tracking |
| **Phần 4** | `verification_remarks` | Long Text | "4. Đánh giá kết quả & xác nhận hoàn thành" |
| **Phần 4** | `verification_outcome` | Select | Đạt yêu cầu / Không đạt — chuyển tiếp |
| **Phần 4** | `verifier` | Link → Employee | "Người đánh giá" |
| **Phần 4** | `verifier_signature` | Image |  |
| **Phần 4** | `verifier_date` | Date |  |
| **Phần 4** | `reissued_to_ncr` | Link → `FSMS NCR` | Nếu không đạt → tham chiếu phiếu mới |
| **Phần 4** | `reissued_from_ncr` | Link → `FSMS NCR` | Reverse link |
| Attachments | `attachment_report` | Attach | "kèm theo báo cáo nếu có" |
| Closure | `closed_date` | Date |  |
| Closure | `effectiveness_check_date` | Date | (verify sau N ngày — clause 10.2) |
| Closure | `effectiveness_check_result` | Select | Hiệu lực / Không hiệu lực — mở NCR mới |

**Workflow** (Frappe Workflow engine):

```
[Đề xuất] —submit→ [Phân tích]
[Phân tích] —submit→ [Chờ phê duyệt]
[Chờ phê duyệt] —approve→ [Đang thực hiện]
[Chờ phê duyệt] —reject→ [Phân tích]
[Đang thực hiện] —complete→ [Đang xác minh]
[Đang xác minh] —pass→ [Đã đóng]
[Đang xác minh] —fail→ [Chuyển tiếp]   (auto-create new NCR linked via reissued_to_ncr)
```

**Server-side hooks**:
- `validate`: nếu `verification_outcome = "Không đạt"` → block save unless `reissued_to_ncr` đã set hoặc auto-tạo
- `on_submit`: send email notification tới `affected_department.head` + `assigned_to`
- Scheduled job nightly: tìm NCR `Đang thực hiện` quá hạn (now > proposed_completion_date) → tạo Notification + escalate

### 4.2 `FSMS NCR Source` (Master)
*(Bảng tra cứu nguồn — extensible)*
- `source_code`, `source_name_vi`, `source_doctype` (Data — DocType có thể trigger), `default_severity`

### 4.3 `FSMS NCR Action Item` (Child)
- `seq`, `action_description`, `responsible` → Employee, `due_date`, `done_date`, `status` (Select: Mở / Đang thực hiện / Hoàn thành / Hủy), `evidence` (Attach)

---

## 5. Module `fsms_recall` (QT 02)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 5.1 | `FSMS Recall Event` | Doctype | `THSP.{YYYY}.-.##` | (master event) |
| 5.2 | `FSMS Recall Plan` | Doctype | `KH-TH.{YYYY}.-.##` | BM.02.01 |
| 5.3 | `FSMS Recall Plan Item` | Child | n/a | dòng kế hoạch chi tiết |
| 5.4 | `FSMS Recall Affected Batch` | Child | n/a | lô bị ảnh hưởng |
| 5.5 | `FSMS Recall Distribution` | Child | n/a | đã phân phối tới đâu |
| 5.6 | `FSMS Recall Report` | Doctype | `BC-TH.{YYYY}.-.##` | BM.02.02 |
| 5.7 | `FSMS Recall Team Member` | Child | n/a | thành viên ban thu hồi |

### 5.1 `FSMS Recall Event`
- `event_no`, `event_date`
- `trigger_source` (Select: Cơ quan QLNN / Khiếu nại KH / Phát hiện nội bộ / Sự cố kỹ thuật)
- `defect_severity` (Select: Cấp 1 (nguy hiểm tử vong) / Cấp 2 (ảnh hưởng SK) / Cấp 3 (thương hiệu))
- `recall_level` (Select: A — đến người sử dụng / B — đến hệ thống PP & cửa hàng / C — chỉ phân phối sỉ)
  - **Auto-suggest rule**: Cấp 1 → Mức A, Cấp 2 → Mức B, Cấp 3 → Mức C (override được)
- `defect_description` (Long Text)
- `affected_items` (Table → mỗi dòng link `Item` core)
- `affected_batches` (Table → `FSMS Recall Affected Batch` link `Batch` core)
- `recall_team` (Table → `FSMS Recall Team Member`)
- `recall_plan` → `FSMS Recall Plan` (1-1)
- `recall_report` → `FSMS Recall Report`
- `linked_ncr` → `FSMS NCR` (auto-create on submit)
- Workflow: `Phát sinh → Lập kế hoạch → Đang thu hồi → Bảo quản → Báo cáo → Đóng`

### 5.2 `FSMS Recall Plan` (BM.02.01)
- `plan_no`, `recall_event` → Recall Event
- `recall_scope` (Long Text — phạm vi địa lý + kênh)
- `recall_method` (Long Text)
- `target_completion_date`
- `quarantine_location` (Data — "khu vực hàng thu hồi có khóa")
- `quarantine_responsible` → Employee
- `disposal_proposal` (Long Text)
- `notification_template` (Long Text — mẫu thông báo gửi KH)
- `plan_items` (Table → `FSMS Recall Plan Item`)
- Workflow: `Draft → Approved by GĐ → Executing → Completed`

### 5.3 `FSMS Recall Plan Item` (Child)
- `seq`, `task_description`, `responsible` → Employee, `due_date`, `done_date`, `status`, `evidence`

### 5.4 `FSMS Recall Affected Batch` (Child)
- `batch` → `Batch` (ERPNext core)
- `item` → `Item`
- `production_date` (auto pull from Batch)
- `expiry_date`
- `total_produced_qty` (Float)
- `currently_in_stock_qty` (Float — pull từ Stock Ledger Entry)
- `distributed_qty` (Float)
- `customer_returned_qty` (Float)
- `recovered_qty` (Float — cập nhật theo tiến độ thu hồi)
- `recovery_rate_pct` (Float — auto)

### 5.5 `FSMS Recall Distribution` (Child)
- `customer` → `Customer` core
- `delivery_note` → `Delivery Note` (link)
- `distributed_qty`, `recovered_qty`, `remaining_qty`, `customer_response_status`

### 5.6 `FSMS Recall Report` (BM.02.02)
- `report_no`, `recall_event` → Recall Event
- `executive_summary` (Long Text)
- `total_affected_qty`, `total_recovered_qty`, `total_recovery_rate_pct`
- `quarantine_kept_qty`, `disposed_qty`
- `disposal_method`, `disposal_evidence` (Attach)
- `cost_impact` (Currency)
- `cause_summary` (Long Text)
- `corrective_actions_table` (Table → link NCR)
- `external_notification_required` (Check — báo cáo cơ quan QLNN)
- `external_notification_evidence` (Attach)
- Workflow: `Draft → Reviewed → Approved by GĐ → Submitted to authority → Closed`

### 5.7 `FSMS Recall Team Member` (Child)
- `employee` → Employee, `role_in_team` (Select: Trưởng ban / Thành viên / Liên lạc với KH / Thực thi thu hồi vật lý / Báo cáo)

---

## 6. Module `fsms_emergency` (QT 03)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 6.1 | `FSMS Emergency Scenario` | Master | n/a | PL.03.01–05 (bão lũ, cháy, điện, dịch bệnh, thông tin SP) |
| 6.2 | `FSMS Emergency Event` | Doctype | `KC.{YYYY}.-.###` | (event log) |
| 6.3 | `FSMS Emergency Drill` | Doctype | `DT-KC.{YYYY}.-.##` | (kế hoạch & kết quả thực tập) |
| 6.4 | `FSMS Fire Equipment` | Master | n/a | (danh mục thiết bị PCCC) |
| 6.5 | `FSMS Fire Equipment Log` | Doctype | `STBPCCC.{YYYY}.-.###` | BM.03.01 |
| 6.6 | `FSMS Disease Event Log` | Doctype | `SDB.{YYYY}.-.###` | BM.03.02 |
| 6.7 | `FSMS Safety Equipment Inspection` | Doctype | `KDTBAT.{YYYY}.-.###` | BM.03.03 |

### 6.1 `FSMS Emergency Scenario` (Master — Phụ lục)
- `scenario_code` (Data — vd "PL.03.01")
- `scenario_name`
- `scenario_type` (Select: Thiên tai / Cháy nổ / Mất điện / Dịch bệnh / Thông tin SP)
- `response_procedure` (Long Text)
- `attached_file`
- `responsible_team` (Table → Employee)
- `equipment_required` (Table → link Fire Equipment / Asset)

### 6.2 `FSMS Emergency Event`
- `event_no`, `event_date`, `event_time`
- `scenario` → Emergency Scenario
- `description` (Long Text)
- `severity` (Select)
- `affected_areas` (Long Text)
- `actions_taken` (Long Text)
- `damages` (Long Text)
- `casualties` (Int)
- `external_authority_notified` (Check)
- `linked_ncr` → NCR (escalate nếu cần)
- `closing_remarks`
- Workflow: `Đang xảy ra → Đã xử lý → Đã báo cáo → Đóng`

### 6.3 `FSMS Emergency Drill`
- `drill_no`, `drill_date`, `scenario` → Emergency Scenario
- `participants` (Table → Employee)
- `objectives`, `script`, `findings`, `improvements`
- `next_drill_date`
- `linked_meeting_minutes` (Attach — biên bản thực tập)
- *(replaces "Biên bản thực tập phương án PCCC.doc")*

### 6.4 `FSMS Fire Equipment` (Master)
- `equipment_code`, `equipment_name`, `equipment_type` (Select: Bình chữa cháy / Vòi nước / Báo cháy / Chỉ dẫn / Cứu hộ)
- `manufacturer`, `purchase_date`, `expiry_date`, `last_inspection_date`, `next_inspection_date`
- `location` (Data)
- `status` (Select: OK / Cần kiểm tra / Hỏng / Hết hạn)

### 6.5 `FSMS Fire Equipment Log` (BM.03.01)
- `log_date`, `equipment` → Fire Equipment
- `inspector` → Employee
- `condition_check` (Select: OK / Cần thay / Cần bảo dưỡng)
- `pressure_value` (Float — cho bình)
- `expiry_remaining_days` (Int — auto)
- `notes`
- *(record book pattern — list-view friendly)*

### 6.6 `FSMS Disease Event Log` (BM.03.02)
- `log_date`, `disease_type` (Data — COVID / cúm / dịch tả lợn...), `affected_employee` → Employee, `symptoms`, `quarantine_required` (Check), `return_to_work_date`, `affected_area`, `disinfection_action`, `recorded_by`

### 6.7 `FSMS Safety Equipment Inspection` (BM.03.03)
- `inspection_date`, `equipment` → Asset core, `inspection_type` (Select: KĐ định kỳ / KĐ đột xuất), `result` (Select: Đạt / Không đạt), `certificate_no`, `certificate_attachment`, `next_inspection_date`, `inspector_organization`, `cost`

---

## 7. Module `fsms_verification` (QT 04)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 7.1 | `FSMS Verification Plan` | Doctype | `KH-TT.{YYYY}.-.##` | BM.04.01 |
| 7.2 | `FSMS Verification Object` | Child | n/a | đối tượng cần thẩm tra |
| 7.3 | `FSMS Verification Report` | Doctype | `BC-TT.{YYYY}.-.###` | BM.04.02 |
| 7.4 | `FSMS Verification Test` | Child | n/a | mỗi test trong report |

### 7.1 `FSMS Verification Plan` (BM.04.01)
- `plan_no`, `plan_year`, `plan_period` (Select: Q1 / Q2 / Q3 / Q4 / Năm)
- `objects_to_verify` (Table → `FSMS Verification Object`)
- `external_lab_engaged` (Check)
- `external_lab_name` (Data — yêu cầu ISO 17025)
- `external_lab_accreditation` (Attach)
- Workflow: `Draft → Approved → Executing → Reported → Closed`

### 7.2 `FSMS Verification Object` (Child)
*(Đối tượng theo §QT 04: HACCP plan, OPRP, monitoring records, PRP, Quy phạm SX, hiệu chuẩn, đào tạo, sức khỏe NV, hạn SD)*
- `object_type` (Select: Hạ tầng SX/Bảo quản / HACCP — Mô tả SP / HACCP — Sơ đồ QT / HACCP — Bố trí mặt bằng / HACCP — Phân loại khu vực / HACCP — Phân tích mối nguy / HACCP — CCP, CP / Kế hoạch HACCP / Kế hoạch OPRP / Hồ sơ giám sát / Chương trình PRP / Quy phạm SX / Hiệu chuẩn / Đào tạo / Sức khỏe NV / Hạn SD)
- `linked_doctype` (Dynamic Link), `linked_name`
- `verification_method` (Long Text)
- `frequency` (Select: Tháng / Quý / 6 tháng / Năm)
- `responsible` → Employee
- `status` (Select: Chưa thực hiện / Đang thực hiện / Hoàn thành)

### 7.3 `FSMS Verification Report` (BM.04.02)
- `report_no`, `verification_plan` → Plan
- `executed_date`
- `tests_performed` (Table → `FSMS Verification Test`)
- `external_lab_results` (Attach)
- `findings` (Long Text)
- `nonconformities_found` (Table → link NCR)
- `recommendations`
- `next_verification_date`
- Workflow: `Draft → Reviewed → Approved → Closed`

### 7.4 `FSMS Verification Test` (Child)
- `object` → Verification Object
- `method`, `acceptance_criteria`, `actual_result`, `pass_fail` (Select), `evidence` (Attach), `notes`

---

## 8. Module `fsms_context_risk` (QT 05)

| # | DocType | Type | Naming | Print Format mapping |
|---|---------|------|--------|------------------------|
| 8.1 | `FSMS Interested Party` | Doctype | `BQT.###` | BM.05.01 |
| 8.2 | `FSMS Interested Party Requirement` | Child | n/a | yêu cầu của bên QT |
| 8.3 | `FSMS Risk Register` | Doctype | `RR.{YYYY}.-.###` | BM.05.02 |
| 8.4 | `FSMS Risk Score Reference` | Master | n/a | bảng điểm A/B/C/D |
| 8.5 | `FSMS Risk Action` | Child | n/a | hành động xử lý risk |

### 8.1 `FSMS Interested Party` (BM.05.01)
- `party_name`, `party_type` (Select: Khách hàng trực tiếp / Nhà cung cấp / Nhà thầu phụ / Chính quyền sở tại / Cơ quan pháp luật / Cổ đông / Người lao động / Đối thủ cạnh tranh / Khác)
- `relevance_to_fsms` (Long Text)
- `requirements` (Table → `FSMS Interested Party Requirement`)
- `review_year` (Int)
- `next_review_date`
- `responsible_employee` → Employee

### 8.2 `FSMS Interested Party Requirement` (Child)
- `requirement_text`, `current_compliance_status` (Select: Đáp ứng / Một phần / Chưa / N/A), `action_plan`, `responsible`, `due_date`, `linked_objective` → FSMS Objective

### 8.3 `FSMS Risk Register` (BM.05.02)
*(Theo công thức QT 05: Total = A + B + C + D, ngưỡng 9/11/16)*
- `risk_no`, `risk_year`, `risk_description` (Long Text)
- `risk_category` (Select: ATTP / Tài chính / Pháp lý / Vận hành / Thiên tai / NCC / Khác)
- `risk_owner` → Department, `risk_owner_employee` → Employee
- `score_a_likelihood` (Int 1–4 — Khả năng xảy ra)
- `score_b_consequence` (Int 1–4 — Hậu quả)
- `score_c_severity` (Int 1–4 — Mức độ nghiêm trọng)
- `score_d_detectability` (Int 1–4 — Khả năng phát hiện, **đảo nghịch**: dễ phát hiện = điểm thấp)
- `total_score` (Int — auto = A+B+C+D)
- `risk_level` (Select — auto theo total: ≤9 "Theo dõi" / 10–11 "Kiểm soát" / 12–16 "Ứng phó kịp thời")
- `treatment_strategy` (Select: Tránh / Giảm thiểu / Chuyển giao / Chấp nhận)
- `actions` (Table → `FSMS Risk Action`)
- `last_review_date`, `next_review_date`
- `linked_ncr` (Table → NCR khi risk thực sự xảy ra)

### 8.4 `FSMS Risk Score Reference` (Master)
- `score_dimension` (Select: A / B / C / D)
- `score_value` (Int 1–4)
- `description` (text — VD: "A=4: Xảy ra rất thường xuyên, hàng ngày")
- `examples` (text)
- *(Để training NV mới đánh giá nhất quán)*

### 8.5 `FSMS Risk Action` (Child)
- `action_description`, `responsible` → Employee, `due_date`, `done_date`, `status`, `effectiveness` (Select: Hiệu quả / Một phần / Không), `evidence`

---

## 9. Module `fsms_equipment` (QT 06 — chia 2 phần)

QT 06 phân biệt rõ: **thiết bị sản xuất** (vận hành/bảo dưỡng/sửa chữa) vs **thiết bị đo** (kiểm định/hiệu chuẩn). Thiết kế tách 2 nhánh:

### 9.A Thiết bị sản xuất

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 9.1 | `FSMS Production Equipment` | Master (link `Asset`) | `TBSX.###` | (danh mục — mới, theo QT 06) |
| 9.2 | `FSMS Equipment Maintenance Plan` | Doctype | `KH-BD.{YYYY}.-.##` | (mới — BM.06.01 đề xuất) |
| 9.3 | `FSMS Equipment Maintenance Log` | Doctype | `SO-BDSC.{YYYY}.-.###` | (mới — BM.06.02 đề xuất) |
| 9.4 | `FSMS Equipment Maintenance Item` | Child | n/a | mỗi lần BD/SC |

### 9.B Thiết bị đo

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 9.5 | `FSMS Measurement Equipment` | Master (link `Asset`) | `TBĐO.###` | (mới — BM.06.03 đề xuất) |
| 9.6 | `FSMS Calibration Plan` | Doctype | `KH-HC.{YYYY}.-.##` | (mới — BM.06.04 đề xuất) |
| 9.7 | `FSMS Calibration Record` | Doctype | `HC.{YYYY}.-.###` | (mới — BM.06.05 đề xuất) |

> **Note Q8 anh dặn**: QT 06 chưa có BM riêng → em thiết kế 5 BM mới (BM.06.01–05) base trên nội dung QT 06. Anh xem fields dưới đây có khớp ý không.

### 9.1 `FSMS Production Equipment`
- `equipment_code` (unique), `equipment_name`, `linked_asset` → Asset
- `manufacturer`, `model`, `serial_no`, `purchase_date`, `installation_date`
- `production_line` (Data)
- `location` (Data)
- `responsible_operator` → Employee
- `status` (Select: Đang vận hành / Bảo dưỡng / Sửa chữa / Ngừng / Thanh lý)
- `attached_manual` (Attach — sách HD vận hành)
- `attached_sop` (Attach)

### 9.2 `FSMS Equipment Maintenance Plan` (BM.06.01)
- `plan_year`, `equipment` → Production Equipment, `frequency` (Select: Tuần / Tháng / Quý / 6 tháng / Năm)
- `maintenance_type` (Select: Bảo dưỡng định kỳ / Vệ sinh / Hiệu chỉnh / Thay phụ tùng)
- `scope_of_work` (Long Text)
- `responsible_team` (Table → Employee)
- `estimated_downtime_hours` (Float)
- `estimated_cost` (Currency)
- `scheduled_dates` (Table — danh sách ngày trong năm theo frequency)

### 9.3 `FSMS Equipment Maintenance Log` (BM.06.02)
*(Sổ ghi BD/SC — record book)*
- `log_date`, `equipment` → Production Equipment, `event_type` (Select: BD / SC / Vệ sinh)
- `description` (Long Text)
- `parts_replaced` (Table — link Item nếu có)
- `cost`, `downtime_hours`
- `performed_by` (Table → Employee or vendor name)
- `result` (Select: OK / Chưa khắc phục / Cần đầu tư mới)
- `next_scheduled_date`
- `attached_invoice` (Attach)

### 9.5 `FSMS Measurement Equipment`
*(Phương tiện đo — separate from asset SX)*
- `equipment_code` (unique), `equipment_name`, `linked_asset` → Asset
- `measurement_type` (Select: Khối lượng / Nhiệt độ / Độ ẩm / Áp suất / pH / Lực / Khác)
- `measurement_range`, `accuracy_class`, `manufacturer`, `model`, `serial_no`
- `calibration_method` (Select: Kiểm định nhà nước / Hiệu chuẩn nội bộ / Hiệu chuẩn ngoại)
- `calibration_frequency` (Select: 6 tháng / Năm / 2 năm / Theo lô)
- `last_calibration_date`, `next_calibration_date`
- `current_status` (Select: Hợp chuẩn / Hết hạn / Hỏng / Đã thanh lý)
- `linked_ccp` (Table → HACCP CCP — thiết bị đo phục vụ CCP nào)

### 9.6 `FSMS Calibration Plan` (BM.06.04)
- `plan_year`, `equipment_table` (Table → Measurement Equipment + scheduled date)
- `external_calibration_org` (Data)
- Workflow: `Draft → Approved → Executing → Closed`

### 9.7 `FSMS Calibration Record` (BM.06.05)
- `cal_no`, `cal_date`, `equipment` → Measurement Equipment
- `cal_type` (Select: KĐ NN / HC nội bộ / HC ngoại)
- `external_org` (Data — nếu HC ngoại)
- `accreditation_attached` (Attach — chứng chỉ ISO 17025 nếu có)
- `cal_result` (Select: Đạt / Không đạt / Đạt sau hiệu chỉnh)
- `cal_certificate_no`, `cal_certificate_attached` (Attach)
- `validity_period_months` (Int)
- `next_cal_due_date` (auto)
- `linked_ncr` → NCR (nếu không đạt → ảnh hưởng CCP)

---

## 10. Module `fsms_supplier` (QT 07)

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 10.1 | `FSMS Supplier Category` | Master | n/a | Loại 1 / Loại 2 (per QT 07) |
| 10.2 | `FSMS Supplier Profile` | Master (link `Supplier`) | n/a | mở rộng Supplier core |
| 10.3 | `FSMS Supplier Evaluation` | Doctype | `ĐG-NCC.{YYYY}.-.###` | BM.07.01 |
| 10.4 | `FSMS Supplier Evaluation Criteria` | Child | n/a | từng tiêu chí + điểm |
| 10.5 | `FSMS Approved Supplier List` | Single (yearly) hoặc Doctype | `DSNCC.{YYYY}` | BM.07.02 |
| 10.6 | `FSMS Material Quality Control Plan` | Master | `KH-KSCL.{YYYY}` | HD.07.01 |
| 10.7 | `FSMS Material Inspection Log` | Doctype | `KTNL.{YYYY}.-.####` | BM.07.03 |

### 10.1 `FSMS Supplier Category` (Master)
- `category_code` (Loai_1 / Loai_2)
- `description` (Long Text — định nghĩa từ QT 07)
- `evaluation_required` (Check)
- `evaluation_frequency_months` (Int)

### 10.2 `FSMS Supplier Profile`
- `supplier` → `Supplier` (ERPNext core, 1-1)
- `category` → Supplier Category
- `is_pd_approved` (Check — NCU-PD)
- `approval_date`, `approval_expiry_date`
- `iso_certificates` (Table → cert_type / cert_no / valid_until / attachment)
- `regulatory_licenses` (Attach)
- `last_evaluation_date`, `last_evaluation_score`, `last_evaluation_grade` (Select: A / B / C / D)
- `current_status` (Select: Đang sử dụng / Tạm ngưng / Loại bỏ / Mới)
- `disqualification_reason` (Long Text)

### 10.3 `FSMS Supplier Evaluation` (BM.07.01)
- `eval_no`, `eval_date`, `supplier` → Supplier
- `evaluator` → Employee
- `evaluation_period` (Select: Định kỳ / Đột xuất / Đầu vào)
- `criteria` (Table → `FSMS Supplier Evaluation Criteria`)
- `total_score` (Float — auto sum × weight)
- `grade` (Select: A / B / C / D — auto theo total_score)
- `recommendation` (Select: Tiếp tục / Theo dõi / Cảnh báo / Loại bỏ)
- `comments` (Long Text)
- Workflow: `Draft → Reviewed → Approved`
- `on_submit`: cập nhật `Supplier Profile.last_evaluation_*`

### 10.4 `FSMS Supplier Evaluation Criteria` (Child)
- `criterion_name` (Data — vd "Chất lượng nguyên liệu")
- `weight` (Float — tổng weight = 1.0 hoặc 100)
- `score` (Int 1–10 hoặc 1–5, chốt ở fixtures)
- `weighted_score` (Float — auto)
- `evidence` (Long Text)

### 10.5 `FSMS Approved Supplier List` (BM.07.02)
*(Có thể là DocType yearly + auto-regenerate, hoặc Single)*
- `list_year`, `effective_date`
- `suppliers` (Table → Supplier + Category + Grade + Approval expiry + Notes)
- `published_by`, `revision_no`

### 10.6 `FSMS Material Quality Control Plan` (HD.07.01)
- `plan_year`
- `materials` (Table → mỗi dòng: Item / Inspection method / Sampling rate / Acceptance criteria / Frequency)

### 10.7 `FSMS Material Inspection Log` (BM.07.03)
*(Sổ kiểm tra chất lượng vật tư hàng hóa nhập vào — record book, link với Purchase Receipt)*
- `inspection_date`
- `purchase_receipt` → Purchase Receipt (ERPNext core)
- `supplier` (auto from PR)
- `items` (Table — mỗi dòng = 1 item: Item / Batch / Qty / Inspection result / Defect type / Decision (Nhận / Trả / Cách ly))
- `inspector` → Employee, `inspector_signature`
- `linked_ncr` → NCR (nếu reject)

---

## 11. Module `fsms_production` (QT 08)

> **Note Q8 anh dặn**: QT 08 chưa có BM riêng → thiết kế BM mới (BM.08.01–04 đề xuất).

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 11.1 | `FSMS Production Order` | Doctype (link `Work Order`) | `LSX.{YYYY}.-.####` | (mới — BM.08.01 đề xuất) |
| 11.2 | `FSMS Production Process Monitoring` | Doctype | `GS-SX.{YYYY}.-.####` | (mới — BM.08.02 đề xuất) |
| 11.3 | `FSMS Production Step Record` | Child | n/a | mỗi công đoạn |
| 11.4 | `FSMS Finished Product Inspection` | Doctype | `KCS-TP.{YYYY}.-.####` | SỔ THEO DÕI KIỂM TRA THÀNH PHẨM (đã có) |
| 11.5 | `FSMS Production Nonconformity` | Doctype | `KPH-SX.{YYYY}.-.####` | (mới — BM.08.04 đề xuất) |

### 11.1 `FSMS Production Order` (mở rộng Work Order)
- `work_order` → `Work Order` (ERPNext, 1-1)
- `production_date`, `shift` (Select: Sáng / Chiều / Đêm)
- `production_team_lead` → Employee
- `target_batch` → `Batch`
- `production_line` (Data)
- `haccp_plan` → `FSMS HACCP Plan` (auto khi item match)
- `prp_checklist_required` (Check — auto)
- `linked_monitoring` → Production Process Monitoring (1-1)
- `linked_finished_inspection` → Finished Product Inspection (1-1)
- `traceability_pull_link` → Traceability Backward Trace
- `status` (Select: Lên kế hoạch / Đang SX / Hoàn thành / KCS / Nhập kho / Đã đóng)

### 11.2 `FSMS Production Process Monitoring` (BM.08.02)
*(Sổ giám sát quá trình SX — ghi chép theo công đoạn HACCP)*
- `production_order` → Production Order
- `step_records` (Table → `FSMS Production Step Record`)
- `total_ccp_violations` (Int — auto)
- `total_oprp_violations` (Int — auto)

### 11.3 `FSMS Production Step Record` (Child)
- `step_seq`, `process_step` (Data — link to HACCP Process Step)
- `start_time`, `end_time`
- `operator` → Employee
- `parameter_value` (Float)
- `parameter_unit` (Data)
- `acceptance_min`, `acceptance_max` (Float — pull from HACCP CCP/OPRP definition)
- `is_within_limit` (Check — auto)
- `is_ccp` (Check — pull)
- `is_oprp` (Check — pull)
- `corrective_action_taken` (Long Text)
- `linked_ncr` → NCR (auto if out-of-limit)

### 11.4 `FSMS Finished Product Inspection` (Sổ theo dõi kiểm tra thành phẩm)
- `inspection_date`, `production_order` → Production Order
- `batch` → Batch (auto)
- `item` → Item
- `qty_inspected`, `qty_passed`, `qty_failed`
- `inspection_table` (Table — chỉ tiêu kiểm tra: Tên / Tiêu chuẩn / Kết quả / Đạt? / Ghi chú)
- `decision` (Select: Đạt / Treo / Loại)
- `kcs_inspector` → Employee
- `linked_ncr` → NCR (nếu loại)
- `release_to_warehouse_date`

### 11.5 `FSMS Production Nonconformity`
*(KPH phát hiện trong SX, trước KCS — light-weight version of NCR cho ghi nhanh, có thể escalate sang full NCR)*
- `event_date`, `production_order` → Production Order, `step` (Data), `description`, `quantity_affected`, `disposition` (Select: Tái chế / Loại / Cách ly / Sử dụng có điều kiện), `linked_ncr` → NCR

---

## 12. Module `fsms_prp`

> **Note Q8 anh dặn**: Sổ kiểm tra vệ sinh CN — dùng bản .doc (bỏ bản .xlsx).

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 12.1 | `FSMS PRP Program` | Single | n/a | He thong PRP.doc |
| 12.2 | `FSMS PRP Item` | Child | n/a | mỗi quy phạm thuộc PRP |
| 12.3 | `FSMS Worker Hygiene Daily` | Doctype | `VSCN.{YYYY}.-.####` | So kiem tra ve sinh Cong nhan hang ngay.doc |
| 12.4 | `FSMS Worker Hygiene Item` | Child | n/a | mỗi nhân viên + check items |
| 12.5 | `FSMS Sanitation Report` | Doctype | `BC-VS.{YYYY}.-.##` | Bao cao tinh hinh ve sinh.doc |
| 12.6 | `FSMS PRP Checklist Template` | Master | n/a | (template các area cleaning) |
| 12.7 | `FSMS Cleaning Log` | Doctype | `VS.{YYYY}.-.####` | (record book chung — vệ sinh khu vực, máy, dụng cụ) |

### 12.1 `FSMS PRP Program` (Single)
- `program_version`, `effective_date`
- `prp_items` (Table → `FSMS PRP Item`)
- `responsible_team` (Table → Employee)
- `attached_master_doc` (Attach — file Word gốc)

### 12.2 `FSMS PRP Item` (Child)
*(Theo Codex Alimentarius / ISO/TS 22002-1: 11 PRP groups)*
- `prp_code` (Select: PRP1-Construction / PRP2-Layout / PRP3-Utilities / PRP4-Waste / PRP5-Equipment / PRP6-Material / PRP7-Cross-contam / PRP8-Cleaning / PRP9-Pest / PRP10-Personnel / PRP11-Rework — pre-fill từ fixtures)
- `description` (Long Text)
- `monitoring_method` (Long Text)
- `frequency`
- `acceptance_criteria`
- `responsible` → Employee
- `linked_template` → PRP Checklist Template

### 12.3 `FSMS Worker Hygiene Daily` (Sổ KT vệ sinh CN hàng ngày)
- `inspection_date`, `shift`, `inspector` → Employee
- `worker_inspections` (Table → `FSMS Worker Hygiene Item`)
- `total_workers`, `total_passed`, `total_failed`
- `linked_ncr` → NCR (nếu fail rate cao)

### 12.4 `FSMS Worker Hygiene Item` (Child)
- `worker` → Employee
- `health_card_valid` (Check)
- `uniform_clean` (Check)
- `personal_hygiene` (Check — móng tay, tóc, trang sức)
- `hand_wash_compliance` (Check)
- `no_illness_symptoms` (Check)
- `total_pass` (Check — auto AND của trên)
- `notes_if_fail`
- `corrective_action`

### 12.5 `FSMS Sanitation Report`
- `report_period` (Select: Tuần / Tháng / Quý)
- `report_year`, `report_period_value`
- `worker_hygiene_summary` (Table — pull từ Daily logs)
- `area_cleaning_summary` (Table — pull từ Cleaning Log)
- `pest_control_summary` (Long Text)
- `chemical_storage_check` (Long Text)
- `findings`, `improvements`
- Workflow: `Draft → Reviewed → Approved`

### 12.7 `FSMS Cleaning Log` (record book chung)
- `log_date`, `area_or_equipment` (Data), `cleaning_type` (Select: Hằng ngày / Hằng tuần / Sau ca / Sâu)
- `chemicals_used` (Table → Item link)
- `concentration`, `contact_time_min`
- `cleaner` → Employee
- `verifier` → Employee
- `result` (Select: Đạt / Cần làm lại)

---

## 13. Module `fsms_sample` (QĐ.01)

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 13.1 | `FSMS Sample Retention Policy` | Single | n/a | QĐ.01 |
| 13.2 | `FSMS Sample Retention Log` | Doctype | `LM.{YYYY}.-.####` | Sổ lưu mẫu.doc |

### 13.1 `FSMS Sample Retention Policy` (Single)
- `policy_version`, `effective_date`
- `retention_period_months` (Int)
- `sample_size_per_batch` (Float — đơn vị g/ml)
- `storage_location` (Data)
- `storage_temperature_min`, `_max` (Float)
- `disposal_method` (Long Text)
- `responsible` → Employee
- `attached_master` (Attach)

### 13.2 `FSMS Sample Retention Log`
- `sample_date`, `production_order` → Production Order, `batch` → Batch, `item` → Item
- `sample_qty`, `sample_unit`
- `expected_disposal_date` (auto = sample_date + retention_period)
- `actual_disposal_date`
- `disposal_method`
- `disposal_evidence` (Attach)
- `taken_by` → Employee, `taken_by_signature`
- `disposed_by` → Employee, `disposed_by_signature`
- `notes`
- `quality_test_during_retention` (Table — kết quả test giữa kỳ nếu có)

---

## 14. Module `fsms_haccp`

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 14.1 | `FSMS HACCP Plan` | Doctype | `HACCP.{ITEM_CODE}.-.##` | KH.HACCP.01 + 02 |
| 14.2 | `FSMS HACCP Process Step` | Child | n/a | sơ đồ quy trình SX |
| 14.3 | `FSMS HACCP Hazard` | Child | n/a | mối nguy theo bước |
| 14.4 | `FSMS HACCP Decision Tree` | Child | n/a | câu hỏi Q1–Q4 codex |
| 14.5 | `FSMS HACCP CCP` | Child | n/a | điểm CCP |
| 14.6 | `FSMS HACCP OPRP` | Child | n/a | điểm OPRP |
| 14.7 | `FSMS CCP Monitoring Schedule` | Master | n/a | (lịch monitoring tự sinh từ HACCP Plan) |
| 14.8 | `FSMS CCP Monitoring Log` | Doctype | `CCP.{YYYY}.-.####` | (mới) |

### 14.1 `FSMS HACCP Plan`
*(1 plan / 1 product line — bánh đậu xanh, bột đậu)*
- `plan_no`, `item` → Item, `product_description_doctype` → mở rộng Item
- `plan_version`, `effective_date`, `next_review_date`
- `team_members` (Table → Employee)
- `intended_use` (Long Text)
- `target_consumer` (Long Text)
- `process_flow_attachment` (Attach — sơ đồ vẽ tay scan; fields process_steps là dạng list)
- `process_steps` (Table → `FSMS HACCP Process Step`)
- `hazard_analysis` (Table → `FSMS HACCP Hazard`)
- `ccps` (Table → `FSMS HACCP CCP`)
- `oprps` (Table → `FSMS HACCP OPRP`)
- `validation_records` (Table — link Verification Report)
- `linked_recall_plan` → Recall Plan (template recall cho item này)
- Workflow: `Draft → Reviewed → Approved → Published → Under Revision → Obsolete`

### 14.2 `FSMS HACCP Process Step` (Child)
- `step_no`, `step_name`, `description`, `parameters` (Long Text), `is_ccp_candidate` (Check)

### 14.3 `FSMS HACCP Hazard` (Child)
- `process_step` (Data — link Process Step seq)
- `hazard_type` (Select: Sinh học / Hóa học / Vật lý / Dị ứng)
- `hazard_description`
- `severity` (Int 1–4)
- `likelihood` (Int 1–4)
- `risk_level` (Int — auto = severity × likelihood)
- `is_significant` (Check — auto theo threshold)
- `existing_controls` (Long Text)
- `decision_tree_q1`–`q4` (Check — Codex 4 câu hỏi)
- `is_ccp` (Check — auto)
- `is_oprp` (Check — auto)

### 14.5 `FSMS HACCP CCP` (Child)
- `ccp_no` (vd CCP-1, CCP-2)
- `process_step` (link)
- `hazard_controlled` (link Hazard)
- `critical_limit` (Data — vd "Nhiệt độ ≥ 90°C trong 5 phút")
- `monitoring_what` (Long Text)
- `monitoring_how` (Long Text)
- `monitoring_frequency` (Data)
- `monitoring_who`
- `corrective_action` (Long Text)
- `verification_method`, `verification_frequency`
- `record_keeping` (Long Text)
- `linked_measurement_equipment` → Measurement Equipment

### 14.6 `FSMS HACCP OPRP` (Child) — same fields as CCP nhưng cho OPRP

### 14.8 `FSMS CCP Monitoring Log`
*(Mỗi ca SX, cho mỗi CCP)*
- `log_date`, `production_order` → Production Order
- `ccp` → HACCP CCP (link)
- `measurement_value` (Float), `measurement_unit`
- `is_within_limit` (Check — auto compare critical_limit)
- `monitor` → Employee
- `corrective_action_taken` (Long Text — nếu out-of-limit)
- `linked_ncr` → NCR (auto-create nếu out-of-limit)
- `verifier` → Employee, `verification_date`

---

## 15. Module `fsms_management_review` (clause 9.3)

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 15.1 | `FSMS Management Review` | Doctype | `XXLD.{YYYY}.-.##` | (mới — biên bản họp) |
| 15.2 | `FSMS Management Review Input` | Child | n/a | input clause 9.3.2 |
| 15.3 | `FSMS Management Review Output` | Child | n/a | output clause 9.3.3 |

### 15.1 `FSMS Management Review`
*(Per QT 01 §5: lồng ghép họp giao ban hoặc cuộc họp tổng kết năm — flexible)*
- `review_no`, `review_date`, `review_type` (Select: Lồng ghép họp giao ban / Họp xem xét chuyên đề / Họp tổng kết năm)
- `chairperson` → Employee (default GĐ)
- `participants` (Table → Employee)
- `reviewed_period_from`, `_to`
- `inputs` (Table → `Management Review Input` — covering 9.3.2 a-i)
- `outputs` (Table → `Management Review Output` — covering 9.3.3)
- `meeting_minutes` (Long Text hoặc Attach)
- `actions_arising` (Table → link NCR / Risk Action)
- Workflow: `Đã lên lịch → Đang họp → Đã họp → Đã ban hành → Đóng`

### 15.2 `FSMS Management Review Input` (Child)
- `input_topic` (Select: Trạng thái CAR từ kỳ trước / Thay đổi nội bộ + bên ngoài / Hiệu lực FSMS / Trends + KPI / Đánh giá NCC / Audit results / Recall events / NC + correction / Verification results / Risk + cơ hội / Đào tạo + năng lực / Resource sufficiency / Communication / Other)
- `input_data_summary` (Long Text)
- `linked_doctype`, `linked_name` (Dynamic Link tới object cụ thể)

### 15.3 `FSMS Management Review Output` (Child)
- `output_type` (Select: Quyết định cải tiến hiệu lực FSMS / Cập nhật FSMS / Resource needs / Cập nhật mục tiêu / Khác)
- `decision_text`, `responsible` → Employee, `due_date`, `linked_ncr` → NCR

---

## 16. Module `fsms_training` (GAP-FILL clause 7.2)

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 16.1 | `FSMS Training Course` | Master | `KH-ĐT.###` | (mới) |
| 16.2 | `FSMS Training Plan` | Doctype | `KH-ĐT.{YYYY}.-.##` | (mới) |
| 16.3 | `FSMS Training Session` | Doctype | `BĐT.{YYYY}.-.####` | (mới — biên bản đào tạo) |
| 16.4 | `FSMS Training Attendance` | Child | n/a | điểm danh + kết quả |
| 16.5 | `FSMS Competency Matrix` | Single (yearly) | n/a | (yêu cầu năng lực theo position) |

### 16.1 `FSMS Training Course`
- `course_code`, `course_name`, `category` (Select: ATTP cơ bản / HACCP / GMP / PRP / Recall drill / Internal audit / Khác)
- `objectives`, `target_audience`, `duration_hours`, `frequency_required` (Select: Once / Annual / Bi-annual)
- `passing_score` (Float)
- `attached_material` (Attach)

### 16.2 `FSMS Training Plan` — kế hoạch đào tạo năm
- `plan_year`, `courses` (Table → Course + scheduled date + target audience)

### 16.3 `FSMS Training Session`
- `session_no`, `session_date`, `course` → Course
- `trainer` → Employee or external
- `attendees` (Table → `FSMS Training Attendance`)
- `evaluation_result_overall`
- `meeting_minutes` (Attach)
- Workflow: `Lên lịch → Đã thực hiện → Đã đánh giá → Đóng`

### 16.4 `FSMS Training Attendance` (Child)
- `employee` → Employee, `attended` (Check), `pre_test_score`, `post_test_score`, `passed` (Check), `certificate` (Attach), `next_refresher_date`

### 16.5 `FSMS Competency Matrix`
*(Cho từng `Designation` của ERPNext, list courses required)*
- `matrix_year`, `matrix_table` (Table → Designation × Course × Required (Check) × Refresher cycle)

---

## 17. Module `fsms_communication` (GAP-FILL clause 7.4)

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 17.1 | `FSMS Communication Plan` | Single | n/a | matrix giao tiếp |
| 17.2 | `FSMS Communication Log` | Doctype | `LL.{YYYY}.-.####` | (mới) |
| 17.3 | `FSMS Customer Complaint` | Doctype | `KN-KH.{YYYY}.-.####` | (mới) |

### 17.1 `FSMS Communication Plan` (Single)
- `internal_matrix` (Table — Topic × From department × To department × Frequency × Method)
- `external_matrix` (Table — Topic × Counterparty type (KH/NCC/QLNN) × Trigger × Method × Responsible)

### 17.2 `FSMS Communication Log`
- `log_date`, `direction` (Select: Internal / Outbound / Inbound)
- `counterparty_type` (Select: NV nội bộ / KH / NCC / QLNN / Khác)
- `counterparty_link_doctype` (Dynamic Link)
- `counterparty_link_name`
- `subject`, `content`, `medium` (Select: Email / Phone / Meeting / Letter / Zalo / Khác)
- `attachment` (Attach)
- `follow_up_required` (Check), `linked_ncr` → NCR

### 17.3 `FSMS Customer Complaint`
- `complaint_no`, `complaint_date`, `customer` → Customer
- `complaint_channel` (Select: Hotline / Email / Đại diện KD / Cơ quan QLNN / Mạng xã hội)
- `complaint_subject` (Long Text)
- `affected_item` → Item, `affected_batch` → Batch
- `severity` (Select: Cấp 1 / 2 / 3 — same as Recall Event mapping)
- `auto_create_recall_event` (Check)
- `auto_create_ncr` (Check)
- `linked_recall_event` → Recall Event
- `linked_ncr` → NCR
- `resolution_text`, `resolution_date`, `customer_satisfied` (Check)
- Workflow: `Mới → Đang xử lý → Đã giải quyết → Đóng`

---

## 18. Module `fsms_traceability` (GAP-FILL clause 8.3 — QT 09 mới)

> **Q8 anh dặn**: Thiết kế thêm QT truy xuất nguồn gốc base trên QT 02 + QT 07 + QT 08. Em đề xuất gọi là `QT 09 — Truy xuất nguồn gốc`. Nội dung quy trình em ghi tóm tắt cuối module này.

| # | DocType | Type | Naming | Print Format |
|---|---------|------|--------|---------------|
| 18.1 | `FSMS Traceability Settings` | Single | n/a | tham số truy xuất |
| 18.2 | `FSMS Traceability Drill` | Doctype | `DT-TXNG.{YYYY}.-.##` | (mới — diễn tập trace) |
| 18.3 | `FSMS Traceability Trace` | Doctype | `TXNG.{YYYY}.-.####` | (mới — kết quả 1 lần truy xuất) |
| 18.4 | `FSMS Trace Backward Link` | Child | n/a | trace ngược: lô SX → NL → NCC |
| 18.5 | `FSMS Trace Forward Link` | Child | n/a | trace xuôi: lô SX → KH cuối |

### 18.1 `FSMS Traceability Settings` (Single)
- `target_trace_time_minutes` (Int — vd 120 phút theo QT 02)
- `mandatory_drill_frequency_months` (Int)
- `last_drill_date`, `last_drill_result` (Select: Đạt / Không đạt)

### 18.2 `FSMS Traceability Drill`
- `drill_no`, `drill_date`
- `selected_batch` → Batch (random hoặc có chủ đích)
- `start_time`, `target_completion_time`, `actual_completion_time`
- `time_taken_minutes` (Int — auto)
- `is_within_target` (Check — auto vs Settings)
- `forward_links` (Table → Trace Forward Link)
- `backward_links` (Table → Trace Backward Link)
- `drill_outcome` (Select: Đạt — đúng giờ + đầy đủ / Đạt một phần / Không đạt)
- `gaps_identified` (Long Text)
- `linked_ncr` → NCR (nếu không đạt)

### 18.3 `FSMS Traceability Trace` (real trace, không phải drill)
*(Khi có recall hoặc QLNN yêu cầu — auto link Recall Event)*
- `trace_no`, `trace_date`, `trigger` (Select: Recall / QLNN yêu cầu / KH yêu cầu / Drill)
- `linked_recall_event` → Recall Event
- `target_batch` → Batch
- `forward_links`, `backward_links` (same Tables)
- `report_attached` (Attach)

### 18.4 `FSMS Trace Backward Link` (Child)
- `target_batch` → Batch (lô SX cuối)
- `material_item` → Item (NL)
- `material_batch` → Batch (lô NL)
- `supplier` → Supplier
- `supplier_lot_no` (Data)
- `purchase_receipt` → Purchase Receipt
- `received_date`
- `qty_used_in_target_batch` (Float)

### 18.5 `FSMS Trace Forward Link` (Child)
- `target_batch` → Batch (lô SX gốc)
- `delivery_note` → Delivery Note
- `customer` → Customer
- `delivered_date`
- `delivered_qty`
- `currently_recovered_qty` (cho recall)

### Note QT 09 — Quy trình truy xuất (em soạn nội dung tóm tắt, anh review)
1. **Mục đích**: Trong vòng 2 giờ, từ 1 lô SX bất kỳ, xác định được:
   - Backward: NL nào, NCC nào, lô NL nào, ngày nhận
   - Forward: đã giao cho KH nào, thời gian, số lượng còn lại
2. **Phạm vi**: Mọi lô SX của mọi item trong scope FSMS
3. **Trigger**: Recall, yêu cầu QLNN, yêu cầu KH, diễn tập (≥ 2 lần/năm)
4. **Tiến trình**: User chọn Batch → Frappe query Stock Ledger Entry + Purchase Receipt + Delivery Note + Work Order BOM → render Trace
5. **Diễn tập định kỳ**: 6 tháng/lần, chọn batch random, đo thời gian
6. **Hồ sơ lưu**: 5 năm (theo retention chung)

---

## 19. Cross-cutting integration

### 19.1 ERPNext core link summary

| Frappe core DocType | FSMS module sử dụng |
|----------------------|---------------------|
| `Item` | HACCP Plan, Recall Affected Batch, Production Order, Sample Retention, Material Inspection |
| `Batch` | Recall, Sample Retention, CCP Monitoring, Production, Traceability |
| `Customer` | Recall Distribution, Communication Log, Customer Complaint, Trace Forward |
| `Supplier` | Supplier Profile, Evaluation, Approved List, Material Inspection, Trace Backward |
| `Employee` | TẤT CẢ — signature, ownership, action |
| `Department` | Permission scoping, ownership |
| `Designation` | Competency Matrix |
| `Asset` | Production Equipment, Measurement Equipment |
| `Work Order` | Production Order |
| `Purchase Receipt` | Material Inspection, Trace Backward |
| `Delivery Note` | Recall Distribution, Trace Forward |
| `Quality Procedure` | (extend nếu phù hợp — em propose KHÔNG extend, tạo song song để không ràng schema core) |
| `Quality Meeting` | Management Review (có thể tận dụng template) |

### 19.2 Auto-create chain (server hooks)

```
Audit Finding (NC Major/Minor) ─┐
CCP Out-of-Limit ───────────────┤
Customer Complaint (severe) ────┼──→ FSMS NCR (auto-create)
Material Inspection Reject ─────┤
Calibration Fail ───────────────┤
Production Nonconformity ───────┘

Customer Complaint (Cấp 1/2) ──→ FSMS Recall Event (auto-suggest)
Recall Event ──→ FSMS NCR (auto-create on submit)
Recall Event ──→ FSMS Traceability Trace (auto-create)
```

### 19.3 Notifications & SLA
- NCR overdue: nightly job → Email + In-app notification
- Document review due (next_review_date < today + 30): monthly digest email
- Calibration due (next_cal_due_date < today + 14): weekly notification
- Audit Plan kickoff approaching: 7 days notice
- Sample retention disposal due: weekly digest
- Risk re-review due: monthly digest

---

## 20. DocType count summary

| Module | Doctype | Single | Master | Child | Tổng |
|--------|---------|--------|--------|-------|------|
| 1. core | 1 | 3 | 1 | — | 5 |
| 2. document_control | 1 | — | 4 | — | 5 |
| 3. audit | 6 | — | 1 | 4 | 11 |
| 4. ncr | 1 | — | 1 | 1 | 3 |
| 5. recall | 3 | — | — | 4 | 7 |
| 6. emergency | 5 | — | 2 | — | 7 |
| 7. verification | 2 | — | — | 2 | 4 |
| 8. context_risk | 2 | — | 1 | 2 | 5 |
| 9. equipment | 4 | — | 2 | 1 | 7 |
| 10. supplier | 4 | — | 3 | 1 | 8 |
| 11. production | 4 | — | — | 1 | 5 |
| 12. prp | 4 | 1 | 1 | 2 | 8 |
| 13. sample | 1 | 1 | — | — | 2 |
| 14. haccp | 2 | — | 1 | 5 | 8 |
| 15. mgmt_review | 1 | — | — | 2 | 3 |
| 16. training | 2 | 1 | 1 | 1 | 5 |
| 17. communication | 2 | 1 | — | — | 3 |
| 18. traceability | 2 | 1 | — | 2 | 5 |
| **TOTAL** | **47** | **8** | **17** | **28** | **101** |

> ~47 DocType business + 8 Single + 17 Master + 28 Child Tables = **~100 DocType + Child Table** tổng.
>
> So với estimate ban đầu (~50 DocType), số tăng vì em tách Child Tables rõ ràng. Số DocType "có UI list view" thực sự = 47 + 17 = **64**.

---

## 21. Trạng thái + bước tiếp theo

- **Đã hoàn thành**: 00 inventory + 01 business model + **02 doctype blueprint**
- **Đang chờ**: Anh review file này, đặc biệt:
  - Naming series (có muốn unify pattern khác không?)
  - Phần 4 NCR — workflow 7 trạng thái có hợp ý anh không?
  - Phần 9 — 5 BM mới cho QT 06 em đề xuất
  - Phần 11 — 4 BM mới cho QT 08 em đề xuất
  - Phần 14 HACCP — chia OPRP riêng có quá tải không (có thể gộp vào CCP với flag)?
  - Phần 18 — QT 09 truy xuất nguồn gốc — anh confirm trước khi em soạn full text QT 09
- **Sau khi duyệt 02**: Em sang `03_permission_matrix.md` — Role × DocType × permlevel × ifowner

---

**End of `02_doctype_blueprint.md` — chờ anh review.**
