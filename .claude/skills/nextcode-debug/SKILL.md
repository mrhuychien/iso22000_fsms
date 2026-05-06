---
name: nextcode-debug
description: Use when the user reports a bug, error, traceback, or unexpected behavior in a Frappe/ERPNext v16 environment — and wants to investigate root cause. Triggers include "bug", "lỗi", "traceback", "AttributeError", "PermissionError", "DoesNotExistError", "TimestampMismatchError", "validation error mà tôi không hiểu", "hook không chạy", "background job stuck", "queue đang stuck", "permission denied dù đã có role", "Server Script bị skip", "scheduler không trigger", "cache stale", "ImportError after migrate". Do NOT use this skill for designing new features (use nextcode-design), implementing from spec (use nextcode-build), or general performance tuning that isn't tied to a specific bug (use nextcode-perf). This skill is evidence-driven investigation, not speculation.
---

# Nextcode Debug — Frappe Investigation Master

Skill này áp dụng **9-step Investigation Protocol** của Vibecode V5 cho Frappe-specific bug.

Đọc full master prompt ở `references/prompt.md`.

## Quick reference

**Triết lý**: KHÔNG đoán. KHÔNG fix khi chưa hiểu root cause. Mỗi giả thuyết phải có **evidence** trước khi chấp nhận.

**Output**:
- `INVESTIGATION.md` — log toàn quá trình (giả thuyết → evidence → kết luận)
- Root cause statement (1 câu)
- Reproduction steps (deterministic)
- Fix proposal (kèm rollback plan)
- Test case để đảm bảo bug không tái phát

**Frappe-specific tools** em sẽ chỉ định cho user chạy:
- `bench --site X console` (REPL)
- `frappe.log_error()` đọc qua Error Log
- `frappe.db.sql.log_queries = True`
- `bench worker --queue long` (xem background job real-time)
- `bench --site X clear-cache`
- `bench --site X migrate --resume`
