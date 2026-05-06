# 01 — Business Model

> **App**: ISO 22000 FSMS App for Công ty CP Hoàng Giang
> **Working name**: `iso22000_fsms` *(anh chốt lại)*
> **Phụ thuộc**: ERPNext v16, Frappe v16
> **Trạng thái**: Draft v0.1 — chờ anh duyệt trước khi sang `02_doctype_blueprint.md`

---

## 1. Bối cảnh nghiệp vụ

### 1.1 Doanh nghiệp

| Trường | Giá trị |
|--------|---------|
| Tên | Công ty Cổ phần Hoàng Giang |
| MST/ĐKKD | 0800280839 |
| Địa chỉ | Cụm Công nghiệp Khu 4, Phường Cẩm Thượng, TP. Hải Dương |
| Điện thoại | 02203.848.559 |
| Email | hoanggiavn.vn@gmail.com |
| Tiêu chuẩn áp dụng | **ISO 22000:2018** |
| Sản phẩm trong scope | Bánh đậu xanh, bột đậu xanh |
| Phạm vi địa điểm | 1 nhà máy duy nhất (Cẩm Thượng, Hải Dương) |
| Phạm vi tổ chức | Văn phòng + Bộ phận sản xuất + Phòng kinh doanh |

*(Trích Sổ tay ATTP)* — RVHG **đã** áp dụng FSMS theo ISO 22000:2018, có Sổ tay, Chính sách, Mục tiêu, 8 QT, 2 HACCP plan, hệ thống PRP, 21 biểu mẫu. App này **không thay thế** FSMS — app **digitize** việc quản lý tài liệu, ghi chép, theo dõi NCR/CAR, đánh giá nội bộ, monitoring CCP/PRP, lưu mẫu, thu hồi.

### 1.2 Lý do digitize

1. **Truy xuất nhanh** khi audit (BSI/SGS/BV ghé) — thay vì lục tủ giấy, search Frappe.
2. **Audit trail** tự động — version, ai sửa, ai duyệt, ai phát hành, ai đóng CAR.
3. **Báo cáo định kỳ** tự sinh — KPI ATTP, số CAR mở, số CAR đóng đúng hạn, số ngày CCP out-of-spec...
4. **Reminder** — đến hạn hiệu chuẩn thiết bị, đến hạn audit nội bộ, đến hạn review chính sách.
5. **Liên kết với ERPNext core**: lô SX (`Batch`) ↔ HACCP record ↔ Recall, NCC (`Supplier`) ↔ đánh giá NCC, KH (`Customer`) ↔ recall, NV (`Employee`) ↔ training, ↔ ký các phiếu.

---

## 2. Actors (vai trò trong hệ thống)

Trích sơ đồ tổ chức RVHG (QĐ 01/QĐ-HG ngày 12/05/2017) + Sổ tay ATTP:

| Code | Tên vai trò | Bộ phận | Quyền chính trong app |
|------|-------------|---------|------------------------|
| `GD` | Giám đốc | Top management | Phê duyệt cấp công ty (Sổ tay, Chính sách, Mục tiêu, CAR cấp cao), chair Họp xem xét lãnh đạo |
| `BAT_HEAD` | Trưởng Ban ATTP | Ban ATTP (cross-functional) | Phê duyệt tài liệu hệ thống, phát hành revision, lập KH đánh giá nội bộ, phê duyệt CAR thông thường |
| `BAT_MEMBER` | Thành viên Ban ATTP | Cross-functional | Tham gia đánh giá, soát xét tài liệu, ghi nhận điểm lưu ý |
| `TBP_KH` | Trưởng BP Kế hoạch–Tổng hợp | KH-TH | Quản lý hành chính tài liệu, chủ trì danh mục tài liệu nội bộ/bên ngoài |
| `TBP_SX` | Trưởng BP Quản lý–Sản xuất | Sản xuất | Phê duyệt CAR thuộc SX, ký monitoring CCP/PRP, chủ trì recall thực thi |
| `TBP_KT` | Trưởng BP Kế toán | Kế toán | Read-only nhiều phần, phê duyệt chi phí thu hồi |
| `TBP_KD` | Trưởng BP Kinh doanh | Kinh doanh | Xử lý phản hồi KH, khởi tạo recall, log communication với KH |
| `AUDITOR` | Chuyên gia đánh giá nội bộ | Cross-functional (NV được train) | Tạo audit plan, ghi finding, phát hành điểm lưu ý + CAR |
| `QC` | Cán bộ QC (vệ sinh + CCP + lưu mẫu) | Sản xuất / Ban ATTP | Ghi sổ vệ sinh hàng ngày, monitoring CCP, lưu mẫu sản phẩm |
| `NV` | Nhân viên (general) | Mọi BP | Đề xuất CAR, điền biểu mẫu thuộc phạm vi mình, đọc tài liệu được phân quyền |

