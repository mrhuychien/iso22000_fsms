from . import __version__ as app_version

app_name = "iso22000_fsms"
app_title = "ISO 22000 FSMS"
app_publisher = "Công ty CP Hoàng Giang"
app_description = "Hệ thống quản lý ATTP theo ISO 22000:2018"
app_email = "hoanggiavn.vn@gmail.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# ============================================================================
# Static asset bundles
# ============================================================================
app_include_css = ["/assets/iso22000_fsms/css/fsms.css"]
app_include_js = ["/assets/iso22000_fsms/js/fsms_client.js"]

# ============================================================================
# Lifecycle
# ============================================================================
after_install = "iso22000_fsms.install.after_install"
before_uninstall = "iso22000_fsms.install.before_uninstall"

# ============================================================================
# Document Events — server hooks per DocType
# ============================================================================
doc_events = {
	"FSMS NCR": {
		"validate": "iso22000_fsms.fsms_ncr.api.validate_ncr",
		"before_save": "iso22000_fsms.fsms_ncr.api.set_signatures",
		"on_submit": "iso22000_fsms.fsms_ncr.api.notify_assignees",
		"on_update_after_submit": "iso22000_fsms.fsms_ncr.api.handle_state_changes",
		"on_cancel": "iso22000_fsms.fsms_ncr.api.audit_cancellation",
	},
	"FSMS Audit Execution": {
		"on_submit": "iso22000_fsms.fsms_audit.api.create_ncr_from_findings",
	},
	"FSMS Audit Finding": {
		"validate": "iso22000_fsms.fsms_audit.api.validate_finding",
	},
	"FSMS Recall Event": {
		"on_update_after_submit": "iso22000_fsms.fsms_recall.api.handle_recall_state_change",
		"on_submit": "iso22000_fsms.fsms_recall.api.create_traceability_trace",
	},
	"FSMS Customer Complaint": {
		"on_submit": "iso22000_fsms.fsms_communication.api.handle_complaint",
	},
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
		"0 8 1 12 *": ["iso22000_fsms.fsms_audit.tasks.year_end_audit_reminder"],
	},
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
# Jinja helpers (Print Format + email templates)
# ============================================================================
jinja = {
	"methods": [
		"iso22000_fsms.utils.format_vnd",
		"iso22000_fsms.utils.format_vn_date",
		"iso22000_fsms.utils.signature_or_blank",
	],
}

# ============================================================================
# Fixtures (loaded on app install)
# ============================================================================
fixtures = [
	{"doctype": "Role", "filters": [["role_name", "like", "FSMS%"]]},
	{"doctype": "Role", "filters": [["role_name", "in", [
		"Production Department Head", "Sales Department Head",
		"Planning Department Head", "Accounting Department Head",
	]]]},
	{"doctype": "Custom Field", "filters": [["fieldname", "like", "fsms_%"]]},
	{"doctype": "Property Setter", "filters": [["module", "in", [
		"FSMS Core", "FSMS Traceability", "FSMS Supplier", "FSMS Recall",
	]]]},
	{"doctype": "Workflow State"},
	{"doctype": "Workflow Action Master"},
	{"doctype": "Workflow", "filters": [["name", "like", "FSMS%"]]},
	{"doctype": "Notification", "filters": [["module", "=", "ISO 22000 FSMS"]]},
	{"doctype": "Email Template", "filters": [["name", "like", "FSMS%"]]},
	{"doctype": "Print Format", "filters": [["module", "=", "ISO 22000 FSMS"]]},
	{"doctype": "Dashboard Chart", "filters": [["module", "=", "ISO 22000 FSMS"]]},
	{"doctype": "Number Card", "filters": [["module", "=", "ISO 22000 FSMS"]]},
	{"doctype": "Dashboard", "filters": [["module", "=", "ISO 22000 FSMS"]]},
	{"doctype": "Workspace", "filters": [["module", "=", "ISO 22000 FSMS"]]},
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
