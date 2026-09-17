---
title: "Claude ImageGen integration"
description: "Tài liệu Claude ImageGen integration trong agent-slide-studio."
document_type: integration
status: active
---

# Claude ImageGen integration

1. Đọc `SKILL.md` và hoàn tất deck map, chọn L/I, mở ảnh mẫu thật, style lock và content lock trước khi gọi ảnh.
2. Chỉ dùng capability tạo/chỉnh ảnh native mà phiên Claude hiện tại thực sự công bố. Không suy diễn tên tool, model, API hoặc quyền từ tài liệu cũ.
3. Tạo slide neo trước; nếu host hỗ trợ reference, chỉ gửi đúng ảnh cần thiết. Edit phải dùng đúng ảnh đích.
4. Mở output đúng revision ở kích thước đầy đủ. Sửa lỗi QA bằng native edit; nếu chỉ có generation, regenerate từ prompt đã sửa. QA lại toàn ảnh và toàn deck.
5. Nếu không có capability ImageGen native cần thiết, trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt/content lock. Không dùng Python, HTML, SVG, browser/screenshot, PPTX overlay hoặc renderer thay thế.
6. Ghi host, capability thực dùng, tool/model nếu biết, prompt, reference, output path/handle, kích thước thật, revision và outcome. Không PASS khi ảnh chưa được xem đầy đủ.
