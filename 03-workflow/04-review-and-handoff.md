---
title: "04 — Review ảnh thật và bàn giao"
description: "Tài liệu 04 — Review ảnh thật và bàn giao trong agent-slide-studio."
document_type: workflow
status: active
step: "4"
---

# 04 — Review ảnh thật và bàn giao

**Đầu vào:** ảnh đúng revision, prompt, deck plan, style/content lock.  
**Đầu ra:** [review-and-handoff](../04-templates/review-and-handoff.md) với `passed`, `needs_revision` hoặc `unverified`.

1. Đọc metadata file để ghi width×height thật; phân biệt exact size với exact ratio.
2. Mở toàn ảnh ở kích thước đầy đủ. Kiểm điểm nhìn, thứ tự đọc, phân cấp, khoảng trắng, style lock và vai màu.
3. So từng chuỗi với content lock: dấu tiếng Việt, chữ hoa, dấu câu, tên riêng, số, đơn vị và ngắt dòng. Một ký tự sai là lỗi.
4. Kiểm node, cạnh, thứ tự, nhánh và topology; cycle phải khép kín, mũi tên không xuyên chữ.
5. Kiểm crop, overlap, safe margin, title/footer, độ đọc khi trình chiếu và chi tiết giả chữ/watermark/logo.
6. Kiểm consistency toàn deck: canvas, title alignment, palette, font appearance, icon/material, card radius, connector và density.
7. Sửa theo thứ tự: nghĩa/nội dung → chữ/số → topology → crop/lề/độ đọc → style/trang trí. Mỗi edit phải QA lại.

`passed` chỉ khi mọi cổng bắt buộc có bằng chứng. Lỗi cụ thể là `needs_revision`; thiếu ảnh, vision hoặc số đo là `unverified`. Prompt/tool success/tên file không thay bằng chứng nhìn ảnh. Raster không chứng minh font metadata hoặc editability; nếu user yêu cầu exact font family/point size, ghi giới hạn ImageGen-only.

Bàn giao gồm ảnh đúng revision, prompt thực, content lock, generation record, QA từng slide, QA toàn deck, alt text, phần chưa kiểm và cách mở artifact. Chỉ tạo PowerPoint khi được giao riêng; ảnh đặt vào PPTX vẫn là raster.
