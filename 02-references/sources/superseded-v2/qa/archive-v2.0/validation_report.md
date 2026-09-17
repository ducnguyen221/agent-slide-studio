# Báo cáo kiểm tra gói phát hành 2.0.0

Ngày kiểm tra: **2026-09-17**. Bộ kỹ năng: **aia-slide-design**.

## Kết quả thực hiện

| Nhóm | Kết quả | Phạm vi |
|---|---|---|
| UTF-8 và YAML | PASS | 135 Markdown; 7 tệp có frontmatter đúng loại; 1 YAML metadata riêng |
| Header kỹ năng | PASS | name/description; tên khớp thư mục; không khóa trùng hoặc BOM |
| Liên kết cục bộ | PASS | Các liên kết Markdown và tài nguyên HTML được đối chiếu với tệp thực |
| Bố cục | PASS | L01–L36 không trùng; đủ đặc tả, PNG và SVG |
| Hình xem trước | PASS | 36 PNG 1600×900; 36 SVG; 3 bảng PNG3200×1800 đều16:9 |
| Nguồn lưu trữ | PASS | 24 bản Markdown gốc/lịch sử khớp SHA-256 trong source_inventory.json |
| Cài thử filesystem | PASS | 10 phép thử dry-run, project/user, backup, cấu hình nguyên vẹn và điều kiện từ chối |
| Thử lỗi validator | PASS | 6 phép thử YAML trùng, link hỏng, ID trùng, BOM/hash, tỷ lệ ảnh và phục hồi |
| Tệp loại trừ | PASS | Không DOCX, font, ZIP lồng, cache hoặc symlink |

Chi tiết máy đọc được: kết quả tĩnh (`static_validation.json`, đường dẫn tại v2.0) và 16 phép thử (`install_test_results.json`, đường dẫn tại v2.0).
Các con số files trong kết quả tĩnh được ghi trước khi thêm manifest.json và SHA256SUMS;
hai tệp danh mục tự loại khỏi payload để không tạo vòng lặp checksum.

## Phạm vi kiểm tra thị giác đã làm

Đã mở và xem ba bảng tổng hợp để rà cấu trúc của36 bố cục.
Đã xem riêng PNG L13 và L18 ở kích thước đầy đủ; chỉnh đường nối của L18 trước bản phát hành.
Đây là kiểm tra sơ đồ khung, không phải kiểm tra36 slide có nội dung hoàn chỉnh trên máy chiếu.
Các biểu đồ được ghi là minh họa; L20 không có phần tử chữ nhìn thấy.

## Đối chiếu nguồn

Có24 mục nguồn ngoài: 22 mục được truy cập, 2 mục có giới hạn truy cập.
Giới hạn được ghi riêng trong danh mục nguồn (`../references/sources.md`, đường dẫn tại v2.0), không nhận đã đọc nội dung bị chặn.
Không có report Deep Research hoàn tất được cung cấp; đây là đối chiếu web bổ sung trực tiếp.

## Chưa thực hiện — không diễn giải thành đã đạt

- Chưa chạy đăng nhập thật trên Codex, Claude Code và Google Antigravity.
- Chưa kiểm thử khả năng tự khám phá/gọi skill và hành vi model trên từng phiên bản ứng dụng.
- Chưa chạy36 bản slide nội dung trong PowerPoint hoặc Accessibility Checker.
- Không chứng nhận toàn bộ WCAG, độ chính xác tuyệt đối hoặc khả năng giữ từng pixel của image model.

Kịch bản cho bước này nằm ở runtime_smoke_tests (`runtime_smoke_tests.md`, đường dẫn tại v2.0) với trạng thái NOT_RUN.

## Môi trường công cụ kiểm tra

Python 3.13.5; PyYAML 6.0.3; Pillow 12.3.0; CairoSVG 2.8.2.
Dựng preview bằng SVG và raster hóa, không truy cập dịch vụ sinh ảnh, không phân phối font.

## Kiểm tra lại

```bash
python scripts/validate.py . --require-manifest
python scripts/test_package.py
```

Lệnh test thứ hai dùng thư mục tạm và chỉ in JSON; không sửa gói đã phát hành.
Muốn chỉnh kỹ năng, làm trên bản nguồn, kiểm tra rồi tạo lại manifest trước phát hành mới.
