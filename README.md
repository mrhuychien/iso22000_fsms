# ISO 22000 FSMS

Hệ thống quản lý an toàn thực phẩm (Food Safety Management System) cho ERPNext v16, triển khai dạng Frappe custom app, tuân thủ **ISO 22000:2018** + **HACCP** (Codex) + **ISO/TS 22002-1**.

## 1. Tổng quan

| Hạng mục | Số lượng |
|---|---|
| Module Frappe | 18 |
| DocType (business + child + master + single) | 123 |
| Workflow | 28 (NCR 7 trạng thái — focal flow) |
| Print Format (BM giống Word RVHG) | 38 |
| Notification + Email Template | 24 |
| Custom Field bổ sung lên ERPNext core | 6 |
| Custom Permission read-only trên core | 48 |
| Master data fixture | 47 records |
| Test (FrappeTestCase) | 5 module |

Toàn bộ thiết kế nằm ở `docs/design/00…06`. Implementation tham chiếu trực tiếp blueprint từng phần — không đoán.

## 2. Module map (per `iso22000_fsms/modules.txt`)

| # | Module | Phạm vi |
|---|--------|---------|
| 1 | `fsms_core` | Settings, Manual, Policy, Objective |
| 2 | `fsms_document_control` | QT 01 — Doc + Records control |
| 3 | `fsms_audit` | QT 01 — Internal Audit (Program/Plan/Execution/Summary) |
| 4 | `fsms_ncr` | QT 01 — NCR / CAR (TÂM ĐIỂM, 7 trạng thái workflow) |
| 5 | `fsms_recall` | QT 02 — Recall Event/Plan/Report |
| 6 | `fsms_emergency` | QT 03 — Sự cố khẩn cấp + diễn tập |
| 7 | `fsms_verification` | QT 04 — Tham tra |
| 8 | `fsms_context_risk` | QT 05 — Bên quan tâm + Risk Register |
| 9 | `fsms_equipment` | QT 06 — Thiết bị SX + thiết bị đo |
| 10 | `fsms_supplier` | QT 07 — Đánh giá NCC + KSCL vật tư |
| 11 | `fsms_production` | QT 08 — Lệnh SX + giám sát + KCS |
| 12 | `fsms_prp` | PRP — vệ sinh CN, vệ sinh khu vực |
| 13 | `fsms_sample` | QĐ.01 — Sổ lưu mẫu |
| 14 | `fsms_haccp` | KH.HACCP — Plan + CCP/OPRP + Monitoring |
| 15 | `fsms_management_review` | Họp xem xét lãnh đạo (clause 9.3) |
| 16 | `fsms_training` | Đào tạo + Competency Matrix (clause 7.2) |
| 17 | `fsms_communication` | Truyền thông + Customer Complaint (clause 7.4) |
| 18 | `fsms_traceability` | QT 09 — Truy xuất nguồn gốc (clause 8.3) |

## 3. Cài đặt

### Yêu cầu
- Frappe v16
- ERPNext v16
- MariaDB 10.6+, Python 3.10+, Node 18+

### Bench commands

```bash
# Trong thư mục frappe-bench
bench get-app https://github.com/mrhuychien/iso22000_fsms
bench --site rvhg.local install-app iso22000_fsms

# Run patches (idempotent)
bench --site rvhg.local migrate

# Build assets
bench build --app iso22000_fsms
bench restart
```

Sau install, mở **Bảng điều khiển ATTP** từ menu chính.

### Setup thủ công sau install

1. Vào `FSMS Settings` (Single) → nhập tên công ty, MST, scope.
2. Mở `User List` → gán role `FSMS Manager` / `FSMS Director` / 4 role TBP cho user phù hợp.
3. Mở `Department` → đảm bảo phòng ban có Employee Head (cho phân quyền NCR).
4. Tạo `FSMS Manual` v1.0 + `FSMS Policy` v1.0, gán signature image cho mỗi Employee.
5. Chạy patch `bootstrap_fsms_settings` (tự chạy khi `bench migrate`).

## 4. Tài liệu hệ thống

| File | Nội dung |
|---|---|
| `docs/design/00_document_inventory.md` | Map 52 file hồ sơ → tier |
| `docs/design/01_business_model.md` | Actors + 18 use cases + decisions |
| `docs/design/02_doctype_blueprint.md` | 47 doctype + 28 child — full schema |
| `docs/design/03_permission_matrix.md` | Role × DocType × permlevel × ifowner |
| `docs/design/04_workflow_blueprint.md` | 28 state machines + cross-cutting rules |
| `docs/design/05_integration_plan.md` | Hooks + scheduled tasks + dashboard + fast-track |
| `docs/design/06_fixtures_plan.md` | Fixtures specification (~205 records) |
| `docs/design/QT 09 ...docx` | Quy trình truy xuất nguồn gốc (mới) |

## 5. Workflow quan trọng

### NCR (focal — 7 trạng thái)
```
Đề xuất → Phân tích → Chờ phê duyệt → Đang thực hiện
                                           → Đang xác minh → Đã đóng
                                                          → Chuyển tiếp (auto-tạo NCR mới)
```

### Recall Event (6 trạng thái)
```
Phát sinh → Lập kế hoạch → Đang thu hồi → Bảo quản → Báo cáo → Đóng
```

### HACCP Plan (Publish lifecycle)
```
Draft → Reviewed → Approved → Published → Under Revision → Obsolete
```

## 6. Auto-create chain (server hooks)

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

## 7. Tests

```bash
bench --site rvhg.local set-config allow_tests true
bench --site rvhg.local run-tests --app iso22000_fsms
```

Test modules:
- `tests/test_ncr_workflow.py` — NCR validation + signature auto-fill
- `tests/test_recall_fast_track.py` — recall_level auto-suggest, recovery rate
- `tests/test_traceability.py` — drill outcome derivation
- `tests/test_haccp_ccp_breach.py` — hazard risk + decision tree → CCP/OPRP
- `tests/test_audit_to_ncr_chain.py` — Audit Finding → NCR auto-create

## 8. Cấu trúc folder

```
iso22000_fsms/
├── docs/design/             # Blueprint + thiết kế
├── iso22000_fsms/
│   ├── hooks.py             # Wire toàn bộ doc_events / scheduler / fixtures
│   ├── modules.txt          # 18 modules
│   ├── api.py               # Cross-module REST endpoints
│   ├── boot.py              # extend_bootinfo
│   ├── install.py           # after_install / before_uninstall
│   ├── utils.py             # Jinja helpers (format_vnd, format_vn_date, signature_or_blank)
│   ├── workflow_validation.py  # OR-logic approval router
│   ├── fixtures/            # 19 JSON fixture files (255 records)
│   ├── templates/notifications/  # 12 email HTML templates
│   ├── public/css/fsms.css  # Print Format styling (.fsms- prefix)
│   ├── public/js/fsms_client.js  # Workflow tag helper, signature lookup
│   ├── translations/vi.csv  # Vietnamese DocType labels
│   ├── config/              # desktop.py + docs.py
│   ├── patches/v1_0_0/      # bootstrap_fsms_settings + seed_default_pdf_settings
│   ├── tests/               # 5 FrappeTestCase modules
│   └── fsms_*/              # 18 module folders
└── README.md (file này)
```

## 9. License

MIT — xem `LICENSE.txt`

## 10. Liên hệ

- Maintainer: Công ty CP Hoàng Giang
- Email: hoanggiavn.vn@gmail.com
