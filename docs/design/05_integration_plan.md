# 05 — Integration Plan

> **App**: `iso22000_fsms` · Frappe v16 · ERPNext v16
> **Trạng thái**: Draft v0.1 — chờ review trước khi sang `06_fixtures_plan.md`
> **Phụ thuộc**: 01–04 đã được duyệt
> **Phase 2 deferred**: Telegram Bot, Zalo OA notification — không trong phase 1

---

## 0. Mục tiêu file này

Quy định **TẤT CẢ** integration points giữa `iso22000_fsms` và phần còn lại của hệ thống — đủ chi tiết để `nextcode-build` viết code không cần phải đoán:

1. ERPNext core DocType — link references và sync rules
2. `hooks.py` outline đầy đủ
3. Per-DocType server events (validate / on_update / on_submit / on_cancel / on_trash / before_workflow_transition)
4. Scheduled jobs
5. Whitelisted REST API methods
6. Custom Reports
7. **GD Dashboard** thiết kế cụ thể
8. Email Notification templates
9. **Recall fast-track mode** (per anh chốt)
10. ERPNext version requirements

---

## 1. ERPNext core DocType integration

### 1.1 Hard dependency table

| ERPNext Core | Required for | Direction | Sync rules |
|---|---|---|---|
| `Item` | HACCP Plan (1 plan / 1 item line), Recall Affected Batch, Production Order, Sample Retention, Material Inspection | Read by FSMS; **FSMS extends Item via Custom Field** `haccp_plan_link` (Link → FSMS HACCP Plan) | When HACCP Plan publishes → auto-update Item.haccp_plan_link |
| `Batch` | Recall Affected Batch, CCP Monitoring, Sample Retention, Production Order, Traceability | Read-only by FSMS | None |
| `Customer` | Recall Distribution, Customer Complaint, Communication Log, Trace Forward | Read-only | None |
| `Supplier` | Supplier Profile (1-1), Evaluation, Inspection, Trace Backward | Read-only; FSMS extends via separate DocType `FSMS Supplier Profile` (link 1-1, NO custom field on Supplier) | Supplier Profile auto-create on first Evaluation |
| `Employee` | Signature, ownership, assignment, training | Read; FSMS extends Employee via Custom Field `fsms_competency_status` (Select: Đủ / Thiếu / Đang đào tạo) | Updated by FSMS Training Session on_submit |
| `Department` | Permission scoping, ownership | Read-only | None |
| `Designation` | Competency Matrix link | Read-only | None |
| `Asset` | Production Equipment + Measurement Equipment (1-1) | Read; FSMS Equipment is separate DocType linking Asset | Asset.asset_status mirror to FSMS Equipment.status via on_update |
| `Work Order` | Production Order (1-1) | Read; FSMS Production Order links Work Order | When Work Order completes → auto-create FSMS Finished Product Inspection |
| `Purchase Receipt` | Material Inspection Log (1-N) | Read | When PR submitted → auto-create draft Material Inspection Log if Item.requires_inspection |
| `Delivery Note` | Recall Distribution, Trace Forward | Read | None |
| `Stock Ledger Entry` | Trace queries | Read-only | None |
| `Quality Inspection` | (NOT used directly — FSMS Material Inspection Log is preferred to allow Vietnamese fields) | — | — |
| `Quality Procedure`, `Quality Action`, `Quality Goal`, `Quality Meeting`, `Quality Review` | (NOT extended — FSMS uses parallel DocTypes; rationale §1.3) | — | — |

### 1.2 Custom Fields lên ERPNext core (ship qua fixtures)

```python
# fixtures/custom_field.json (extract)
[
  {
    "doctype": "Custom Field",
    "dt": "Item",
    "fieldname": "haccp_plan_link",
    "label": "HACCP Plan",
    "fieldtype": "Link",
    "options": "FSMS HACCP Plan",
    "insert_after": "is_stock_item",
    "read_only": 1,
    "description": "Auto-set khi HACCP Plan được publish"
  },
  {
    "doctype": "Custom Field",
    "dt": "Item",
    "fieldname": "requires_inspection",
    "label": "Yêu cầu kiểm tra đầu vào (FSMS)",
    "fieldtype": "Check",
    "insert_after": "haccp_plan_link"
  },
  {
    "doctype": "Custom Field",
    "dt": "Employee",
    "fieldname": "fsms_competency_status",
    "label": "Tình trạng năng lực FSMS",
    "fieldtype": "Select",
    "options": "Đủ\nThiếu\nĐang đào tạo",
    "insert_after": "department",
    "read_only": 1
  },
  {
    "doctype": "Custom Field",
    "dt": "Employee",
    "fieldname": "fsms_signature_image",
    "label": "Chữ ký số FSMS",
    "fieldtype": "Attach Image",
    "insert_after": "fsms_competency_status"
  },
  {
    "doctype": "Custom Field",
    "dt": "Batch",
    "fieldname": "fsms_recall_status",
    "label": "Tình trạng thu hồi FSMS",
    "fieldtype": "Select",
    "options": "\nĐang thu hồi\nĐã thu hồi\nKhông áp dụng",
    "insert_after": "expiry_date",
    "read_only": 1
  },
  {
    "doctype": "Custom Field",
    "dt": "Supplier",
    "fieldname": "fsms_approved",
    "label": "Đã phê duyệt FSMS (NCU-PD)",
    "fieldtype": "Check",
    "insert_after": "supplier_group",
    "read_only": 1
  }
]
```