**Lưu ý actor model:**
- Một nhân viên (`Employee`) có thể đảm nhận **nhiều role** đồng thời (ví dụ: Trưởng BP SX kiêm Auditor kiêm BAT_MEMBER).
- Mapping `Employee` ↔ `Role` chốt ở `03_permission_matrix.md`.
- Không tạo `User` riêng — dùng `Employee` link với `User` của Frappe.

---

## 3. Use cases (quy trình nghiệp vụ chính)

| # | Mã | Tên use case | Trigger | Output | DocType chính |
|---|-----|--------------|---------|--------|----------------|
| UC-01 | UC-DOC | Lifecycle tài liệu hệ thống (Document Control) | Yêu cầu sửa đổi BM.01.01 | Tài liệu được phát hành/thu hồi | `FSMS Document Change Request`, `FSMS Document Register Internal/External` |
| UC-02 | UC-AUDIT | Chương trình + chu kỳ đánh giá nội bộ | Lên kế hoạch hằng năm (BM.01.05) | Báo cáo tổng hợp KQ (BM.01.09) | `FSMS Audit Program`, `FSMS Audit Plan`, `FSMS Audit Checklist`, `FSMS Audit Observation`, `FSMS Audit Summary` |
| UC-03 | **UC-NCR** | **NCR + Hành động khắc phục — TÂM ĐIỂM** | Phát hiện sự không phù hợp (audit, complaint, CCP fail, vệ sinh fail, monitoring fail...) | CAR đóng + verify | `FSMS NCR / CAR` *(workflow 6 trạng thái — xem §4)* |
| UC-04 | UC-RECALL | Thu hồi sản phẩm | Sự cố ATTP / phản hồi KH / phát hiện lô lỗi | Báo cáo thu hồi (BM.02.02) | `FSMS Recall Plan`, `FSMS Recall Report` (link `Batch` của ERPNext) |
| UC-05 | UC-EMERGENCY | Ứng phó tình huống khẩn cấp | Sự kiện (bão lũ / cháy / mất điện / dịch / sản phẩm bị nhầm) | Biên bản xử lý + CAR (nếu có) | `FSMS Emergency Event`, `FSMS Fire Equipment Log` *(BM.03.01)*, `FSMS Disease Log` *(BM.03.02)*, `FSMS Safety Equipment Inspection` *(BM.03.03)* |
| UC-06 | UC-VERIFY | Thẩm tra hệ thống | Lập kế hoạch định kỳ (BM.04.01) | Báo cáo thẩm tra (BM.04.02) | `FSMS Verification Plan`, `FSMS Verification Report` |
| UC-07 | UC-CONTEXT | Xác định bên quan tâm + rủi ro *(clause 4)* | Định kỳ review (hằng năm hoặc khi có thay đổi lớn) | Bảng cập nhật | `FSMS Interested Party` (BM.05.01), `FSMS Risk Register` (BM.05.02) |
| UC-08 | UC-EQUIP | Quản lý thiết bị SX + thiết bị đo *(clause 7.1.5)* | Đến hạn hiệu chuẩn / kiểm định | Hồ sơ hiệu chuẩn | DocType `FSMS Equipment` (link `Asset` ERPNext) — **chi tiết cần đọc QT 06** |
| UC-09 | UC-SUPPLIER | Đánh giá lựa chọn NCC | Định kỳ + khi có NCC mới | Phiếu đánh giá NCC (BM.07.01), Danh sách NCC duyệt (BM.07.02) | Mở rộng `Supplier Scorecard` (ERPNext) + DocType `FSMS Supplier Evaluation`, `FSMS Material Inspection Log` (BM.07.03) |
| UC-10 | UC-PROD | Quản lý sản xuất *(QT 08)* | Mỗi lô SX | Hồ sơ lô | **Phụ thuộc đọc QT 08** — có thể chỉ link với `Work Order` + `Batch` ERPNext, không tạo DocType mới |
| UC-11 | UC-PRP | PRP — vệ sinh hàng ngày + báo cáo | Ca SX hằng ngày | Sổ KT vệ sinh CN, báo cáo vệ sinh | `FSMS PRP Program`, `FSMS Worker Hygiene Log`, `FSMS Sanitation Report` |
| UC-12 | UC-SAMPLE | Lưu mẫu sản phẩm | Mỗi lô SX | Sổ lưu mẫu | `FSMS Sample Retention Log` (link `Batch`) |
| UC-13 | UC-HACCP | HACCP plan + monitoring CCP | Khi cập nhật plan + mỗi ca SX (monitoring) | Plan + sổ theo dõi thành phẩm | `HACCP Plan` + Child Table `HACCP CCP`, `HACCP Hazard`, `HACCP Step` + DocType `FSMS Finished Product Inspection` |
| UC-14 | UC-MR | Họp xem xét của lãnh đạo *(clause 9.3)* | Định kỳ (lồng ghép họp giao ban hoặc cuối năm) | Biên bản + CAR phát sinh | Mở rộng `Quality Meeting` (ERPNext) |
| UC-15 | UC-MGT-DOC | Quản lý các tài liệu mẹ (Sổ tay, Chính sách, Mục tiêu) | Khi cần update | Phiên bản mới ban hành | `FSMS Manual` (Single), `FSMS Objective` (multi-record có version) |

