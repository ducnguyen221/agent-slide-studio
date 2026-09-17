---
title: "Codex ImageGen adapter"
description: "Tài liệu Codex ImageGen adapter trong agent-slide-studio."
document_type: integration
status: active
---

# Codex ImageGen adapter

1. Đọc `SKILL.md` và hoàn tất deck map, chọn L/I, mở ảnh mẫu thật, style lock và content lock trước khi gọi ảnh.
2. Dùng capability tạo/chỉnh ảnh native đang được phiên Codex hiện tại cung cấp. Chỉ ghi tool/model khi host công bố; nếu không biết, ghi `unknown`. Không suy diễn tên tool, model hoặc API từ tài liệu cũ.
3. Tạo slide neo trước. Nếu host hỗ trợ reference, chỉ gửi đúng ảnh cần thiết; edit phải dùng đúng ảnh đích.
4. Mở output đúng revision ở kích thước đầy đủ. Repair lỗi QA bằng native edit; nếu edit không có nhưng generation có, regenerate từ prompt đã sửa. QA lại toàn ảnh và toàn deck.
5. Nếu không có capability ImageGen native cần thiết, trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt/content lock. Không dùng Python, HTML, SVG, browser/screenshot, PPTX overlay hoặc renderer thay thế.
6. Ghi host, capability thực dùng, tool/model nếu biết, prompt, reference, output path/handle, kích thước thật, revision và outcome. Không PASS khi ảnh chưa được xem đầy đủ.
