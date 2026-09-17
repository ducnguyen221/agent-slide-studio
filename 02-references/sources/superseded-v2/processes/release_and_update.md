# 10 — Đóng gói và nâng cấp

**Đầu vào:** MD, registry, hình xem trước, adapter và phiên bản.

**Đầu ra:** ZIP, manifest, checksum và báo cáo kiểm tra.

## Thực hiện

1. Giữ SKILL.md nhỏ; tài liệu lớn đọc theo nhu cầu. Không đổi mã L01–L20 khi mở rộng.

2. Chạy validator để kiểm BOM, YAML, đường dẫn, mã trùng, hình đúng tỷ lệ và file cấm.

3. Cài thử vào thư mục tạm cho từng host; kiểm tra từ chối ghi đè và backup. Không sửa cấu hình thật của người dùng.

4. Ghi các kiểm tra đã làm và chưa làm; tạo manifest khi nội dung đã ổn định.

5. ZIP chỉ có thư mục aia-slide-design, không DOCX/font/cache/ZIP lồng. Kiểm tra CRC và checksum sau nén.

## Giới hạn và điểm kiểm soát

Bài học chỉ tạo đề xuất cập nhật; không tự sửa luật an toàn sau tác vụ thông thường.

[Quy trình tổng thể](README.md) · [Quy chuẩn](../references/design_system.md) · [Nguồn](../references/sources.md).