### Use cases gap-filler (em đề xuất bổ sung — anh chốt)

| # | Mã | Tên | Lý do |
|---|-----|-----|-------|
| UC-16 | UC-TRAINING | Quản lý đào tạo nhân viên ATTP | Clause 7.2 — auditor hay hỏi, chưa có trong tài liệu zip |
| UC-17 | UC-COMM | Log trao đổi thông tin nội bộ + bên ngoài | Clause 7.4 — chưa có trong tài liệu zip |
| UC-18 | UC-TRACE | Truy xuất nguồn gốc 2 chiều | Clause 8.3 — chưa thấy QT riêng, có thể đã ngầm trong QT 02/QT 08, em sẽ verify khi đọc |

---

## 4. Workflow tâm điểm — NCR / CAR (UC-03)

Trích trực tiếp từ biểu mẫu **BM.01.07 Phiếu yêu cầu hành động khắc phục** (cấu trúc 4 phần trên giấy):

| Phần trên phiếu giấy | Frappe state |
|----------------------|---------------|
| 1. Nội dung đề xuất hành động (Hồ sơ kèm theo số:…) | `Đề xuất` (Draft) |
| 2. Phân tích nguyên nhân, biện pháp đề xuất | `Phân tích` (Pending Analysis) |
| 3. Phê duyệt (Trưởng ban ISO/Trưởng bộ phận) | `Chờ phê duyệt` (Pending Approval) |
| (thực thi) | `Đang thực hiện` (In Progress) |
| 4. Đánh giá kết quả & xác nhận hoàn thành | `Đang xác minh` (Verification) |
| Nếu đạt → đóng | `Đã đóng` (Closed) |
| Nếu không đạt → "chuyển thực hiện tiếp ngày... / Số phiếu yêu cầu mới..." | `Chuyển tiếp` (Reissued) — link sang phiếu mới |

