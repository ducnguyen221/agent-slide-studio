---
title: "Review và handoff"
description: "Tài liệu Review và handoff trong agent-slide-studio."
document_type: template
status: active
---

# Review và handoff

## QA từng ảnh

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

## QA toàn deck

| Yếu tố | passed / failed / unverified | Bằng chứng / slide lệch |
|---|---|---|
| Canvas, lề, title/footer |  |  |
| Font appearance, palette, surface |  |  |
| Icon, card, connector |  |  |
| Nhịp, density, thuật ngữ |  |  |

## Handoff

- Ảnh/prompt/content lock/generation record được giao:
- Cách mở và thứ tự file:
- Phần chưa kiểm:
- Giới hạn: ImageGen raster; font metadata/editability chỉ xác nhận khi có artifact tương ứng.
