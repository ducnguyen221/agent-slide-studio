# Kiểm định v2.1.0 — danh mục phân loại và infographic

Ngày kiểm tra: **2026-09-17**. Phạm vi: gói tệp cục bộ và trình xem mẫu. Không phải chứng nhận tương thích hành vi của mô hình hoặc đăng nhập thực tế Codex/Claude Code/Antigravity.

## Kết quả đã thực hiện

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| YAML/frontmatter, UTF-8, liên kết cục bộ | PASS | [Kết quả tĩnh](static_validation.json) |
| Đủ L01–L48, I01–I12; mỗi mã một nhóm chính | PASS | [registry L](../archetypes/registry.json), [registry I](../infographics/registry.json), [groups](../taxonomy/groups.json) |
| 10 bảng nhóm, mỗi bảng sáu mẫu; ảnh PNG/SVG 16:9 | PASS | Bộ kiểm tra tĩnh |
| Mã/tên/tệp/pattern L01–L36 giữ nguyên | PASS | [Migration](migration_check.json) |
| 72 ảnh PNG/SVG cũ giữ nguyên byte | PASS | [Migration](migration_check.json) |
| Bảy ảnh tham chiếu mới giữ nguyên byte | PASS | [Sổ ảnh](../references/user-infographics/registry.json) |
| 16 phép thử cài đặt tạm và phát hiện lỗi có chủ đích | PASS | [Kết quả](install_test_results.json) |
| 8 phép thử lọc nhóm/mã/quan hệ trong JavaScript/DOM | PASS | [Kết quả](gallery_test_results.json) |
| Số chữ hiển thị trong 12 infographic | 32–51 đơn vị cách trắng | [Đếm từ SVG](illustrated_text_counts.json) |

## Kiểm tra thị giác

Đã mở và xem các bảng G09A, G09B (đủ 12 mẫu minh họa), G05 và G08 để đối chiếu hình, mã, số lượng mẫu và vị trí chữ. Đã loại bỏ hai phần chữ đúc kết trùng trên I07/I08. Các hình L01–L36 được giữ nguyên từ gói đã cung cấp; không tuyên bố đã tái duyệt mọi chi tiết cũ.

Đếm chữ loại trừ kicker thư viện, mã lặp lại ở chân và huy hiệu số. Đây không phải phép đếm token mô hình hoặc số từ ngôn ngữ học. Nhãn, tiêu đề và câu mẫu đều được tính. Không dùng số đếm này thay việc thử trên màn chiếu thực.

## Phạm vi chưa kiểm chứng

Trình duyệt trong môi trường thử chặn điều hướng file://. Vì vậy đã kiểm thử JavaScript/DOM bằng nội dung HTML được nạp trực tiếp; đường dẫn hình được kiểm tra tồn tại bằng bộ kiểm tra tĩnh. Chưa xác nhận mở file:// trên trình duyệt của người dùng. Trang không dùng fetch, phông ngoài hay thư viện mạng.

Không chạy đăng nhập vào ba ứng dụng host. Adapter/frontmatter được kế thừa; sửa đổi v2.1 tập trung vào danh mục, quy trình chọn mẫu và ảnh xem trước.

## Tính toàn vẹn

Manifest và SHA256SUMS được tạo sau khi hoàn thành báo cáo. Chạy kiểm tra cuối bằng:

```bash
python scripts/validate.py . --require-manifest
```

Không ghi báo cáo vào bên trong gói sau khi tạo manifest nếu chưa tạo lại checksum. Kết quả v2.0 được giữ tại qa/archive-v2.0 để đối chiếu lịch sử, không phải kết quả của bản hiện tại.
