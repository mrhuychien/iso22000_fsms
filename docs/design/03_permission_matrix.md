# 03 — Permission Matrix

> **App**: `iso22000_fsms` · Frappe v16
> **Trạng thái**: Draft v0.1 — chờ review trước khi sang `04_workflow_blueprint.md`
> **Phụ thuộc**: `01_business_model.md` (actor model) + `02_doctype_blueprint.md` (DocType list)

---

## 1. Roles recap

| Role code | Role name (Frappe role) | Vai trò nghiệp vụ | Số lượng dự kiến |
|-----------|-------------------------|-------------------|------------------|
| `GD` | FSMS Director | Giám đốc | 1 |
| `BAT_HEAD` | FSMS Manager | Trưởng Ban ATTP | 1 |
| `BAT_MEMBER` | FSMS Team Member | Thành viên Ban ATTP (cross-functional) | 4–6 |
| `TBP_KH` | FSMS Planning Lead | Trưởng BP Kế hoạch–Tổng hợp | 1 |
| `TBP_SX` | FSMS Production Lead | Trưởng BP Sản xuất | 1 |
| `TBP_KT` | FSMS Accounting Lead | Trưởng BP Kế toán | 1 |
| `TBP_KD` | FSMS Sales Lead | Trưởng BP Kinh doanh | 1 |
| `AUDITOR` | FSMS Internal Auditor | Chuyên gia đánh giá nội bộ | 3–5 |
| `QC` | FSMS QC Officer | Cán bộ QC, vệ sinh, CCP, lưu mẫu | 2–4 |
| `NV` | FSMS Employee | Nhân viên general | 50+ |

> **Cách map**: 1 `Employee` có thể có nhiều Frappe Role. Vd Trưởng BP SX kiêm Auditor kiêm BAT Member. Permission là **cộng dồn** (Frappe behaviour).

> **Role infrastructure**: tất cả roles trên là **custom role** ship qua fixtures. KHÔNG đè lên built-in role của Frappe (System Manager, Accounts Manager, Stock Manager...).

---

## 2. Permission notation (compact)

Em dùng ký hiệu rút gọn cho dễ đọc bảng. Mỗi cell là **kết hợp các quyền cấp 0** (permlevel 0):

| Ký hiệu | Ý nghĩa | Frappe permissions tương ứng |
|---------|---------|-------------------------------|
| **F** | Full | read + write + create + delete + submit + cancel + amend + print + email + report + export |
| **M** | Manage | read + write + create + submit + amend + print + email + report (no delete, no cancel) |
| **A** | Approve | read + write + submit + cancel + amend + print + email (chỉ workflow transition, không create mới) |
| **E** | Edit | read + write + create + print + email (chỉ trước submit; không submit) |
| **C** | Contribute | read + write + create (low-level, no submit, no print restricted) |
| **V** | View | read + print + email + report + export |
| **O** | ifowner | thêm flag `ifowner = 1` — chỉ thấy/sửa record do mình tạo |
| **L** | Limited (read-only with field restriction) | read + print, một số field bị ẩn qua permlevel >= 1 |
| **—** | None | không có quyền nào |

**Ngoài ra**:
- Dòng `+ifdept` = bổ sung User Permission scope theo Department (xem §5)
- `[L1]`, `[L2]` = giới hạn tới permlevel cao hơn (xem §6)

---

## 3. Permission matrix per module

### 3.1 Module `fsms_core`

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Settings` | F | E[L1] | V | V | V | V | V | V | V | V |
| `FSMS Manual` | A | M | V | E | V | V | V | V | V | V |
| `FSMS Policy` | A | M | V | V | V | V | V | V | V | V |
| `FSMS Objective` | A | M | E | E+ifdept | E+ifdept | E+ifdept | E+ifdept | V | V | V |

> `Settings` permlevel L1 dành cho field cài đặt nhạy cảm (retention years, fiscal year cycle...) — chỉ GD edit được.
> `Manual`, `Policy`: GD = Approve only (final sign-off), BAT_HEAD = soạn + soát xét + submit. NV = chỉ View.
> `Objective`: TBP có thể soạn objective cho department mình (qua User Permission); BAT_HEAD soát xét toàn bộ; GD phê duyệt cuối.

### 3.2 Module `fsms_document_control` (QT 01)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Document Register Internal` | V | M | E | M | E | E | E | V | V | V |
| `FSMS Document Register External` | V | M | E | M | E | E | E | V | V | V |
| `FSMS Records Register` | V | M | E | M | E | E | E | V | V | V |
| `FSMS Document Change Request` | A | A | E | M | C+O | C+O | C+O | E | C+O | C+O |
| `FSMS Document Category` | V | M | V | M | V | V | V | V | V | V |

