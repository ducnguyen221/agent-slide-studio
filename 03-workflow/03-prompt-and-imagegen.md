---
title: "03 — Soạn prompt và gọi ImageGen"
description: "Tài liệu 03 — Soạn prompt và gọi ImageGen trong agent-slide-studio."
document_type: workflow
status: active
step: "3"
---

# 03 — Soạn prompt và gọi ImageGen

**Đầu vào:** deck plan, style lock, content lock và ảnh tham chiếu đã mở.  
**Đầu ra:** prompt tự đủ nghĩa, generation record và ảnh thật hoặc trạng thái fail-closed.

## Prompt bảy phần

Mỗi prompt có đúng thứ tự sau; nội dung chỉ xuất hiện một lần:

```text
CANVAS | kích thước/tỷ lệ; safe margins; nền; title zone.
OBJECTIVE | một câu về thông điệp, người xem và vai trò slide.
COMPOSITION | vùng, topology, thứ tự đọc, node/cạnh và điểm nhấn.
STYLE | style lock, font appearance, palette, icon, material.
CONTENT | ID + exact visible text, số, đơn vị và ngắt dòng cho phép.
CONSTRAINTS | bất biến, reference scope, số node/cạnh, vùng khóa.
NEGATIVE | lỗi thị giác/nội dung phải tránh, không lặp phần trên.
```

Prompt phải tự đủ nghĩa; ImageGen không thể đọc repo hoặc bảng ngoài prompt. ID là chỉ dẫn, không được in trừ khi nó là visible text. Direct text là mặc định theo hợp đồng ImageGen-only. Nếu lượng chữ không thể đọc được, đề xuất biên tập/tách slide trước khi gọi; không tự chuyển sang overlay, Python, SVG, HTML, screenshot hoặc renderer khác.

## Gọi và ghi nhận

1. Kiểm tool native của host, quyền dùng reference và phạm vi task. Không hardcode model/API không được host công bố.
2. Chạy preflight cho slide neo đã khóa ở bước 02: prompt đủ bảy phần, không placeholder, content/style/reference lock đầy đủ, tool/capability và outcome trước đó rõ ràng.
3. Tại đây, gọi ImageGen đúng một lần đầu tiên cho slide neo. Mở ảnh neo thật và QA theo [bước 04](04-review-and-handoff.md); chỉ khi ảnh neo đạt mới dùng nó làm style reference nếu tool hỗ trợ.
4. Sau anchor gate, gọi ImageGen cho từng slide phụ thuộc với prompt đã khóa. Tạo mới không đính kèm reference không cần thiết; edit phải truyền đúng ảnh đích.
5. Ghi slide ID, revision, host, tool/model nếu biết, prompt thực, reference, output path/handle, kích thước thật và outcome. Trường thiếu ghi `unknown`.
6. Timeout/chưa rõ kết quả trả `OUTCOME_UNKNOWN`; kiểm cùng tác vụ nếu host cho phép, không gửi lại mù. Thiếu capability trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt, không fallback renderer.
7. Mọi repair phải gắn lỗi QA cụ thể, tạo revision mới và QA lại toàn ảnh.