→ State machine 7 trạng thái: `Đề xuất → Phân tích → Chờ phê duyệt → Đang thực hiện → Đang xác minh → (Đã đóng | Chuyển tiếp)`. Chi tiết hành động + role transition viết trong `04_workflow_blueprint.md`.

**Trigger source của NCR**:
- Audit observation (UC-02)
- Customer complaint (UC-RECALL)
- CCP out-of-spec (UC-13)
- PRP fail (UC-11)
- Supplier rejection (UC-09)
- Equipment calibration fail (UC-08)
- Manual report (bất kỳ NV nào đề xuất)

→ Mọi DocType có khả năng phát sinh NCR đều có button "Tạo CAR" (Frappe `make_method`).

---

## 5. Out of scope (chốt loại trừ)

1. Hồ sơ pháp lý PCCC chuyên biệt (3 file trong sub-folder `Phương án PCCC`) — đề xuất tách app riêng hoặc giữ raw file đính kèm. Không ép vào schema FSMS.
2. Tiêu chuẩn QCVN, giấy phép kinh doanh — không quản schema, chỉ link/attach.
3. Hồ sơ nhân sự ngoài training-related ATTP — dùng HRMS module sẵn có.
4. Quản lý kho thành phẩm + xuất hàng — dùng ERPNext core.
5. Tích hợp eInvoice/eContract — không liên quan FSMS.

---

## 6. Quyết định cần anh chốt trước khi sang `02_doctype_blueprint.md`

| # | Câu hỏi | Em đề xuất default |
|---|---------|----------------------|
| Q1 | Tên app cuối cùng | `iso22000_fsms` (đơn giản, không gắn brand) — hoặc `hg_fsms` nếu muốn brand RVHG |
| Q2 | Scope MVP — digitize TẤT CẢ 13 (15) UC trong 1 release, hay chia phase? | **Phase MVP**: UC-01 (Doc), UC-02 (Audit), UC-03 (NCR/CAR), UC-12 (Lưu mẫu), UC-15 (Sổ tay/CS/MT). Phase 2: HACCP + PRP + monitoring. Phase 3: Recall + Emergency + Supplier + Equipment. Lý do: NCR/CAR là tâm + dễ thấy giá trị nhanh. |
| Q3 | Có bổ sung 3 UC gap-filler (Training, Communication, Traceability)? | **Có**, ít nhất Training (clause 7.2 chắc chắn cần) và Traceability (clause 8.3) — Communication có thể delay. |
| Q4 | Tích hợp ERPNext core — confirm các link sau? | `Item` ↔ HACCP Plan ↔ Sample Retention; `Batch` ↔ HACCP record ↔ Recall ↔ Sample; `Supplier` ↔ QT 07; `Customer` ↔ Recall + Communication; `Employee` ↔ Training + ký phiếu; `Asset` ↔ Equipment (UC-08) |
| Q5 | Mục tiêu certification | Duy trì ISO 22000:2018 hiện tại + audit hằng năm? Có dự định thêm BRC, IFS, FSSC 22000 trong tương lai không? Cái này ảnh hưởng độ "chặt" của workflow + audit trail. |
| Q6 | Multi-language | Chỉ tiếng Việt, hay cần song ngữ Việt-Anh (cho auditor quốc tế)? |
| Q7 | Print Format | Có cần in biểu mẫu **giống hệt** layout file Word hiện tại (để CN ký giấy như cũ), hay accept layout Frappe chuẩn? |

---

## 7. Trạng thái + bước tiếp theo

- **Đã hoàn thành**: 00 inventory + 01 business model
- **Đang chờ**: Anh trả lời Q1–Q7 ở §6
- **Sau khi duyệt 01**: Em sang `02_doctype_blueprint.md` — chi tiết toàn bộ DocType + field + naming series + relationship
- **Em sẽ KHÔNG** đụng tới code app cho đến khi qua hết 01–06 và anh approve `06_fixtures_plan.md`

---

**End of `01_business_model.md` — chờ anh review.**