> `Document Change Request`: bất kỳ ai cũng đề xuất được (C+O), nhưng chỉ thấy phiếu của mình; BAT_HEAD và BAT_MEMBER thấy hết. GD chỉ approve khi tài liệu cấp công ty (ví dụ Sổ tay).

### 3.3 Module `fsms_audit` (QT 01 đánh giá)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Audit Program` | A | M | E | V | V | V | V | E | V | V |
| `FSMS Audit Plan` | V | M | E | V+ifdept | V+ifdept | V+ifdept | V+ifdept | M | V | V |
| `FSMS Audit Checklist Template` | V | M | E | V | V | V | V | M | V | V |
| `FSMS Audit Execution` | V | M | E | V+ifdept | V+ifdept | V+ifdept | V+ifdept | M+O | V | V |
| `FSMS Audit Observation` | V | M | E | V+ifdept | V+ifdept | V+ifdept | V+ifdept | E+O | V | V |
| `FSMS Audit Summary` | V | M | E | V | V | V | V | E | V | V |

> Auditor chỉ sửa Execution / Observation **của chính mình** (ifowner). BAT_HEAD review tất cả.
> Auditee (TBP) thấy được audit khi audit Department của họ (qua User Permission +ifdept).

### 3.4 Module `fsms_ncr` (TÂM ĐIỂM)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS NCR` | A[L2] | A[L2] | E | A[L2]+ifdept | A[L2]+ifdept | A[L2]+ifdept | A[L2]+ifdept | E | E+ifdept | C+O |
| `FSMS NCR Source` | V | M | V | V | V | V | V | V | V | V |
| `FSMS NCR Action Item` | inherit from NCR parent |

> **Quy tắc NCR cốt lõi**:
> - **Mọi người** được tạo NCR (C+O cho NV) — bất kỳ ai cũng có thể đề xuất CAR.
> - **TBP của department bị ảnh hưởng** = approver chính cho phần 3 (Phê duyệt) → cần `A[L2]+ifdept`.
> - **BAT_HEAD** = approver cấp cao + có thể override TBP nếu cần (A[L2] không ifdept).
> - **GD** = chỉ approve NCR cấp công ty (Critical severity hoặc liên quan recall) — qua workflow rule riêng.
> - **Permlevel L2** dùng cho 4 field signature (`approved_signature`, `verifier_signature`...) — chỉ approver hợp lệ mới fill được, không cho người khác sửa.

### 3.5 Module `fsms_recall` (QT 02)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Recall Event` | A | M | E | E | E | V | M | V | V | V |
| `FSMS Recall Plan` | A | M | E | E | E | V | M | V | V | V |
| `FSMS Recall Report` | A | M | E | E | E | V | E | V | V | V |
| `FSMS Recall Affected Batch` | inherit from Recall Event |
| `FSMS Recall Distribution` | inherit from Recall Plan |
| `FSMS Recall Team Member` | inherit from Recall Event |

> Recall = sự kiện cấp công ty. **GD ban hành quyết định thu hồi** (per QT 02 §5.2.6) → A = Approve.
> **TBP_KD** (Sales) = tay phải trong recall (liên hệ KH, theo dõi recovery) → M.
> **TBP_SX** (Production) = tay trái (cách ly hàng thu hồi, cung cấp data về lô) → E.
> **TBP_KT** = chỉ View (theo dõi cost impact) — không edit data.