→ Tổng số Custom Field trên ERPNext core: **~6 fields** (cố tình giữ tối thiểu để không ảnh hưởng upgrade).

### 1.3 Tại sao KHÔNG extend Quality Procedure / Quality Meeting / Quality Action?

Anh đã hỏi câu này trong vòng đầu — em xác nhận quyết định:

1. **Quality Procedure** schema đơn giản, chỉ phù hợp ISO 9001 chung; thiếu nhiều field FSMS cần (HACCP linkage, retention, owner department, change history). Extend sẽ cần custom fields nhiều hơn là tạo mới.
2. **Quality Meeting** không có concept "Inputs/Outputs theo clause 9.3.2/9.3.3" của ISO 22000.
3. **Quality Action** workflow đơn giản (Open/Closed) — không phù hợp 7-state NCR của ta.
4. Tách biệt giúp upgrade Frappe/ERPNext smooth — không bị schema conflict.
5. Trade-off: data 2 nơi cho cùng concept "quality" nếu khách hàng đang dùng. Với RVHG mới triển khai, không có data legacy → không vấn đề.

---

## 2. `hooks.py` outline đầy đủ

```python
# iso22000_fsms/hooks.py

from . import __version__ as app_version

app_name = "iso22000_fsms"
app_title = "ISO 22000 FSMS"
app_publisher = "Công ty CP Hoàng Giang"
app_description = "Hệ thống quản lý ATTP theo ISO 22000:2018"
app_email = "hoanggiavn.vn@gmail.com"
app_license = "MIT"  # hoặc GPL v3 nếu anh chọn license khác

# ============================================================================
# Document Events — server hooks per DocType
# ============================================================================
doc_events = {
    # NCR (centerpiece)
    "FSMS NCR": {
        "validate": "iso22000_fsms.fsms_ncr.api.validate_ncr",
        "before_save": "iso22000_fsms.fsms_ncr.api.set_signatures",
        "on_submit": "iso22000_fsms.fsms_ncr.api.notify_assignees",
        "on_update_after_submit": "iso22000_fsms.fsms_ncr.api.handle_state_changes",
        "on_cancel": "iso22000_fsms.fsms_ncr.api.audit_cancellation",
    },
    
    # Audit chain
    "FSMS Audit Execution": {
        "on_submit": "iso22000_fsms.fsms_audit.api.create_ncr_from_findings",
    },
    "FSMS Audit Finding": {
        "validate": "iso22000_fsms.fsms_audit.api.validate_finding",
    },
    
    # Recall chain
    "FSMS Recall Event": {
        "on_update_after_submit": "iso22000_fsms.fsms_recall.api.handle_recall_state_change",
        "on_submit": "iso22000_fsms.fsms_recall.api.create_traceability_trace",
    },
    "FSMS Customer Complaint": {
        "on_submit": "iso22000_fsms.fsms_communication.api.handle_complaint",
    },
    
    # CCP / Production / Material monitoring → NCR
    "FSMS CCP Monitoring Log": {
        "validate": "iso22000_fsms.fsms_haccp.api.check_ccp_limits",
        "on_submit": "iso22000_fsms.fsms_haccp.api.escalate_if_breach",
    },
    "FSMS Material Inspection Log": {
        "on_submit": "iso22000_fsms.fsms_supplier.api.escalate_rejected_material",
    },
    "FSMS Calibration Record": {
        "on_submit": "iso22000_fsms.fsms_equipment.api.escalate_failed_calibration",
    },
    
    # Master document publishing → update registers
    "FSMS HACCP Plan": {
        "on_update_after_submit": "iso22000_fsms.fsms_haccp.api.sync_to_item_on_publish",
    },
    "FSMS Document Change Request": {
        "on_update_after_submit": "iso22000_fsms.fsms_document_control.api.publish_document",
    },
    "FSMS Supplier Evaluation": {
        "on_submit": "iso22000_fsms.fsms_supplier.api.update_supplier_profile",
    },
    "FSMS Training Session": {
        "on_submit": "iso22000_fsms.fsms_training.api.update_employee_competency",
    },
    
    # ERPNext core hooks (cross-app integration)
    "Work Order": {
        "on_submit": "iso22000_fsms.fsms_production.api.create_production_order_link",
    },
    "Purchase Receipt": {
        "on_submit": "iso22000_fsms.fsms_supplier.api.auto_create_inspection_log",
    },
    "Batch": {
        "after_insert": "iso22000_fsms.fsms_traceability.api.register_batch",
    },
    "Item": {
        "before_save": "iso22000_fsms.fsms_haccp.api.sync_haccp_plan_link",
    },
}

# ============================================================================
# Scheduled tasks
# ============================================================================
scheduler_events = {
    "daily": [
        "iso22000_fsms.fsms_ncr.tasks.check_overdue_ncr",
        "iso22000_fsms.fsms_equipment.tasks.check_calibration_due",
        "iso22000_fsms.fsms_sample.tasks.check_disposal_due",
        "iso22000_fsms.fsms_emergency.tasks.check_inspection_due",
    ],
    "weekly": [
        "iso22000_fsms.fsms_document_control.tasks.check_document_review_due",
        "iso22000_fsms.fsms_audit.tasks.audit_plan_kickoff_reminder",
        "iso22000_fsms.fsms_training.tasks.training_compliance_digest",
    ],
    "monthly": [
        "iso22000_fsms.fsms_context_risk.tasks.risk_review_reminder",
        "iso22000_fsms.fsms_haccp.tasks.haccp_plan_annual_review_check",
        "iso22000_fsms.fsms_traceability.tasks.drill_due_check",
    ],
    "cron": {
        # Yearly: Audit Program preparation reminder (Dec 1)
        "0 8 1 12 *": ["iso22000_fsms.fsms_audit.tasks.year_end_audit_reminder"],
    }
}

# ============================================================================
# Workflow validation (cross-cutting OR-logic approval)
# ============================================================================
override_whitelisted_methods = {
    "frappe.model.workflow.apply_workflow": "iso22000_fsms.workflow_validation.apply_workflow_with_validation",
}

# ============================================================================
# Boot session — pass FSMS settings to client side
# ============================================================================
extend_bootinfo = ["iso22000_fsms.boot.boot_fsms_session"]

# ============================================================================
# Fixtures (loaded on app install)
# ============================================================================
fixtures = [
    "Role",
    "Custom Field",
    "Custom Permission",
    {"doctype": "Workflow State"},
    {"doctype": "Workflow"},
    {"doctype": "Workflow Action Master"},
    {"doctype": "Notification"},
    {"doctype": "Email Template"},
    {"doctype": "Print Format", "filters": [["module", "=", "ISO 22000 FSMS"]]},
    {"doctype": "FSMS Document Category"},
    {"doctype": "FSMS NCR Source"},
    {"doctype": "FSMS Risk Score Reference"},
    {"doctype": "FSMS Supplier Category"},
    {"doctype": "FSMS Emergency Scenario"},
    {"doctype": "FSMS PRP Item", "filters": [["is_template", "=", 1]]},
]

# ============================================================================
# Permissions — global query conditions for User Permission
# ============================================================================
permission_query_conditions = {
    "FSMS NCR": "iso22000_fsms.fsms_ncr.permissions.get_query_conditions",
    "FSMS Risk Register": "iso22000_fsms.fsms_context_risk.permissions.get_query_conditions",
}

has_permission = {
    "FSMS NCR": "iso22000_fsms.fsms_ncr.permissions.has_permission",
}
```

