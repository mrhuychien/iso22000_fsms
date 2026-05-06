# 00 — Document Master Inventory

> **App**: ISO 22000 FSMS App for Công ty CP Hoàng Giang (RVHG)
> **Source**: `Hệ thống quy trình.zip` — 52 active files (sau khi loại temp/junk)
> **Tiêu chuẩn**: ISO 22000:2018
> **Ngày**: 2026-05-06
> **Trạng thái**: Draft v0.1 — chờ anh phê duyệt trước khi sang `01_business_model.md`

---

## 1. Naming convention quan sát được

| Prefix | Nghĩa | Số lượng | Frappe mapping (preview, sẽ chốt ở `02_doctype_blueprint.md`) |
|--------|-------|----------|---------------------------------------------------------------|
| `QT`   | Quy Trình hệ thống | 8 | Mở rộng `Quality Procedure` (ERPNext core) hoặc tạo `FSMS Procedure` |
| `BM`   | Biểu Mẫu (form trắng cho người dùng điền) | 21 | Mỗi BM → 1 DocType riêng (e.g. `FSMS NCR Request`, `FSMS Internal Audit Plan`) |
| `HD`   | Hướng Dẫn công việc | 1 | DocType phụ hoặc Web Page nội bộ |
| `KH.HACCP` | Kế hoạch HACCP | 2 | DocType mới `HACCP Plan` + Child Table `HACCP Step / CCP` |
| `QĐ`   | Quy Định / Quyết định | 1 | DocType `FSMS Regulation` (sub-type) |
| `PL`   | Phụ Lục | 5 | Attached file của parent QT, không tạo DocType riêng |
| `Sổ`   | Sổ ghi chép (record book — tích lũy nhiều dòng theo thời gian) | 4 | DocType có thiết kế list-style (1 record = 1 dòng) |

---

## 2. Cây tài liệu theo tier

### Tier 0 — Foundation (4 file)
| File | Mô tả | Frappe target |
|------|-------|---------------|
| `So tay an toan thuc pham.doc` | Sổ tay FSMS (master document) | `FSMS Manual` (Single DocType) — chỉ 1 record duy nhất |
| `1.So do to chuc, chuc nang nhiem vu cac bo phan.doc` | QĐ 01/QĐ-HG ngày 12/05/2017 — Sơ đồ tổ chức + chức năng nhiệm vụ | Render từ Frappe `Department` + `Employee` + Print Format |
| `Chính sách ATTP.doc` | Chính sách ATTP | Field text trong `FSMS Manual` |
| `Mục tiêu ATTP.doc` | Mục tiêu ATTP | DocType `FSMS Objective` (multi-record, có review định kỳ) |

### Tier 1 — Quy Trình hệ thống (8 QT)
| Code | Tên | Biểu mẫu | Phụ lục / Sub-content |
|------|-----|----------|------------------------|
| QT 01 | Quản lý chung hệ thống ATTP *(gộp 5 việc: kiểm soát tài liệu, kiểm soát hồ sơ, đánh giá nội bộ, kiểm soát KPH + CAR, họp xem xét lãnh đạo)* | BM.01.01 → BM.01.09 (9) | — |
| QT 02 | Thu hồi sản phẩm | BM.02.01 → BM.02.02 (2) | — |
| QT 03 | Ứng phó tình huống khẩn cấp | BM.03.01 → BM.03.03 (3) | PL.03.01–05 (5 phụ lục), thư mục con `Phương án PCCC` (3 file) |
| QT 04 | Thẩm tra hệ thống | BM.04.01 → BM.04.02 (2) | — |
| QT 05 | Xác định bên quan tâm và rủi ro *(clause 4)* | BM.05.01 → BM.05.02 (2) | — |
| QT 06 | Quản lý thiết bị sản xuất và thiết bị đo *(clause 7.1.5)* | **Chưa có BM riêng?** | — |
| QT 07 | Mua hàng, đánh giá lựa chọn nhà cung cấp | BM.07.01 → BM.07.03 (3) | HD.07.01 (Kế hoạch kiểm soát chất lượng vật tư) |
| QT 08 | Quản lý sản xuất | **Chưa có BM riêng?** | — |

