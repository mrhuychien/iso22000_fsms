# Cài đặt iso22000_fsms

Hướng dẫn cài đặt chi tiết cho RVHG (hoặc môi trường tương đương).

## 1. Tiền điều kiện

| Mục | Yêu cầu |
|---|---|
| Frappe Framework | v16 |
| ERPNext | v16 (cùng major version với Frappe) |
| MariaDB | 10.6+ |
| Python | 3.10+ |
| Node.js | 18+ |
| Redis | 6+ |
| OS | Ubuntu 22.04 / Debian 12 / RHEL 9 |

Kiểm tra version hiện tại:

```bash
bench version
# frappe 16.x.x
# erpnext 16.x.x
```

## 2. Cài đặt app

### 2.1. Clone vào bench

```bash
cd ~/frappe-bench
bench get-app https://github.com/mrhuychien/iso22000_fsms
```

Hoặc nếu đã clone local:

```bash
bench get-app /path/to/iso22000_fsms
```

### 2.2. Install vào site

```bash
# Backup trước (an toàn)
bench --site rvhg.local backup --with-files

# Install
bench --site rvhg.local install-app iso22000_fsms

# Migrate (chạy patches)
bench --site rvhg.local migrate

# Build assets (CSS + JS)
bench build --app iso22000_fsms

# Restart bench
bench restart
```

### 2.3. Verify install

```bash
bench --site rvhg.local console
```

```python
>>> import frappe
>>> frappe.get_installed_apps()
['frappe', 'erpnext', 'iso22000_fsms']

>>> frappe.db.count("FSMS NCR Source")
7  # ← from fixtures

>>> frappe.db.count("Workflow", {"name": ["like", "FSMS%"]})
28
```

## 3. Cấu hình ban đầu (post-install)

### 3.1. FSMS Settings

Vào `/app/fsms-settings`, điền:
- `company_name`: Công ty CP Hoàng Giang
- `tax_id`: MST
- `address`: Địa chỉ trụ sở
- `scope_organization`: Phạm vi tổ chức (vd: "Toàn bộ hoạt động sản xuất bánh đậu xanh, bột đậu")
- `scope_location`: Phạm vi địa điểm
- `scope_product`: Phạm vi sản phẩm
- `std_version`: ISO 22000:2018 (default)
- `retention_years_default`: 3 (default)
- `mandatory_drill_frequency_months`: 12 (default)

### 3.2. Gán role cho user

Vào `/app/user`. Cho mỗi user, gán role tương ứng:

| User loại | Role nên gán |
|---|---|
| Giám đốc | `FSMS Director` |
| Trưởng ban ATTP | `FSMS Manager` |
| Đánh giá viên nội bộ | `FSMS Internal Auditor` |
| Trưởng phòng SX | `FSMS Production Lead` + `Production Department Head` |
| Trưởng phòng KD | `FSMS Sales Lead` + `Sales Department Head` |
| Trưởng phòng KH | `FSMS Planning Lead` + `Planning Department Head` |
| Trưởng phòng KT | `FSMS Accounting Lead` + `Accounting Department Head` |
| QC | `FSMS QC Officer` |
| Thành viên ban ATTP | `FSMS Team Member` |
| Nhân viên thường | `FSMS Employee` |

### 3.3. Department + Employee

- Vào `/app/department` đảm bảo có các phòng ban: Sản xuất, Kinh doanh, Kế hoạch, Kế toán, QC, ATTP.
- Mỗi phòng ban gán `parent_department` và `Employee Head` (cho phân quyền NCR).
- Vào `/app/employee` mở từng record:
  - Upload `signature` (chữ ký scan) hoặc `fsms_signature_image`
  - Đảm bảo `department` đúng

### 3.4. Tạo FSMS Manual + Policy

- `/app/fsms-manual` → tạo phiên bản 1.0, scope, sơ đồ tổ chức, chính sách link.
- `/app/fsms-policy` → tạo phiên bản 1.0, nội dung chính sách, cam kết lãnh đạo.
- Submit → Approve → Publish workflow.

### 3.5. (Tùy chọn) Import master data từ CSV

Nếu có dữ liệu nhà cung cấp / khách hàng cần import từ Excel cũ:

```bash
bench --site rvhg.local data-import --doctype Supplier --filepath /path/to/suppliers.csv
bench --site rvhg.local data-import --doctype Customer --filepath /path/to/customers.csv
```

## 4. Smoke test

Sau cài đặt, chạy thử quy trình NCR end-to-end:

1. Login bằng user role `FSMS Team Member`.
2. Mở `/app/fsms-ncr/new` → điền nội dung sự không phù hợp.
3. Action workflow `Gửi phân tích` → state chuyển `Phân tích`.
4. Login bằng `FSMS Manager` → điền root cause + biện pháp + assignee → `Gửi phê duyệt`.
5. Login bằng `FSMS Director` → `Phê duyệt` → state `Đang thực hiện`.
6. Login bằng assignee → cập nhật actual_completion_date → `Hoàn thành thực hiện`.
7. Login bằng `FSMS Internal Auditor` → kết quả xác minh "Đạt yêu cầu" → `Đạt - đóng phiếu`.
8. Verify: NCR ở trạng thái `Đã đóng`.

## 5. Troubleshooting

### Fixtures không load

```bash
bench --site rvhg.local install-app iso22000_fsms --force
bench --site rvhg.local migrate
```

### Workflow không apply

```bash
# Kiểm tra Workflow records đã tồn tại
bench --site rvhg.local execute frappe.get_all "['Workflow', None, ['name'], {'document_type': ['like', 'FSMS%']}]"

# Re-import nếu cần
bench --site rvhg.local export-fixtures --app iso22000_fsms
```

### Permission denied trên DocType

```bash
# Verify role đã được gán
bench --site rvhg.local execute frappe.get_roles "['user@example.com']"

# Bulk-assign role nếu cần
bench --site rvhg.local console
>>> frappe.get_doc({"doctype": "User", "name": "user@example.com"}).add_roles("FSMS Manager")
```

### CSS/JS không load

```bash
bench build --app iso22000_fsms --hard-link
bench restart
```

Mở DevTools → Network tab → kiểm tra `/assets/iso22000_fsms/css/fsms.css` HTTP 200.

## 6. Backup + restore

```bash
# Backup full với files
bench --site rvhg.local backup --with-files

# Restore
bench --site rvhg.local restore /path/to/backup.sql.gz \
  --with-private-files /path/to/files-private.tar \
  --with-public-files /path/to/files.tar
```

## 7. Uninstall (với cảnh báo)

⚠️ **CẨN TRỌNG**: Uninstall sẽ xóa **toàn bộ dữ liệu** của 18 module FSMS. Backup trước khi chạy.

```bash
bench --site rvhg.local backup --with-files
bench --site rvhg.local uninstall-app iso22000_fsms

# Custom Field còn lại trong DB → cần migrate để clean
bench --site rvhg.local migrate
```

`before_uninstall` hook sẽ cảnh báo nếu phát hiện NCR / Recall Event / HACCP / Audit Execution có dữ liệu thực.