### 3.6 Module `fsms_emergency` (QT 03)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Emergency Scenario` | V | M | E | V | V | V | V | V | V | V |
| `FSMS Emergency Event` | A | M | E | E | E | V | E | V | E | C+O |
| `FSMS Emergency Drill` | V | M | E | V | E | V | V | V | E | V |
| `FSMS Fire Equipment` | V | M | E | V | E | V | V | V | E | V |
| `FSMS Fire Equipment Log` | V | V | V | V | V | V | V | V | M | C+O |
| `FSMS Disease Event Log` | V | M | E | V | V | V | V | V | M | C+O |
| `FSMS Safety Equipment Inspection` | V | M | E | V | E | V | V | V | E | V |

> NV được report sự cố khẩn cấp (C+O) — tăng cảnh báo sớm.
> QC Officer = chủ trì record-book pattern (Fire Eq Log, Disease Event Log) → M.

### 3.7 Module `fsms_verification` (QT 04)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Verification Plan` | A | M | E | V | V | V | V | V | V | V |
| `FSMS Verification Report` | V | M | E | V+ifdept | V+ifdept | V | V | E | E | V |

> Verification = trách nhiệm BAT trực tiếp. AUDITOR + QC tham gia thực hiện → E.

### 3.8 Module `fsms_context_risk` (QT 05)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Interested Party` | A | M | E | E | E | E | E | V | V | V |
| `FSMS Risk Register` | A | M | E | E+ifdept | E+ifdept | E+ifdept | E+ifdept | V | V | V |
| `FSMS Risk Score Reference` | V | M | V | V | V | V | V | V | V | V |
| `FSMS Risk Action` | inherit from Risk Register |

> Risk Register: TBP của mỗi BP có thể edit risk thuộc BP mình (+ifdept). BAT_HEAD review toàn bộ. GD approve risk Cấp 12–16.

### 3.9 Module `fsms_equipment` (QT 06)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Production Equipment` | V | V | V | V | M | V | V | V | E | V |
| `FSMS Equipment Maintenance Plan` | V | V | V | V | M | V | V | V | E | V |
| `FSMS Equipment Maintenance Log` | V | V | V | V | M | V | V | V | E | C+O |
| `FSMS Measurement Equipment` | V | E | E | V | E | V | V | V | M | V |
| `FSMS Calibration Plan` | V | M | E | V | E | V | V | V | E | V |
| `FSMS Calibration Record` | V | M | E | V | E | V | V | V | M | V |

> QT 06 chia 2: thiết bị SX = TBP_SX chủ trì (M); thiết bị đo = QC chủ trì (M, vì liên quan trực tiếp CCP).

### 3.10 Module `fsms_supplier` (QT 07)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Supplier Category` | V | M | V | M | V | V | V | V | V | V |
| `FSMS Supplier Profile` | V | M | E | E | V | V | V | V | E | V |
| `FSMS Supplier Evaluation` | V | A | E | M | E | V | V | V | E | V |
| `FSMS Approved Supplier List` | A | M | V | E | V | V | V | V | V | V |
| `FSMS Material Quality Control Plan` | V | M | E | V | E | V | V | V | E | V |
| `FSMS Material Inspection Log` | V | V | V | V | V | V | V | V | M | C+O |

> Inspection log: NV (kho) tạo phiếu khi nhập NL (C+O); QC verify (M); BAT_HEAD chỉ View (escalation lên CAR nếu reject).

### 3.11 Module `fsms_production` (QT 08)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Production Order` | V | E | E | V | M | V | V | V | E | V |
| `FSMS Production Process Monitoring` | V | E | E | V | M | V | V | V | E | C+O |
| `FSMS Finished Product Inspection` | V | E | E | V | E | V | V | V | M | V |
| `FSMS Production Nonconformity` | V | M | E | V | M | V | V | V | E | C+O |

> NV (công nhân vận hành) ghi monitoring (C+O) trong ca SX. Tổ trưởng/QC verify. Production Lead M.