---

## 3. Server hooks chi tiết per DocType

### 3.1 NCR — `fsms_ncr/api.py`

```python
# Critical functions; not all listed — sample showing pattern

def validate_ncr(doc, method=None):
    # Severity validation
    if doc.severity == "Critical" and not doc.evidence_attachment:
        frappe.throw("NCR severity Critical phải có evidence attachment")
    
    # Recompute action items count
    doc.total_actions = len(doc.action_items or [])
    doc.completed_actions = len([a for a in doc.action_items if a.status == "Hoàn thành"])

def set_signatures(doc, method=None):
    # Auto-pull signature from Employee record
    if doc.requestor and not doc.requestor_signature:
        emp = frappe.get_doc("Employee", doc.requestor)
        doc.requestor_signature = emp.fsms_signature_image
    
    if doc.analyzer and not doc.analyzer_signature:
        emp = frappe.get_doc("Employee", doc.analyzer)
        doc.analyzer_signature = emp.fsms_signature_image
    
    # ... approver, verifier signatures similar

def handle_state_changes(doc, method=None):
    """Called on_update_after_submit; route based on workflow_state"""
    if doc.workflow_state == "Chuyển tiếp" and not doc.reissued_to_ncr:
        new = create_reissued_ncr(doc)
        doc.db_set("reissued_to_ncr", new.name)
    
    if doc.workflow_state == "Đã đóng":
        # Schedule effectiveness check after 30 days (configurable)
        schedule_effectiveness_check(doc)

def create_reissued_ncr(old_doc):
    new = frappe.copy_doc(old_doc)
    new.workflow_state = "Đề xuất"
    new.docstatus = 0
    new.reissued_from_ncr = old_doc.name
    new.nonconformity_description = (
        f"Tiếp nối phiếu {old_doc.name} (verify không đạt). "
        f"Lý do: {old_doc.verification_remarks}"
    )
    # Reset all phase 2/3/4 fields
    for f in ["root_cause_analysis", "proposed_action", "approved_by", 
              "approved_on", "approved_signature", "verifier", 
              "verifier_signature", "verification_outcome"]:
        new.set(f, None)
    new.insert(ignore_permissions=True)
    return new

def notify_assignees(doc, method=None):
    """Email + in-app on submit"""
    if doc.workflow_state == "Chờ phê duyệt":
        approvers = get_approvers(doc)  # TBP_dept + BAT_HEAD
        send_notification(doc, approvers, template="ncr_pending_approval")
```

### 3.2 Audit Execution → NCR auto-create

```python
# fsms_audit/api.py

def create_ncr_from_findings(doc, method=None):
    """Called on Audit Execution submit"""
    if not doc.auto_create_ncr:
        return
    
    for finding in doc.findings:
        if finding.finding_type in ["NC Major", "NC Minor"]:
            ncr = frappe.get_doc({
                "doctype": "FSMS NCR",
                "ncr_source": "Audit",
                "source_reference_doctype": "FSMS Audit Execution",
                "source_reference_name": doc.name,
                "severity": "Major" if finding.finding_type == "NC Major" else "Minor",
                "ncr_type": "Khắc phục",
                "nonconformity_description": finding.finding_description,
                "evidence_attachment": doc.auditor_signature,  # link to audit doc
                "affected_department": finding.responsible_department,
                "requestor": doc.auditor,
                "ncr_date": today(),
                "workflow_state": "Đề xuất",
            })
            ncr.flags.ignore_permissions = True
            ncr.insert()
            finding.db_set("linked_ncr", ncr.name)
            
            # Notify auditee TBP
            send_notification(ncr, [finding.responsible_department + " head"], 
                              template="ncr_from_audit")
```

