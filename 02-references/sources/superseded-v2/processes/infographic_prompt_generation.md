# 05 — Soạn prompt và tạo ảnh

**Đầu vào:** Bản chữ khóa, layout, mode, style và ảnh tham chiếu.

**Đầu ra:** image_prompt.md; ảnh thật khi công cụ hiện có và người dùng yêu cầu.

## Thực hiện

1. Điền mục tiêu, lề, vị trí khối, nghĩa đường nối, chất liệu và vùng trống vào mẫu prompt.

2. Tách hướng dẫn vẽ khỏi danh sách chữ chính xác. Với TITLE_RESERVED, y=0–240 trống; với NO_TEXT cấm mọi ký tự.

3. Không để placeholder chưa điền; không trộn --ar/--v hay tham số riêng của một công cụ vào tất cả nền tảng.

4. Khi yêu cầu tạo ảnh, gọi công cụ thật nếu có; khi chỉ soạn prompt, không tự sinh ảnh.

5. Với chữ/mã/số liệu cần chính xác và chỉnh sửa, tách hình minh họa khỏi lớp chữ, sau đó kiểm tra tệp thực.

## Giới hạn và điểm kiểm soát

Không có công cụ ảnh thì nói rõ và bàn giao prompt; không in tool arguments thay sản phẩm hoặc giả đã tạo ảnh.

[Quy trình tổng thể](README.md) · [Quy chuẩn](../references/design_system.md) · [Nguồn](../references/sources.md).
