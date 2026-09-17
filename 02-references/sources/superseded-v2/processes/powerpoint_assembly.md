# 06 — Lắp vào PowerPoint

**Đầu vào:** Tài nguyên ảnh, text lock, mode, yêu cầu chỉnh sửa.

**Đầu ra:** powerpoint_handoff.md và PPTX chỉ khi được yêu cầu/có công cụ.

## Thực hiện

1. Đặt trang Widescreen 16:9. Kiểm tra kích thước ảnh thực, giữ tỷ lệ, không kéo méo.

2. FULL phủ trang không crop nội dung. TITLE_RESERVED giữ toàn ảnh và đặt tiêu đề trong vùng trống; không cắt rồi thu nhỏ lần nữa.

3. EDITABLE_OVERLAY dùng ảnh làm minh họa, chữ/mã/biểu đồ được dựng riêng; ghi lớp và tọa độ.

4. Chỉ gọi SmartArt gốc khi đó là đối tượng SmartArt thực. SVG/PNG hoặc các shape giống SmartArt không phải đối tượng ấy.

5. Thêm mô tả thay thế, tiêu đề trang, thứ tự đọc; xem Slide Show và Accessibility Checker trên ứng dụng thật khi có.

## Giới hạn và điểm kiểm soát

Không đổi đuôi ảnh thành PPTX. Ảnh đặt trong PPTX không tự tạo các thành phần chỉnh sửa riêng.

[Quy trình tổng thể](README.md) · [Quy chuẩn](../references/design_system.md) · [Nguồn](../references/sources.md).