### 3.3 CCP Monitoring breach → NCR

```python
# fsms_haccp/api.py

def check_ccp_limits(doc, method=None):
    """validate hook — compute is_within_limit"""
    ccp = frappe.get_doc("FSMS HACCP CCP", doc.ccp)
    # Parse critical_limit and compare measurement_value
    is_within = parse_and_compare(doc.measurement_value, ccp.critical_limit)
    doc.is_within_limit = is_within

def escalate_if_breach(doc, method=None):
    """on_submit hook"""
    if doc.is_within_limit:
        return
    
    # Determine severity from CCP definition
    ccp = frappe.get_doc("FSMS HACCP CCP", doc.ccp)
    severity = "Critical" if ccp.is_critical_health_risk else "Major"
    
    ncr = frappe.get_doc({
        "doctype": "FSMS NCR",
        "ncr_source": "CCP Fail",
        "source_reference_doctype": "FSMS CCP Monitoring Log",
        "source_reference_name": doc.name,
        "severity": severity,
        "ncr_type": "Khắc phục",
        "nonconformity_description": (
            f"CCP {ccp.ccp_no} vượt giới hạn tới hạn. "
            f"Giá trị đo: {doc.measurement_value} {doc.measurement_unit}. "
            f"Giới hạn: {ccp.critical_limit}"
        ),
        "affected_department": "Sản xuất",
        "requestor": doc.monitor,
        "workflow_state": "Đề xuất",
    })
    ncr.flags.ignore_permissions = True
    ncr.insert()
    doc.db_set("linked_ncr", ncr.name)
```

### 3.4 Recall Event state changes (bao gồm fast-track Cấp 1 — chi tiết §9)

```python
# fsms_recall/api.py

def handle_recall_state_change(doc, method=None):
    if doc.workflow_state == "Đang thu hồi":
        # Auto-create NCR
        if not doc.linked_ncr:
            create_recall_ncr(doc)
        # Set fsms_recall_status on affected batches
        for ab in doc.affected_batches:
            frappe.db.set_value("Batch", ab.batch, "fsms_recall_status", "Đang thu hồi")
    
    if doc.workflow_state == "Đóng":
        for ab in doc.affected_batches:
            frappe.db.set_value("Batch", ab.batch, "fsms_recall_status", "Đã thu hồi")

def create_traceability_trace(doc, method=None):
    """Auto-create Traceability Trace when Recall Event submitted"""
    for ab in doc.affected_batches:
        trace = frappe.get_doc({
            "doctype": "FSMS Traceability Trace",
            "trigger": "Recall",
            "linked_recall_event": doc.name,
            "target_batch": ab.batch,
            "trace_date": today(),
            # backward_links and forward_links auto-populated by query
        })
        # Auto-populate from Stock Ledger Entry + PR + DN
        populate_trace_links(trace, ab.batch)
        trace.flags.ignore_permissions = True
        trace.insert()
```

### 3.5 Other server hooks — overview

| Module | File | Key functions |
|--------|------|---------------|
| `fsms_supplier/api.py` | `escalate_rejected_material()`, `update_supplier_profile()`, `auto_create_inspection_log()` |
| `fsms_equipment/api.py` | `escalate_failed_calibration()`, `sync_asset_status()` |
| `fsms_document_control/api.py` | `publish_document()` — update Document Register Internal/External khi DCR đến state Phát hành |
| `fsms_communication/api.py` | `handle_complaint()` — auto Recall + NCR khi severity Cấp 1/2 |
| `fsms_training/api.py` | `update_employee_competency()` — set `Employee.fsms_competency_status` |
| `fsms_haccp/api.py` | `sync_to_item_on_publish()`, `check_ccp_limits()`, `escalate_if_breach()` |
| `fsms_traceability/api.py` | `populate_trace_links()`, `register_batch()` |

---

## 4. Scheduled tasks chi tiết

### 4.1 Daily

```python
# fsms_ncr/tasks.py
def check_overdue_ncr():
    """Find NCR Đang thực hiện qua hạn → email notification"""
    overdue = frappe.get_all("FSMS NCR",
        filters={
            "workflow_state": "Đang thực hiện",
            "proposed_completion_date": ["<", today()]
        },
        fields=["name", "assigned_to", "approver", "proposed_completion_date", "ncr_date"]
    )
    for ncr in overdue:
        days_late = date_diff(today(), ncr.proposed_completion_date)
        send_overdue_email(ncr, days_late)
        if days_late > 7:
            escalate_to_bat_head(ncr)

# fsms_equipment/tasks.py
def check_calibration_due():
    """Equipment cần hiệu chuẩn trong 14 ngày"""
    upcoming = frappe.get_all("FSMS Measurement Equipment",
        filters={"next_calibration_date": ["between", [today(), add_days(today(), 14)]]},
        fields=["name", "equipment_name", "next_calibration_date"]
    )
    if upcoming:
        send_digest_email("QC", upcoming, "calibration_due")

# fsms_sample/tasks.py
def check_disposal_due():
    """Mẫu lưu đến hạn hủy"""
    due = frappe.get_all("FSMS Sample Retention Log",
        filters={"expected_disposal_date": ["<=", today()], "actual_disposal_date": ["is", "not set"]}
    )
    if due:
        send_digest_email("QC", due, "sample_disposal_due")

# fsms_emergency/tasks.py
def check_inspection_due():
    """Thiết bị PCCC + thiết bị an toàn đến hạn kiểm tra"""
    # Similar pattern
```