### 3.12 Module `fsms_prp`

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS PRP Program` | A | M | E | V | V | V | V | V | E | V |
| `FSMS Worker Hygiene Daily` | V | V | V | V | V | V | V | V | M | V |
| `FSMS Sanitation Report` | V | E | E | V | V | V | V | V | M | V |
| `FSMS PRP Checklist Template` | V | M | E | V | V | V | V | V | E | V |
| `FSMS Cleaning Log` | V | V | V | V | E | V | V | V | M | C+O |

> Hygiene & Cleaning Log = QC daily routine → M.

### 3.13 Module `fsms_sample` (QĐ.01)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Sample Retention Policy` | A | M | E | V | V | V | V | V | E | V |
| `FSMS Sample Retention Log` | V | V | V | V | V | V | V | V | M | V |

### 3.14 Module `fsms_haccp`

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS HACCP Plan` | A | M | E | V | E | V | V | V | E | V |
| `FSMS CCP Monitoring Schedule` | V | M | E | V | E | V | V | V | E | V |
| `FSMS CCP Monitoring Log` | V | V | V | V | V | V | V | V | M | C+O |

> Workforce vận hành CCP (NV) ghi monitoring đúng ca; QC verify cuối ca; BAT_HEAD review. HACCP Plan = phê duyệt cấp GD.

### 3.15 Module `fsms_management_review` (clause 9.3)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Management Review` | A | M | E | E | V | V | V | V | V | V |

> GD chair (A); BAT_HEAD chuẩn bị nội dung (M); TBP_KH ghi biên bản (E).

### 3.16 Module `fsms_training` (clause 7.2)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Training Course` | V | M | E | M | E | E | E | E | E | V |
| `FSMS Training Plan` | A | M | E | M | V | V | V | V | V | V |
| `FSMS Training Session` | V | M | E | M | E | E | E | V | V | V |
| `FSMS Training Attendance` | inherit from Session |
| `FSMS Competency Matrix` | A | M | E | M | V | V | V | V | V | V |

### 3.17 Module `fsms_communication` (clause 7.4)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Communication Plan` | A | M | E | E | V | V | V | V | V | V |
| `FSMS Communication Log` | V | E | E | E | E+O | V | M+O | V | V | C+O |
| `FSMS Customer Complaint` | V | M | E | V | V | V | M | V | V | V |

> Sales (TBP_KD) chủ trì xử lý complaint từ KH. Communication Log: ai có liên hệ thì ghi (+O).

### 3.18 Module `fsms_traceability` (QT 09 mới)

| DocType | GD | BAT_HEAD | BAT_MEMBER | TBP_KH | TBP_SX | TBP_KT | TBP_KD | AUDITOR | QC | NV |
|---------|----|---------|-----------|--------|--------|--------|--------|---------|----|----|
| `FSMS Traceability Settings` | A | M | V | V | V | V | V | V | V | V |
| `FSMS Traceability Drill` | V | M | E | V | E | V | E | E | E | V |
| `FSMS Traceability Trace` | V | M | E | V | E | V | E | V | V | V |

> Drill = BAT_HEAD chủ trì + có sự tham gia của TBP_SX, TBP_KD, AUDITOR.

---

## 4. Cross-cutting permissions on ERPNext core DocTypes

App này **không tự đề xuất quyền mới** trên core DocTypes của ERPNext. Tuy nhiên BAT_HEAD và QC cần read-only access tới một số DocTypes core để pull data:

| Core DocType | Required role access | Mục đích |
|--------------|----------------------|----------|
| `Item` | `read` cho BAT_HEAD, QC, AUDITOR | Trace + HACCP |
| `Batch` | `read` cho TẤT CẢ FSMS roles | Trace + Recall + Sample |
| `Customer` | `read` cho BAT_HEAD, TBP_KD, QC | Recall + Complaint |
| `Supplier` | `read` cho BAT_HEAD, TBP_KH, QC | Evaluation + Inspection |
| `Employee` | `read` cho BAT_HEAD, all TBP | Signature + assignment |
| `Department` | `read` cho all FSMS roles | Filter views |
| `Asset` | `read` cho BAT_HEAD, TBP_SX, QC | Equipment link |
| `Work Order` | `read` cho BAT_HEAD, TBP_SX, QC | Production link |
| `Purchase Receipt` | `read` cho BAT_HEAD, TBP_SX, TBP_KH, QC | Material Inspection |
| `Delivery Note` | `read` cho BAT_HEAD, TBP_KD | Recall Distribution + Trace Forward |
| `Stock Ledger Entry` | `read` cho BAT_HEAD, QC | Trace |

