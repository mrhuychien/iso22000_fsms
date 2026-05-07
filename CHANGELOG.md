# Changelog

Tất cả thay đổi đáng kể của `iso22000_fsms` được ghi lại tại đây.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/),
phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

## [1.0.0] — 2026-05-07

Phát hành đầu tiên — đầy đủ 18 module FSMS theo design `02_doctype_blueprint.md`.

### Added

- **18 module Frappe** với 123 DocType (47 business + 17 master + 8 single + 28 child + helper children).
- **fsms_core**: FSMS Settings, FSMS Manual, FSMS Policy, FSMS Objective + 3 child tables.
- **fsms_ncr** (focal): FSMS NCR với workflow 7 trạng thái (Đề xuất → ... → Đã đóng | Chuyển tiếp).
- **fsms_recall**: Recall Event/Plan/Report với auto-suggest level, recovery rate calc.
- **fsms_haccp**: HACCP Plan, CCP/OPRP children, Decision Tree, CCP Monitoring Log với auto-NCR khi vượt giới hạn.
- **fsms_audit**: Program/Plan/Execution/Observation/Summary, auto-create NCR từ findings NC Major/Minor.
- **fsms_supplier**: Supplier Profile, Evaluation (weighted score → grade A/B/C/D), Material Inspection Log.
- **fsms_equipment**: Production Equipment, Maintenance Plan/Log, Measurement Equipment, Calibration Plan/Record.
- **fsms_traceability**: QT 09 — Trace + Drill với time-taken + outcome derivation, backward/forward link materialization.
- **fsms_context_risk**: Risk Register với A+B+C+D scoring, level mapping ≤9/10–11/≥12.
- **fsms_communication**: Customer Complaint với severity-based recall auto-flag.
- **+ 7 module phụ trợ** (document_control, emergency, verification, production, prp, sample, training, management_review).

### Fixtures (255 records)

- 14 Role (10 FSMS + 4 Department Head cho OR-logic approval).
- 6 Custom Field, 4 Property Setter, 48 Custom DocPerm.
- 33 Workflow State, 39 Workflow Action Master, 28 Workflow.
- 12 Notification + 12 Email Template.
- 38 Print Format (giống Word RVHG).
- 6 Dashboard Chart, 4 Number Card, 1 Dashboard, 1 Workspace.
- 47 master records (Document Category, NCR Source, Risk Score Reference, Supplier Category, Emergency Scenario, PRP Item Template).

### Hooks + scheduled

- `doc_events`: 16 DocType có hooks (validate / before_save / on_submit / on_update_after_submit / on_cancel).
- `scheduler_events`: daily (4 task), weekly (3 task), monthly (3 task), cron (1 yearly).
- `extend_bootinfo`: pass FSMS settings to client.
- `permission_query_conditions` + `has_permission` cho FSMS NCR + FSMS Risk Register.
- `override_whitelisted_methods`: wrap `apply_workflow` với OR-logic validator.

### Auto-create chain

- Audit Finding (NC Major/Minor) → NCR auto-create với severity mapping.
- CCP Out-of-Limit → NCR (severity Critical) auto-create.
- Customer Complaint Cấp 1/2 → Recall Event auto-suggest + NCR.
- Material Inspection Reject → NCR auto-create.
- Calibration Fail → NCR auto-create + Equipment status update.
- Recall Event submit → Traceability Trace auto-create.

### Templates + assets

- `templates/notifications/*.html` — 12 Jinja partials cho Notification.
- `public/css/fsms.css` — Print Format styling với prefix `.fsms-` (tránh xung đột Bootstrap).
- `public/js/fsms_client.js` — workflow tag helper, signature lookup, confirm dialog.
- `translations/vi.csv` — nhãn tiếng Việt cho DocType + workflow action.

### Config + lifecycle

- `config/desktop.py` + `config/docs.py`.
- `install.py` — `after_install` tạo FSMS Settings record + banner.
- `patches/v1_0_0/bootstrap_fsms_settings.py` — idempotent default values.
- `patches/v1_0_0/seed_default_pdf_settings.py` — A4 + 12pt cho Print Format.
- `utils.py` — Jinja helpers (`format_vnd`, `format_vn_date`, `signature_or_blank`).

### Tests (5 modules)

- `test_ncr_workflow.py` — validation + signature auto-fill + close blocked when verification fails.
- `test_recall_fast_track.py` — recall_level auto-suggest + recovery rate + over-recovery validation.
- `test_traceability.py` — drill outcome derivation (4 cases).
- `test_haccp_ccp_breach.py` — risk_level + decision tree → CCP/OPRP flags.
- `test_audit_to_ncr_chain.py` — Audit Finding → NCR auto-create với severity mapping.

### Documentation

- `README.md` cập nhật full với install guide + module map + workflow + auto-create chain.
- `docs/design/00…06` — 4640 lines blueprint (đã có sẵn từ phase design).
- `CHANGELOG.md` (file này).