### 4.2 Weekly

```python
# fsms_document_control/tasks.py
def check_document_review_due():
    """Tài liệu nội bộ đến hạn review trong 30 ngày"""
    docs = frappe.get_all("FSMS Document Register Internal",
        filters={"next_review_date": ["between", [today(), add_days(today(), 30)]]}
    )
    for d in docs:
        notify_owner(d, "document_review_due")

# fsms_audit/tasks.py
def audit_plan_kickoff_reminder():
    """Audit Plan có audit_date_from trong 7 ngày → gửi reminder cho audit_team + auditees"""

# fsms_training/tasks.py
def training_compliance_digest():
    """Mỗi thứ Hai: tổng hợp NV chưa hoàn thành required course, gửi cho line manager + BAT_HEAD"""
    matrix = frappe.get_doc("FSMS Competency Matrix", current_year_doc())
    # Build compliance %
```

### 4.3 Monthly

```python
# fsms_context_risk/tasks.py
def risk_review_reminder():
    """Risk Register đến next_review_date trong tháng tới"""

# fsms_haccp/tasks.py
def haccp_plan_annual_review_check():
    """Plan có effective_date > 11 tháng trước → trigger Under Revision auto-suggest"""

# fsms_traceability/tasks.py
def drill_due_check():
    """Settings.mandatory_drill_frequency_months = 6 tháng → check last_drill_date, gợi ý drill mới"""
```

### 4.4 Yearly cron

```python
# fsms_audit/tasks.py
def year_end_audit_reminder():
    """Dec 1 mỗi năm → email BAT_HEAD chuẩn bị Audit Program năm sau"""
```

---

## 5. Whitelisted REST API methods

App expose một số custom REST endpoints cho Web/Mobile/Integration:

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `iso22000_fsms.api.create_ncr_from_external` | POST | Tạo NCR từ bên ngoài (vd Telegram bot phase 2) | API key + role check |
| `iso22000_fsms.api.get_ncr_summary` | GET | Tổng hợp NCR cho dashboard | Role check |
| `iso22000_fsms.api.get_traceability_query` | POST `{batch_no}` | Truy xuất nguồn gốc 1 lô | BAT_HEAD/AUDITOR |
| `iso22000_fsms.api.recall_phone_approval` | POST | Ghi nhận phone approval Cấp 1 (chi tiết §9) | TBP_KH/BAT_HEAD |
| `iso22000_fsms.api.dashboard_kpi_for_director` | GET | Dữ liệu cho GD Dashboard (chi tiết §7) | GD only |
| `iso22000_fsms.api.kcs_quick_inspect` | POST | Quick inspect endpoint cho KCS workflow mobile | QC role |
| `iso22000_fsms.api.export_for_authority` | POST | Export hồ sơ FSMS cho cơ quan QLNN khi bị thanh tra | BAT_HEAD/GD |

```python
# iso22000_fsms/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_traceability_query(batch_no, scope="both"):
    """
    scope: 'forward' / 'backward' / 'both'
    Returns: {forward: [...], backward: [...], time_taken_ms: N}
    """
    if not frappe.has_permission("FSMS Traceability Trace", "read"):
        frappe.throw(_("Không có quyền truy xuất nguồn gốc"))
    
    start = now_datetime()
    result = {"forward": [], "backward": []}
    
    if scope in ("backward", "both"):
        result["backward"] = query_backward_trace(batch_no)
    if scope in ("forward", "both"):
        result["forward"] = query_forward_trace(batch_no)
    
    result["time_taken_ms"] = (now_datetime() - start).total_seconds() * 1000
    return result

def query_backward_trace(batch_no):
    """Query Stock Ledger Entry để lấy NL đã consume cho batch này"""
    sql = """
    SELECT sle.item_code, sle.batch_no AS material_batch, 
           pri.purchase_receipt, pr.supplier, pri.qty, pr.posting_date
    FROM `tabStock Ledger Entry` sle
    LEFT JOIN `tabPurchase Receipt Item` pri ON pri.batch_no = sle.batch_no
    LEFT JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
    WHERE sle.against_voucher_type = 'Work Order'
      AND sle.batch_no IN (
        SELECT material_batch FROM `tabBOM Item` 
        WHERE parent = (SELECT bom_no FROM `tabWork Order` WHERE production_item = ...
      )
    """
    # ... refined query, return list of dicts
```

---

## 6. Custom Reports (Frappe Script Report)

