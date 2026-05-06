---
name: nextcode-build
description: Use when the user has an APPROVED design/spec/blueprint for a Frappe/ERPNext v16 custom app and wants to actually scaffold and implement it — generating bench commands, DocType JSON files, Python controllers, hooks.py, Server Scripts, Client Scripts, whitelisted API methods, fixtures, and Print Formats. Triggers include "scaffold app", "tạo DocType", "viết hooks.py", "implement controller", "viết whitelisted method", "tạo Print Format", "fixtures export", "build từ blueprint". Do NOT use this skill if the design isn't ready (use nextcode-design first), or for debugging/auditing existing code (use nextcode-debug or nextcode-xray). This skill writes app code; it requires an approved blueprint as input.
---

# Nextcode Build — Custom App Implementation Master

Skill này áp dụng **Coder Pack discipline** của Vibecode V5 vào Frappe domain.

Tiền điều kiện: **đã có blueprint duyệt** (từ `nextcode-design`) hoặc spec rõ ràng do user cung cấp. Nếu chưa, em từ chối build và yêu cầu chạy `nextcode-design` trước.

Đọc full master prompt ở `references/prompt.md`.

## Quick reference

**Output bắt buộc**:
- Bench commands (sequential, có comment giải thích)
- DocType JSON (đầy đủ, không gọn)
- Python controller class (với hooks: validate, before_save, on_submit, ...)
- `hooks.py` block-by-block
- Server/Client Scripts khi phù hợp (vs. file Python trong app — em sẽ giải thích trade-off)
- Whitelisted API methods
- Print Format (Jinja, dùng class prefix khi embed vào ERPNext UI)
- Patches.txt + patch files
- Fixtures export commands

**Quy ước**:
- App name snake_case
- 1 file = 1 chức năng (KHÔNG nhồi nhiều DocType vào 1 file)
- Mọi whitelisted method có docstring + permission check
- Mọi `frappe.db.sql` có comment giải thích vì sao không dùng ORM
