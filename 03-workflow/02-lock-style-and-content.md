---
title: "02 — Khóa style và nội dung"
description: "Tài liệu 02 — Khóa style và nội dung trong agent-slide-studio."
document_type: workflow
status: active
step: "2"
---

# 02 — Khóa style và nội dung

**Đầu vào:** deck plan đủ slide, nguồn, layout/ảnh đã mở.  
**Đầu ra:** style lock và content lock cho từng slide.

1. Khóa canvas, lề, title zone, font appearance, palette theo vai trò, surface, icon, connector, density và footer theo [design system](../01-design/design-system.md). Thiếu brand/font/style thì hỏi một lượt, trừ khi user đã cho phép tự chọn; không tự áp nhận diện AIA navy/xanh/cam.
2. Chọn một ảnh neo đạt chất lượng. Với mỗi reference, ghi file thực đã mở, đặc tính học và đặc tính cấm kế thừa. Không trộn sáu style thành collage.
3. Gán ID cho mọi chuỗi hiển thị. Khóa chính tả, dấu, tên riêng, cú pháp, số, đơn vị, node, cạnh, thứ tự và ngắt dòng được phép.
4. Mọi chữ nhìn thấy dùng tiếng Việt, trừ tên chính thức, tên tệp hoặc cú pháp đã khóa. Không tự thêm bản dịch tiếng Anh trong ngoặc.
5. Tách nguồn người dùng, bổ sung có nguồn, ví dụ giả định và đề xuất. Khi nguồn mâu thuẫn, ghi khác biệt và quyết định; không hòa giải âm thầm.
6. Với edit, mở đúng ảnh đích, mô tả vùng được sửa và vùng khóa; lưu revision mới. Không hứa giữ pixel ngoài vùng nếu công cụ không bảo đảm.
7. Chọn slide neo và khóa đầy đủ brief của nó: content lock, layout, style lock, reference scope, prompt constraints và tiêu chí QA. Bước này chưa gọi ImageGen và chưa tạo ảnh.

Không sang bước 03 nếu còn placeholder, chữ chưa khóa, reference chưa mở, brand decision chưa chốt hoặc nội dung không fit. Cách xử lý là biên tập có duyệt, đổi layout hoặc tách slide; không thu chữ hay bỏ ý âm thầm. Bước 03 là điểm duy nhất được generation.