> **Action**: tạo `Custom Permission` fixtures bổ sung quyền `read` cho các role FSMS lên các DocType core trên. KHÔNG sửa role permission gốc.

---

## 5. User Permission rules (Department-based scoping)

Frappe `User Permission` cho phép giới hạn record visible theo field link. Áp dụng:

### 5.1 Department-scoped

Tất cả TBP (TBP_KH, TBP_SX, TBP_KT, TBP_KD) chỉ thấy record có field `responsible_department` (hoặc tương đương) khớp với Department mà họ là head:

```
User: tbp_sx@hg.com
User Permission:
  - Allow: Department
  - For value: "Sản xuất"
  - Apply to all doctypes: (set on FSMS Audit Plan, FSMS Audit Execution, 
    FSMS NCR, FSMS Risk Register, FSMS Objective, FSMS Communication Log)
```

→ Khi NV thuộc BP Sản xuất tạo NCR, TBP_SX thấy. NCR của BP Kinh doanh → TBP_SX KHÔNG thấy (trừ khi link cross-department).

### 5.2 Employee-scoped (ifowner)

NV chỉ thấy record của chính mình trên các DocType có flag `ifowner = 1`:
- `FSMS Document Change Request`
- `FSMS NCR` (chỉ phần đề xuất; sau khi assign cho BP khác sẽ chuyển scope)
- `FSMS Communication Log`
- `FSMS Production Process Monitoring`
- `FSMS Cleaning Log`
- `FSMS CCP Monitoring Log`
- `FSMS Material Inspection Log`
- `FSMS Fire Equipment Log`
- `FSMS Production Nonconformity`
- `FSMS Emergency Event` (NV reporter)

### 5.3 Item / Customer / Supplier scoping

KHÔNG áp dụng — RVHG có 1 nhà máy, scope nhỏ. Nếu sau này mở rộng đa địa điểm, sẽ bổ sung.

---

## 6. Permlevel cho fields nhạy cảm

Frappe permlevel 0 = default. Permlevel >= 1 = field-level restriction.

### 6.1 Permlevel L1 — System-level config

| DocType | Field | Lý do |
|---------|-------|-------|
| `FSMS Settings` | `retention_years_default`, `fiscal_year_cycle`, `mandatory_drill_frequency_months` | Cấp độ hệ thống — chỉ GD edit |
| `FSMS Manual` | `version_no`, `effective_date` | Phải thông qua workflow phát hành |
| `FSMS Policy` | `policy_text`, `effective_date` | Tương tự Manual |

→ Cấu hình: `permlevel 1`, chỉ role `GD` có write quyền.

### 6.2 Permlevel L2 — Approval signatures

Trên `FSMS NCR`, `FSMS Recall Event`, `FSMS Recall Plan`, `FSMS Recall Report`, `FSMS Audit Execution`, `FSMS Audit Summary`, `FSMS Verification Report`, `FSMS Management Review`, `FSMS Manual`, `FSMS HACCP Plan`:

| Field | Permlevel |
|-------|-----------|
| `approved_by`, `approved_on`, `approved_signature` | L2 |
| `verifier_signature` (NCR phần 4) | L2 |
| Các signature image khác (prepared/reviewed) | L0 (auto-fill từ Employee) |

→ Cấu hình: `permlevel 2`, chỉ approver hợp lệ (BAT_HEAD hoặc GD tùy DocType) có write. Các role khác chỉ read.

→ **Hiệu quả**: tránh tình trạng người tạo phiếu tự đánh dấu mình đã được phê duyệt.

### 6.3 Permlevel L3 — Effectiveness check (post-closure)

Trên `FSMS NCR`:

| Field | Permlevel |
|-------|-----------|
| `effectiveness_check_date`, `effectiveness_check_result` | L3 |

