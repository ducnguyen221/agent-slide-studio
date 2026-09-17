---
title: Distill Private Style References
status: documentation_only
updated: 2026-09-15
---

# Nhập ảnh mẫu riêng và chắt thành profile

Quy trình này dùng khi người sở hữu cho phép đọc một project/chat cụ thể để tái sử dụng phong cách. Mục tiêu là lưu nguyên bản ở station riêng, chọn rất ít mẫu tốt và tạo profile gọn cho agent; không sao chép transcript hay ảnh riêng vào repo công khai.

## Cấu trúc đích

```text
$PRESENTATION_HOME/style-references/chatgpt-library/
├── originals/<chat-slug>/
├── selected/gold/
├── selected/supporting/
├── profiles/
└── manifests/
```

`$PRESENTATION_HOME` mặc định theo convention là `~/.presentation`; caller vẫn phải truyền đường thực khi CLI/runtime chưa tự đọc biến này. `originals/` giữ byte gốc đã lấy; `selected/` là bộ nhỏ dùng thường xuyên; `profiles/` nối style ID với file riêng; `manifests/` giữ nguồn, kích thước, hash, quyết định chọn/loại và quyền sử dụng.

## Quy trình chín bước

1. **Khóa phạm vi.** Ghi project/chat được phép đọc và mục đích dùng nội bộ. Không mở chat ngoài phạm vi, secret hoặc cây cloud placeholder.
2. **Lọc theo tên.** Ưu tiên title có `infographic`, `presentation`, `slide`, `sơ đồ`, `quy trình`; title chỉ là tín hiệu, không là bằng chứng chất lượng.
3. **Thu ảnh ứng viên.** Lấy ảnh thật từ chính chat/library qua công cụ đang đăng nhập; không dùng screenshot thu nhỏ nếu có file gốc. Không tự gửi dữ liệu ra ngoài.
4. **Sàng nhanh.** Loại chân dung cá nhân, banner marketing, logo rời, ảnh không phải slide, bảng/code thuần, ảnh lỗi crop, chữ hỏng rõ hoặc độ phân giải quá thấp.
5. **Xem và đối chiếu.** Mở toàn ảnh; đo width×height, tỷ lệ, bytes và SHA-256. So bố cục, lề, khoảng trắng, phân cấp, icon, màu, chính tả và khả năng đọc ở kích thước slide.
6. **Xếp hạng.** `gold` khi có thể làm chuẩn chính; `supporting` khi chỉ nên học một đặc tính; `rejected` khi không nên đưa vào generation. Chỉ giữ 1–2 ảnh chính cho một style.
7. **Lưu private.** Copy byte gốc vào `originals/`, bản được chọn vào `selected/`, rồi kiểm hash nguồn=đích. Không commit ảnh chat riêng.
8. **Chắt profile.** Dùng [style card template](../references/style-library/style-card-template.md) để mô tả geometry, spacing, palette, density, icon language, content ceiling, token gọn và lỗi cần tránh. Loại tên riêng, dữ liệu nghiệp vụ, câu chữ và dấu hiệu nhận diện không cần thiết.
9. **Kiểm và bàn giao.** Chạy [style fidelity cases](../evals/style-fidelity-cases.md), kiểm liên kết gói skill và ghi rõ ảnh nào private, ảnh nào có quyền public. Generation sau chỉ nạp profile cùng tối đa hai reference đã chọn.

## Cổng chất lượng

- Chọn theo chất lượng slide, không theo việc ảnh “đẹp” riêng lẻ.
- Tỷ lệ gần 16:9 không được khai exact-size; luôn ghi kích thước thật.
- Một lỗi chính tả không làm ảnh vô dụng cho style, nhưng hạ cấp và cấm lấy câu chữ làm chuẩn.
- `gold` không đồng nghĩa có quyền tái phân phối. Quyền nội bộ và quyền public là hai trường độc lập.
- Không giữ ảnh loại chỉ để “đủ bộ”. Manifest có thể ghi lý do loại mà không cần copy binary.