| Report | Type | Audience | Purpose |
|--------|------|----------|---------|
| `FSMS NCR Aging` | Script Report | BAT_HEAD, GD | NCR mở theo độ tuổi (0-7 / 7-30 / 30+ ngày) |
| `FSMS NCR by Source × Department` | Script Report | BAT_HEAD | Pivot table NCR theo nguồn × bộ phận |
| `FSMS Audit Findings Trend` | Script Report | BAT_HEAD, GD | Trend NC Major/Minor theo quý |
| `FSMS Calibration Compliance` | Script Report | QC, BAT_HEAD | % thiết bị đo còn hợp chuẩn vs quá hạn |
| `FSMS Supplier Performance` | Script Report | TBP_KH, BAT_HEAD | Grade trung bình theo supplier × thời gian |
| `FSMS Recall Events YTD` | Script Report | GD | List recall events trong năm + cost impact |
| `FSMS Risk Heatmap` | Query Report | BAT_HEAD, GD | Risk × Likelihood × Severity, color-coded |
| `FSMS Training Compliance Matrix` | Script Report | TBP_KH, BAT_HEAD | Employee × Course × Status |
| `FSMS Document Review Due` | Standard Report | TBP_KH | List tài liệu đến hạn review |
| `FSMS HACCP Plan Status` | Standard Report | BAT_HEAD | List HACCP Plans + last review date |
| `FSMS Traceability Drill History` | Standard Report | BAT_HEAD | Drill outcomes + average completion time |
| `FSMS Sample Retention Inventory` | Standard Report | QC | Mẫu đang lưu + ngày hủy dự kiến |
| `FSMS Sanitation Compliance` | Script Report | QC, BAT_HEAD | % vệ sinh đạt theo ngày × ca |
| `FSMS Customer Complaint Analysis` | Script Report | TBP_KD, BAT_HEAD | Complaint theo channel × severity × resolution time |

---

## 7. GD Dashboard — design cụ thể

Theo decision của anh: GD operate ở dashboard level. Em thiết kế **Frappe Workspace** riêng cho role `FSMS Director`:

### 7.1 Workspace name: "Bảng điều khiển ATTP"

Layout 4 hàng × 3 cột (12 widget):

#### Hàng 1 — KPIs cấp cao (4 number cards)
| Widget | Source | Refresh |
|--------|--------|---------|
| Số NCR đang mở | Count `FSMS NCR` not in (Đã đóng, Chuyển tiếp) | Hourly |
| % NCR đóng đúng hạn (rolling 90 days) | Computed | Daily |
| Số recall events YTD | Count `FSMS Recall Event` this year | Daily |
| % audit findings đã đóng | Computed from Audit Execution + linked NCR | Daily |

#### Hàng 2 — Charts (3 widget)
| Widget | Type | Data |
|--------|------|------|
| NCR Trend 12 tháng | Bar chart | NCR count by month, stacked by severity |
| Audit Findings by Department | Pie chart | Distribution of NCR Major/Minor by affected_department |
| Risk Heatmap | Heatmap | Likelihood × Severity matrix from Risk Register |

#### Hàng 3 — Status lists (3 widget)
| Widget | Content |
|--------|---------|
| NCR Critical đang chờ phê duyệt của tôi | List of NCR where workflow_state = "Chờ phê duyệt" AND severity = Critical |
| Recall Events đang xử lý | List of Recall Event not in (Đóng) |
| Documents chờ phê duyệt | DCR + Manual + Policy + HACCP Plan in Pending Approval |

#### Hàng 4 — Bottom indicators (4 small widgets)
| Widget | Source |
|--------|--------|
| Calibration overdue count | Equipment count where next_cal < today |
| Sample disposal due count | Sample Retention count where expected_disposal_date <= today |
| Training compliance % | Employee with fsms_competency_status = "Đủ" / total |
| Last management review date | FSMS Management Review max(review_date) |

### 7.2 Implementation

```python
# iso22000_fsms/iso22000_fsms/workspace/fsms_director_dashboard.json
# Ship qua fixtures
# Bao gồm: Number Cards, Charts (Frappe Chart engine), Reports, Quick Lists
```

### 7.3 Dashboard API endpoint

```python
@frappe.whitelist()
def dashboard_kpi_for_director():
    """Single API call returning all KPIs for dashboard refresh"""
    if not has_role(frappe.session.user, "FSMS Director"):
        frappe.throw(_("Chỉ GD truy cập được"))
    
    return {
        "open_ncr_count": frappe.db.count("FSMS NCR", 
            {"workflow_state": ["not in", ["Đã đóng", "Chuyển tiếp"]]}),
        "ncr_on_time_pct": compute_ncr_on_time_pct(days=90),
        "recall_events_ytd": frappe.db.count("FSMS Recall Event",
            {"event_date": [">=", year_start()]}),
        "audit_findings_closed_pct": compute_audit_closure_pct(),
        # ... etc
    }
```

---

## 8. Email Notification templates

Templates ship qua fixtures, dùng Jinja:

