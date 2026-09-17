# 04 — Khóa nội dung và phạm vi sửa

**Đầu vào:** Bản chữ, tên riêng, nguồn, ảnh đích đang truy cập được.

**Đầu ra:** content_lock.md có phiên bản; edit_request.md nếu sửa ảnh.

## Thực hiện

1. Liệt kê mọi chuỗi sẽ hiện trên hình theo ID T01/C01/A01; ghi tên riêng và dữ liệu giữ nguyên.

2. Ghi vùng được thay đổi và vùng khóa. Khi có ảnh, mô tả hộp x/y/w/h tương đối; không đo một ảnh không tồn tại trong phiên.

3. Chữ nguyên văn do người dùng cung cấp có thể là bản khóa; không bắt duyệt lại nếu mục tiêu rõ.

4. Chỉ sửa phần được yêu cầu, lưu thành bản mới, không ghi đè gốc.

5. Nếu cần giữ chính xác ngoài vùng sửa, ưu tiên overlay hoặc chỉnh vùng có kiểm soát; không hứa từng pixel khi tái sinh toàn ảnh.

## Giới hạn và điểm kiểm soát

Thiếu ảnh đích thì xin ảnh; không sửa một tên ảnh hoặc ID opaque không mở được.

[Quy trình tổng thể](README.md) · [Quy chuẩn](../references/design_system.md) · [Nguồn](../references/sources.md).