### Tier 2 — HACCP (3 file)
| File | Mô tả |
|------|-------|
| `KH.HACCP.01 — Kế hoạch HACCP (bánh đậu xanh).doc` + `So do quy trinh san xuat Banh dau xanh.doc` | HACCP plan + flowchart sản xuất bánh đậu |
| `KH.HACCP.02 — Kế hoạch HACCP (bột đậu).doc` | HACCP plan bột đậu |
| `SỔ THEO DÕI KIỂM TRA THÀNH PHẨM.doc` | Sổ ghi monitoring thành phẩm (record book) |

### Tier 3 — PRP / Vệ sinh (4 file)
| File | Mô tả | Frappe target |
|------|-------|---------------|
| `He thong PRP.doc` | Master PRP system doc | `FSMS PRP Program` |
| `Bao cao tinh hinh ve sinh của Cong ty.doc` | Báo cáo tình hình vệ sinh | DocType `FSMS Sanitation Report` |
| `So kiem tra ve sinh Cong nhan hang ngay.doc` | Sổ KT vệ sinh CN hàng ngày | DocType `FSMS Worker Hygiene Log` (record book pattern) |
| `Sổ kiểm tra vệ sinh công nhân.xlsx` | (Có vẻ là phiên bản Excel của trên — em sẽ verify) | Same — đè bản .doc nếu trùng nội dung |

### Tier 4 — Quy Định riêng (2 file)
| File | Mô tả |
|------|-------|
| `QD.01 Luu mau san pham.doc` | Quy định lưu mẫu sản phẩm |
| `Sổ lưu mẫu.doc` | Sổ ghi log lưu mẫu |

### Tier 5 — Biểu mẫu (21 BM, đếm chi tiết)
| Group | BM | Tên |
|-------|-----|-----|
| QT 01 | BM.01.01 | Phiếu yêu cầu sửa đổi tài liệu |
| QT 01 | BM.01.02 | Danh mục tài liệu nội bộ |
| QT 01 | BM.01.03 | Danh mục tài liệu bên ngoài |
| QT 01 | BM.01.04 | Danh mục hồ sơ |
| QT 01 | BM.01.05 | Chương trình và kế hoạch đánh giá |
| QT 01 | BM.01.06 | Check list đánh giá |
| QT 01 | **BM.01.07** | **Phiếu yêu cầu hành động khắc phục — đây là trung tâm NCR/CAR** |
| QT 01 | BM.01.08 | Điểm lưu ý (audit observation) |
| QT 01 | BM.01.09 | Bảng tổng hợp kết quả đánh giá |
| QT 02 | BM.02.01 | Kế hoạch thu hồi sản phẩm |
| QT 02 | BM.02.02 | Báo cáo thu hồi sản phẩm |
| QT 03 | BM.03.01 | Sổ theo dõi thiết bị PCCC |
| QT 03 | BM.03.02 | Sổ theo dõi tình trạng phát sinh dịch bệnh |
| QT 03 | BM.03.03 | Sổ theo dõi kiểm định thiết bị an toàn |
| QT 04 | BM.04.01 | Kế hoạch thẩm tra |
| QT 04 | BM.04.02 | Báo cáo thẩm tra |
| QT 05 | BM.05.01 | Bảng xác định các bên quan tâm |
| QT 05 | BM.05.02 | Bảng xác định rủi ro |
| QT 07 | BM.07.01 | Phiếu đánh giá nhà cung ứng |
| QT 07 | BM.07.02 | Danh sách nhà cung ứng |
| QT 07 | BM.07.03 | Sổ kiểm tra chất lượng vật tư, hàng hóa nhập vào |

### Tier 6 — Phụ lục QT 03 (5 PL — kịch bản ứng phó)
- PL.03.01 Ứng phó bão lũ
- PL.03.02 Phương án chữa cháy
- PL.03.03 Ứng phó với điện
- PL.03.04 Dịch bệnh
- PL.03.05 Thông tin sản phẩm (sản phẩm bị nhầm lẫn / sai thông tin)