| Template | Trigger | Recipients | Subject (VN) |
|----------|---------|------------|--------------|
| `ncr_pending_approval` | NCR enter `Chờ phê duyệt` | TBP_dept + BAT_HEAD | `[FSMS] NCR {{name}} chờ phê duyệt — {{severity}}` |
| `ncr_overdue` | Daily scheduler hit | assigned_to + approver | `[FSMS] NCR {{name}} quá hạn {{days_late}} ngày` |
| `ncr_from_audit` | Auto-create from audit | affected_department head | `[FSMS] NCR mới từ đánh giá nội bộ {{audit_no}}` |
| `ncr_critical_escalation` | NCR severity Critical → GD | GD | `[FSMS-CRITICAL] NCR {{name}} cần phê duyệt khẩn cấp` |
| `recall_event_initiated` | Recall Event created | GD + BAT_HEAD + TBP_KD + TBP_SX | `[FSMS-RECALL] Recall Event {{name}} — Cấp {{level}}` |
| `recall_phone_approval_required` | Recall Event Cấp 1 | GD (multiple channels) | `[FSMS-URGENT] Cần phê duyệt qua điện thoại — Recall Cấp 1` |
| `calibration_due_digest` | Weekly | QC + TBP_SX | `[FSMS] Hiệu chuẩn đến hạn — {{count}} thiết bị` |
| `sample_disposal_due` | Daily | QC | `[FSMS] {{count}} mẫu lưu đến hạn hủy` |
| `document_review_due` | Monthly | doc owner + BAT_HEAD | `[FSMS] {{count}} tài liệu đến hạn review` |
| `audit_kickoff_reminder` | 7 days before | audit_team + auditees | `[FSMS] Audit {{name}} kickoff ngày {{date}}` |
| `haccp_plan_annual_review` | Monthly cron, 60 ngày trước | BAT_HEAD | `[FSMS] HACCP Plan {{plan_no}} đến hạn review hằng năm` |
| `training_compliance_digest` | Weekly | line manager + BAT_HEAD | `[FSMS] Tổng hợp đào tạo — {{compliance_pct}}%` |

---

## 9. RECALL CẤP 1 FAST-TRACK MODE (theo decision anh chốt)

### 9.1 Vấn đề
Recall Cấp 1 (nguy hiểm tử vong) không thể chờ GD bấm nút trên hệ thống → cần fast-track:
- Phone approval trước
- Bắt đầu thu hồi vật lý NGAY
- GD bấm nút lùi sau (system approval)
- Audit trail đầy đủ: ai gọi, ai nhận điện, lúc mấy giờ, GD ký system lúc nào

### 9.2 Schema thay đổi cho `FSMS Recall Event`

Thêm fields vào blueprint module 5:

| Field | Type | Mô tả |
|-------|------|-------|
| `is_fast_track` | Check | Set khi `defect_severity = Cấp 1` |
| `phone_approval_received_at` | Datetime | Lúc TBP_KH/BAT_HEAD nhận điện thoại từ GD |
| `phone_approval_received_by` | Link → Employee | Ai nhận điện thoại (TBP_KH/BAT_HEAD) |
| `phone_approval_evidence` | Long Text | Tóm tắt nội dung điện thoại + bằng chứng (ảnh chụp màn hình, ghi âm hợp pháp nếu có) |
| `phone_approval_witnesses` | Table | Danh sách nhân chứng (Employee + role) |
| `gd_system_approval_at` | Datetime | Lúc GD bấm nút trên hệ thống (back-date allowed) |
| `time_lag_minutes` | Int | gd_system_approval_at - phone_approval_received_at (auto, để audit kiểm tra) |

### 9.3 Workflow điều chỉnh

```
Phát sinh → Lập kế hoạch → [Đang thu hồi] → Bảo quản → Báo cáo → Đóng
                              ↑
                              │
            ┌─────────────────┼─────────────────────────┐
            │                                            │
   Standard path:                                Fast-track path:
   GD bấm nút trên hệ thống                      TBP_KH/BAT_HEAD nhận điện
   trước khi vào "Đang thu hồi"                  thoại → Bấm nút "Bắt đầu
                                                  fast-track" → Vào "Đang
                                                  thu hồi" ngay → GD bấm
                                                  nút system phê duyệt
                                                  retroactive trong 24h
```

### 9.4 Implementation

```python
# fsms_recall/api.py

@frappe.whitelist()
def initiate_fast_track_recall(recall_event_name, phone_approval_data):
    """
    Called when TBP_KH/BAT_HEAD receives phone approval from GD for Cấp 1 recall
    
    phone_approval_data = {
      "received_at": "2026-05-06 14:30:00",
      "received_by": "EMP-001",
      "evidence": "GD đồng ý qua điện thoại lúc 14:30, audio note attached",
      "witnesses": [{"employee": "EMP-002", "role": "Phó GĐ"}, ...]
    }
    """
    doc = frappe.get_doc("FSMS Recall Event", recall_event_name)
    
    # Validation
    if doc.defect_severity != "Cấp 1":
        frappe.throw(_("Fast-track chỉ áp dụng cho Recall Cấp 1"))
    if doc.workflow_state != "Lập kế hoạch":
        frappe.throw(_("Recall Event phải ở state Lập kế hoạch"))
    if not has_role(frappe.session.user, ["FSMS Manager", "FSMS Planning Lead"]):
        frappe.throw(_("Chỉ BAT_HEAD hoặc TBP_KH initiate fast-track"))
    if not phone_approval_data.get("witnesses"):
        frappe.throw(_("Phải có ít nhất 1 nhân chứng"))
    
    # Set fast-track fields
    doc.is_fast_track = 1
    doc.phone_approval_received_at = phone_approval_data["received_at"]
    doc.phone_approval_received_by = phone_approval_data["received_by"]
    doc.phone_approval_evidence = phone_approval_data["evidence"]
    doc.phone_approval_witnesses = phone_approval_data["witnesses"]
    
    # Force workflow transition (bypass standard GD approve gate)
    doc.workflow_state = "Đang thu hồi"
    doc.flags.ignore_workflow = True
    doc.save()
    doc.submit()
    
    # Send GD a "URGENT — phải bấm nút retro" notification + email
    send_gd_retro_approval_request(doc)
    
    # Trigger standard hooks (NCR auto-create, Trace, etc.)
    handle_recall_state_change(doc)
    
    # Log to Frappe Activity for audit
    frappe.log_activity(...)
    
    return {"status": "fast-track activated", "recall": doc.name}


@frappe.whitelist()
def gd_retroactive_approval(recall_event_name):
    """GD clicks button after-the-fact to formalize phone approval"""
    if not has_role(frappe.session.user, "FSMS Director"):
        frappe.throw(_("Chỉ GD"))
    
    doc = frappe.get_doc("FSMS Recall Event", recall_event_name)
    if not doc.is_fast_track:
        frappe.throw(_("Không phải fast-track"))
    if doc.gd_system_approval_at:
        frappe.throw(_("Đã được phê duyệt trên hệ thống"))
    
    doc.gd_system_approval_at = now_datetime()
    doc.time_lag_minutes = int(
        (now_datetime() - doc.phone_approval_received_at).total_seconds() / 60
    )
    
    # Validation: SLA cho retroactive approval = 24 giờ
    if doc.time_lag_minutes > 24 * 60:
        frappe.msgprint(_("CẢNH BÁO: Phê duyệt retroactive quá 24 giờ kể từ phone approval"),
                        alert=True, indicator="red")
    
    doc.save()
    return {"status": "approved", "lag_minutes": doc.time_lag_minutes}


def send_gd_retro_approval_request(doc):
    """Notify GD via email + in-app + (phase 2) Telegram/Zalo"""
    frappe.sendmail(
        recipients=[get_gd_email()],
        subject=f"[FSMS-CRITICAL] Recall Cấp 1 đã start — cần phê duyệt retroactive: {doc.name}",
        template="recall_phone_approval_required",
        args={"doc": doc, "phone_at": doc.phone_approval_received_at}
    )
    # Daily reminder until GD bấm nút
    schedule_reminder(doc, "gd_retro_approval", days=[0, 0.5, 1])
```