→ Cấu hình: chỉ BAT_HEAD và AUDITOR có write. Mục đích: sau khi NCR đã đóng, AUDITOR / BAT_HEAD ghi vào sau N ngày verify hiệu lực CAR (clause 10.2). Người thực hiện NCR (assigned_to) không sửa được phần này.

---

## 7. ifowner rules table

DocTypes áp dụng `ifowner = 1` cho role NV (nhân viên general):

| DocType | Role bị giới hạn ifowner | Mục đích |
|---------|--------------------------|----------|
| `FSMS Document Change Request` | NV | NV chỉ thấy phiếu sửa đổi của mình |
| `FSMS NCR` | NV | NV chỉ thấy NCR mình đề xuất (sau khi submit, BAT_HEAD assign sang BP khác → vẫn theo dõi được qua field `requestor`) |
| `FSMS Audit Execution`, `FSMS Audit Observation` | AUDITOR | Auditor sửa được audit của mình |
| `FSMS Production Process Monitoring` | NV | NV ca SX chỉ thấy ca của mình |
| `FSMS CCP Monitoring Log` | NV | Tương tự |
| `FSMS Cleaning Log` | NV | Tương tự |
| `FSMS Material Inspection Log` | NV | NV kho chỉ thấy phiếu của mình |
| `FSMS Fire Equipment Log` | NV | NV PCCC chỉ thấy log của mình |
| `FSMS Communication Log` | NV, TBP_SX | Chỉ thấy log do mình ghi |
| `FSMS Emergency Event` | NV | NV reporter chỉ thấy event của mình |
| `FSMS Production Nonconformity` | NV | Tương tự |

> **Note**: ifowner áp dụng ở cấp Permission, KHÔNG ở cấp DocType. Cùng một DocType, role khác (BAT_HEAD, TBP) vẫn thấy hết.

---

## 8. Submit / Cancel / Amend matrix

DocType `is_submittable = 1` cần phân quyền cụ thể cho 3 hành động này:

| DocType | Submit role | Cancel role | Amend role |
|---------|-------------|-------------|------------|
| `FSMS Manual` | BAT_HEAD | GD only | GD only |
| `FSMS Policy` | BAT_HEAD | GD only | GD only |
| `FSMS Objective` | BAT_HEAD | GD, BAT_HEAD | BAT_HEAD |
| `FSMS Document Change Request` | requestor (any role with create) | BAT_HEAD | BAT_HEAD |
| `FSMS Audit Plan` | BAT_HEAD | BAT_HEAD | BAT_HEAD |
| `FSMS Audit Execution` | AUDITOR (owner) | BAT_HEAD | AUDITOR |
| `FSMS NCR` | requestor (any role) | BAT_HEAD | BAT_HEAD |
| `FSMS Recall Event` | BAT_HEAD | GD only | GD only |
| `FSMS Recall Plan` | BAT_HEAD | GD only | BAT_HEAD |
| `FSMS Recall Report` | BAT_HEAD | GD only | GD only |
| `FSMS Verification Plan` | BAT_HEAD | BAT_HEAD | BAT_HEAD |
| `FSMS Verification Report` | BAT_HEAD | BAT_HEAD | BAT_HEAD |
| `FSMS Risk Register` | BAT_HEAD or TBP+ifdept | BAT_HEAD | BAT_HEAD |
| `FSMS Calibration Record` | QC | BAT_HEAD | QC |
| `FSMS Supplier Evaluation` | TBP_KH | BAT_HEAD | BAT_HEAD |
| `FSMS Material Inspection Log` | NV (kho) | TBP_KH | TBP_KH |
| `FSMS HACCP Plan` | BAT_HEAD | GD only | GD only |
| `FSMS CCP Monitoring Log` | NV (operator) | BAT_HEAD | QC |
| `FSMS Management Review` | BAT_HEAD | GD only | GD only |
| `FSMS Training Plan` | TBP_KH | BAT_HEAD | TBP_KH |
| `FSMS Customer Complaint` | TBP_KD | BAT_HEAD | TBP_KD |
| `FSMS Traceability Drill` | BAT_HEAD | BAT_HEAD | BAT_HEAD |
| `FSMS Traceability Trace` | BAT_HEAD | BAT_HEAD | BAT_HEAD |