### Tier 7 — Hướng Dẫn (1 HD)
- HD.07.01 Kế hoạch kiểm soát chất lượng vật tư, nguyên liệu

### Phụ — PCCC sub-folder (3 file)
- Biên bản thực tập phương án PCCC
- Hồ sơ quản lý PCCC 2018
- Kế hoạch thực tập phương án PCCC
*(không nằm trong scope ISO 22000 thuần túy — là hồ sơ pháp lý PCCC riêng. Em đề xuất TÁCH ra app khác hoặc folder riêng trong app này, không lẫn với FSMS workflow.)*

---

## 3. Mapping vs ISO 22000:2018 clauses

| Clause | Yêu cầu | RVHG doc tương ứng | Status |
|--------|---------|---------------------|--------|
| 4. Bối cảnh tổ chức | Hiểu tổ chức + bên quan tâm | QT 05 | ✓ |
| 5. Lãnh đạo | Cam kết + chính sách | Sổ tay + Chính sách ATTP | ✓ |
| 6. Hoạch định | Mục tiêu + xử lý rủi ro | Mục tiêu ATTP + QT 05 | ✓ |
| 7.1.4 | Môi trường làm việc | (gộp PRP?) | ⚠️ verify |
| 7.1.5 | Thiết bị giám sát đo | QT 06 | ✓ |
| 7.1.6 | Yếu tố từ bên ngoài (NCC, dịch vụ outsource) | QT 07 | ✓ |
| 7.2 | Năng lực | **THIẾU** (chưa thấy QT/BM training) | ❌ |
| 7.3 | Nhận thức | (gộp Sổ tay?) | ⚠️ |
| 7.4 | Trao đổi thông tin (nội bộ + bên ngoài) | (chưa rõ) | ⚠️ |
| 7.5 | Kiểm soát thông tin dạng văn bản | QT 01 (phần kiểm soát tài liệu + hồ sơ) | ✓ |
| 8.2 | PRP | Hệ thống PRP + Sổ vệ sinh | ✓ |
| 8.3 | Truy xuất nguồn gốc | **THIẾU QT riêng** (có thể gộp QT 02/QT 08) | ⚠️ |
| 8.4 | Chuẩn bị + ứng phó tình huống khẩn cấp | QT 03 (rất mạnh, có 5 PL + PCCC) | ✓ |
| 8.5 | Phân tích mối nguy + HACCP plan | KH.HACCP.01 + 02 | ✓ |
| 8.6 | Cập nhật thông tin PRP/HACCP | (gộp QT 04?) | ⚠️ |
| 8.7 | Kiểm soát giám sát đo lường | QT 06 | ✓ |
| 8.8 | Thẩm tra (verification) | QT 04 | ✓ |
| 8.9 | Kiểm soát sản phẩm/quá trình KPH + thu hồi | QT 02 + BM.01.07 | ✓ |
| 9.1 | Theo dõi, đo lường, phân tích, đánh giá | QT 04 | ✓ |
| 9.2 | Đánh giá nội bộ | QT 01 (gộp) + BM.01.05–09 | ✓ |
| 9.3 | Họp xem xét của lãnh đạo | QT 01 (gộp, lồng vào họp giao ban) | ✓ |
| 10. Cải tiến | NCR + CAR | QT 01 + BM.01.07 | ✓ |

---

## 4. Gap analysis — những thứ em thấy thiếu hoặc cần verify