### 9.5 Báo cáo audit cho fast-track

Trong `FSMS Recall Report` thêm section bắt buộc khi `is_fast_track = 1`:

| Field | Mô tả |
|-------|-------|
| `fast_track_summary` | Tóm tắt timeline (phone → executing → system approval) |
| `time_lag_justification` | Lý do nếu time_lag > 4 giờ |
| `phone_approval_audit_attached` | Attach evidence file (audio, screenshot, witness statement) |

### 9.6 Reporting trong management review

`FSMS Management Review Input` có topic riêng "Recall events including fast-track usage" — auto-pull khi review tổng kết năm.

---

## 10. ERPNext version requirement & migration note

### 10.1 Yêu cầu
- **Frappe v16.x** (LTS hoặc latest stable)
- **ERPNext v16.x**
- Python 3.11+
- MariaDB 10.6+ hoặc PostgreSQL 14+ (Frappe v16 hỗ trợ cả 2)
- Node 18+

### 10.2 Lưu ý cho RVHG (đang trên ERPNext v14)

Anh đang vận hành ERPNext v14 cho RVHG. App này **KHÔNG cài được trên v14** vì dùng feature v15+:
- `Workflow Action Master` schema mới (v15)
- `Custom Field` insert_after có hỗ trợ tab break (v15)
- Frappe Activity Log structure (v16)
- `permission_query_conditions` enhancement (v16)

→ App này phụ thuộc vào việc anh hoàn thành **migration v14 → v16** trên RVHG (đã có trong roadmap riêng của anh, theo memory). Kế hoạch:

1. RVHG hoàn tất migrate v14 → v15 → v16 (đang trong roadmap riêng)
2. Cài `iso22000_fsms` trên môi trường staging v16
3. UAT 2 tuần trên staging với data thật
4. Go-live trên production v16

→ **Không** thiết kế backward compat sang v14. Lý do: schema differences quá lớn, maintain 2 phiên bản tốn effort hơn migrate.

### 10.3 Dependencies trong setup.py

```python
# iso22000_fsms/setup.py (excerpt)
install_requires = [
    "frappe>=16.0.0",
    "erpnext>=16.0.0",
]
```

`hooks.py`:
```python
required_apps = ["frappe", "erpnext"]
```

---

## 11. Trạng thái + bước tiếp theo

- **Đã hoàn thành**: 00–04 + QT 09 + **05 integration plan**
- **Đang chờ**: anh review file này, đặc biệt:
  - GD Dashboard 12 widgets §7.1 — anh muốn thêm/bớt widget nào không?
  - Recall fast-track schema §9.2 — phone_approval_witnesses bắt buộc ≥ 1 nhân chứng — anh thấy strict quá hay đúng?
  - Custom Reports §6 — anh có muốn thêm report nào không (vd theo tháng, theo product line)?
  - Section §10 nói rõ phụ thuộc migration v14→v16 — confirm timeline khớp với roadmap migration của anh?
- **Sau khi duyệt 05**: Em sang `06_fixtures_plan.md` — chốt list fixtures (Roles, Custom Fields, Permissions, Workflows, Workflow States, Notifications, Email Templates, Print Formats, Master data: Document Categories / NCR Sources / Risk Score Reference / Supplier Categories / Emergency Scenarios / PRP Items templates).
- **Sau 06**: Anh approve `06_fixtures_plan.md` → em sẵn sàng handoff sang `nextcode-build` để scaffold app code thật.

---

**End of `05_integration_plan.md` — chờ anh review.**