> **Quy tắc chung**: GD = "kill switch" cho các tài liệu cấp công ty (Manual, Policy, HACCP Plan, Recall, Management Review). BAT_HEAD = vận hành thường ngày.

---

## 9. Special cases

### 9.1 Auto-create chains (server-side)

Khi NCR được auto-create từ Audit Finding / CCP fail / Customer Complaint... thì record được tạo bằng `frappe.flags.ignore_permissions = True` trong server hook. Nhưng visibility của NCR mới sẽ tuân theo quy tắc thường:
- Owner = User trigger (auditor / operator / sales)
- Department = Department của source

→ Cấu hình hooks chú ý set đúng `owner` và `responsible_department` để ifowner và User Permission hoạt động đúng.

### 9.2 Document state transitions and approver elevation

Khi NCR ở state `Chờ phê duyệt`, người approve hợp lệ là:
1. TBP của Department bị ảnh hưởng (`affected_department`), HOẶC
2. BAT_HEAD (override quyền)

Frappe Workflow engine không có "OR" logic native. Giải pháp:
- Workflow state `Chờ phê duyệt` cho phép action `Phê duyệt` từ role `BAT_HEAD` HOẶC role `Department Head` (custom role tự sinh per Department)
- Mỗi TBP được gán role tương ứng (vd `Production Department Head` → TBP_SX)
- Approval action validate trong server: `if user_dept != ncr.affected_department and not user_has_role("BAT_HEAD"): raise PermissionError`

→ Note ở `04_workflow_blueprint.md`.

### 9.3 Anonymous reporting (không áp dụng MVP)

Một số FSMS chuẩn cho phép NV report anonymous. RVHG không yêu cầu (tất cả qua named user). Để mở rộng sau này:
- Tạo role `FSMS Anonymous Reporter`
- DocType `FSMS Anonymous Report` với only-create permission
- BAT_HEAD review và escalate sang NCR thực

→ KHÔNG implement phase 1.

### 9.4 Print Format permissions

Print Format follow read permission của parent DocType. Không cần config riêng.

---

## 10. Implementation summary

| # | Item | Action | File output |
|---|------|--------|-------------|
| 10.1 | 10 custom roles | Tạo qua fixtures | `fixtures/role.json` |
| 10.2 | Per-DocType permissions (10 roles × 47 DocTypes ≈ 470 entries) | Tạo qua DocType JSON `permissions` array | trong từng DocType JSON |
| 10.3 | Custom permissions trên ERPNext core DocTypes | `Custom Permission` fixture | `fixtures/custom_permission.json` |
| 10.4 | User Permission templates | Sample seed cho admin tham khảo | `fixtures/user_permission_template.json` |
| 10.5 | Permlevel L1, L2, L3 trên các field nhạy cảm | Set trong field definition của DocType JSON | trong DocType JSON |
| 10.6 | Workflow approval logic (§9.2) | Server hook + custom role per Department | `hooks.py` + `fixtures/role.json` |

---

## 11. Trạng thái + bước tiếp theo

- **Đã hoàn thành**: 00 inventory + 01 business model + 02 doctype blueprint + **03 permission matrix** + QT 09 full text
- **Đang chờ**: anh review file này, đặc biệt:
  - Quyết định ai approve NCR ở phần 3 (cấu trúc §3.4 + §9.2): TBP của BP bị ảnh hưởng, có override bởi BAT_HEAD?
  - GD có cần role-level access cấp record-by-record (tức xem được từng NCR), hay chỉ qua report dashboard?
  - Permlevel L3 cho effectiveness check — anh thấy cần thiết không?
- **Sau khi duyệt 03**: Em sang `04_workflow_blueprint.md` — state machine chi tiết cho mọi DocType có workflow (đặc biệt là NCR 7-state, Recall 6-state, Audit 5-state, Document Change Request 5-state).

---

**End of `03_permission_matrix.md` — chờ anh review.**