1. **Truy xuất nguồn gốc (clause 8.3)** — ISO 22000:2018 yêu cầu rõ truy xuất xuôi (forward — lô SX → KH cuối) và ngược (backward — lô SX → NCC nguyên liệu). Chưa thấy QT riêng. Có thể đã ngầm hiểu trong QT 02 (Recall) hoặc QT 08 (SX) — em cần đọc 2 QT này để xác nhận.
2. **Quản lý đào tạo (clause 7.2)** — Chưa có BM training records. Đây là điểm yếu auditor hay gặt. Đề xuất bổ sung DocType `FSMS Training Record` link `Employee` + `Training Course`.
3. **Trao đổi thông tin (clause 7.4)** — Communication matrix với cơ quan QLNN, KH, NCC. Có thể gộp Sổ tay nhưng nên có form riêng để log communication.
4. **Quản lý dị ứng nguyên (allergen)** — Bánh đậu xanh, bột đậu không phải Big-8/9 allergen điển hình, nhưng nếu xuất khẩu hoặc gắn thêm topping (sữa, đậu phộng...) thì cần. Verify với HACCP plan.
5. **Validation PRP/CCP (clause 8.5.3)** — chưa thấy form validation riêng. Có thể đã gộp BM.04.01 (Kế hoạch thẩm tra).
6. **QT 06 và QT 08 không có BM trong zip** — em đoán chúng dùng ngay biểu mẫu từ các QT khác (ví dụ QT 06 dùng Sổ KT vệ sinh hoặc Sổ kiểm định thiết bị), hoặc BM bị thiếu. Cần verify với anh.
7. **Sổ kiểm tra vệ sinh công nhân — có 2 phiên bản** (.doc + .xlsx). Đề xuất chốt 1 bản chuẩn trước khi digitize.
8. **PCCC sub-folder** — không thuần ISO 22000. Đề xuất tách (giải thích ở Tier "Phụ" trên).
9. **Thiếu danh mục NCC, danh mục KH, danh mục lô SX** — những cái này dùng `Supplier`, `Customer`, `Batch` của ERPNext core, không cần tạo mới.

---

## 5. Summary statistics

```
Tổng file              : 52
Quy Trình (QT)         :  8
Biểu Mẫu (BM)          : 21
Phụ Lục (PL)           :  5
Hướng Dẫn (HD)         :  1
Quy Định (QĐ)          :  1
Kế hoạch HACCP         :  2  (+ 1 sơ đồ SX, + 1 sổ theo dõi thành phẩm)
PRP                    :  4
Foundation (manual+)   :  4
PCCC riêng             :  3
```

**ERPNext v16 core có thể tận dụng**:
- `Quality Procedure`, `Quality Action`, `Quality Review`, `Quality Goal`, `Quality Inspection`, `Quality Meeting`, `Quality Feedback`
- `Item`, `Batch` (cho HACCP + lưu mẫu + recall)
- `Supplier` + `Supplier Quotation` + `Supplier Scorecard` (cho QT 07)
- `Customer` (cho recall)
- `Employee`, `Department`, `Designation` (cho actor + permission)
- `Workflow` engine (cho NCR/CAR)
- `Print Format` (cho in biểu mẫu giống file Word hiện tại)

**DocType MỚI dự kiến phải tạo trong app `iso22000_fsms`** (preview, sẽ chi tiết ở `02_doctype_blueprint.md`):
- `FSMS Manual`, `FSMS Objective`, `FSMS Document Change Request`, `FSMS Document Register Internal`, `FSMS Document Register External`, `FSMS Records Register`
- `FSMS Audit Program`, `FSMS Audit Plan`, `FSMS Audit Checklist`, `FSMS Audit Observation`, `FSMS Audit Summary`
- `FSMS NCR / CAR` *(tâm điểm)*
- `FSMS Recall Plan`, `FSMS Recall Report`
- `FSMS Emergency Drill`, `FSMS Fire Equipment Log`, `FSMS Disease Log`, `FSMS Safety Equipment Inspection Log`
- `FSMS Verification Plan`, `FSMS Verification Report`
- `FSMS Interested Party`, `FSMS Risk Register`
- `HACCP Plan` + Child Table `HACCP CCP` + `HACCP Step` + `HACCP Hazard`
- `FSMS PRP Program`, `FSMS Sanitation Report`, `FSMS Worker Hygiene Log`
- `FSMS Sample Retention Log`
- *(thêm để lấp gap)* `FSMS Training Record`, `FSMS Communication Log`, `FSMS Traceability Record`

Sơ bộ: **~30 DocType mới** trên app `iso22000_fsms`, kế thừa core ERPNext Quality Module ở những chỗ phù hợp.

---

**End of `00_document_inventory.md` — chờ anh review.**
