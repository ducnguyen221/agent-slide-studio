---
title: "Slide Planning and QA Templates"
description: "Reusable deck planning, slide prompt, generation record, review, and handoff templates."
document_type: project-template
status: active
---

# Slide Planning and QA Templates

Dùng đúng template theo giai đoạn: deck plan trước khi tạo ảnh, slide prompt trước mỗi lần generate/edit, review và handoff sau khi có ảnh.

---

## Template 01 — Deck plan

### Deck plan

#### Brief và style lock

- Tên deck / revision:
- Người xem / outcome:
- Thông điệp xuyên suốt:
- Nguồn và phần chưa đọc:
- Nhịp: P01 / P02 / P03 / P04 / P05 / P06 / custom:
- Canvas / lề / title zone:
- Brand, font appearance, palette, surface, icon, connector, footer:
- Slide neo / reference đã mở:
- Học từ reference:
- Không học từ reference:
- Quyết định còn thiếu:

#### Slide map

| Slide ID | Vai trò | Một thông điệp | Nguồn | Exact visible text / lock | Số & đơn vị | Topology | L/I | Density | Reference | QA state |
|---|---|---|---|---|---|---|---|---|---|---|
| S01 |  |  |  |  |  |  |  |  |  | draft |

#### Kiểm toàn deck

- [ ] 100% slide đã map, không ID trùng.
- [ ] Nguồn, thuật ngữ và số liệu nhất quán.
- [ ] Mạch bài chuyển hợp lý; không lặp layout vô thức.
- [ ] Mọi layout/reference đã được mở thật, không quyết định từ thumbnail.

---

## Template 02 — Slide prompt và generation record

### Slide prompt và generation record

#### Content lock

- Slide ID / revision:
- Nguồn:
- Objective / topology / L-I / density:
- Reference thực đã mở; học / không học:

| ID | Vai trò/vùng | Exact visible text | Số/đơn vị | Ngắt dòng cho phép | Căn cứ |
|---|---|---|---|---|---|
| T01 | Title |  |  |  |  |

Node/cạnh/thứ tự khóa:  
Vùng được sửa / vùng khóa:  
Nội dung cấm thêm:

#### Prompt thực

```text
CANVAS |
OBJECTIVE |
COMPOSITION |
STYLE |
CONTENT |
CONSTRAINTS |
NEGATIVE |
```

#### Generation record

- Host / tool / model nếu biết:
- Reference gửi vào:
- Call type: generate / edit
- Outcome: completed / CAPABILITY_UNAVAILABLE / OUTCOME_UNKNOWN / failed
- Output path/handle:
- Kích thước thật:
- Revision trước / thay đổi:
- Metadata chưa biết:

---

## Template 03 — Review và handoff

### Review và handoff

#### QA từng ảnh

- Slide ID / revision / artifact:
- Prompt và content lock:
- Canvas yêu cầu / canvas thật / cách đo:
- Ảnh đã mở ở kích thước đầy đủ: có / không

| Cổng | passed / failed / unverified | Bằng chứng hoặc lỗi/vị trí |
|---|---|---|
| Exact text, dấu, số, đơn vị |  |  |
| Node, cạnh, thứ tự, topology |  |  |
| Dimensions / ratio |  |  |
| Crop, overlap, safe margin |  |  |
| Khả năng đọc và phân cấp |  |  |
| Style lock / reference scope |  |  |
| Raster, font và editability claim |  |  |

- Kết luận: passed / needs_revision / unverified
- Repair cụ thể / revision tiếp theo:
- Alt text:

#### QA toàn deck

| Yếu tố | passed / failed / unverified | Bằng chứng / slide lệch |
|---|---|---|
| Canvas, lề, title/footer |  |  |
| Font appearance, palette, surface |  |  |
| Icon, card, connector |  |  |
| Nhịp, density, thuật ngữ |  |  |

#### Handoff

- Ảnh/prompt/content lock/generation record được giao:
- Cách mở và thứ tự file:
- Phần chưa kiểm:
- Giới hạn: ImageGen raster; font metadata/editability chỉ xác nhận khi có artifact tương ứng.
