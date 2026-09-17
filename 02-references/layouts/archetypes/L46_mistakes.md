---
title: "L46 — Ba lỗi và cách sửa"
description: "Tài liệu L46 — Ba lỗi và cách sửa trong agent-slide-studio."
document_type: layout
status: active
id: "L46"
---

# L46 — Ba lỗi và cách sửa

**Trạng thái:** Bố cục mới do bộ thiết kế đề xuất trong v2.1.0; không phải mẫu có sẵn của PowerPoint.

## Mục đích và giới hạn

Ba cặp lỗi–cách sửa theo cùng hàng để hỗ trợ tự kiểm tra.

**Không nên / kiểm soát:** Phê bình thao tác, không gán nhãn xấu cho người học.

## Cấu trúc tham chiếu

16:9; khung 1920 × 1080; lề trái/phải 100 px, trên 90 px, dưới 80 px.
Chữ chính theo mục tiêu 20–24 pt khi dàn PowerPoint. Không co chữ để nhét thêm nội dung.

```text
[Lỗi 1] → [Cách sửa 1]
[Lỗi 2] → [Cách sửa 2]
[Lỗi 3] → [Cách sửa 3]
```

Một quan hệ chính, 3–4 vùng nhận thức. Tiêu đề tối đa hai dòng. Tài liệu giải thích đưa ra ghi chú.
Ngân sách mật độ là quy ước biên tập của gói, không phải định luật nhận thức.

## Prompt mẫu

```text
Thiết kế slide 16:9 tiếng Việt theo L46 — Ba lỗi và cách sửa.
Mục tiêu: Ba cặp lỗi–cách sửa theo cùng hàng để hỗ trợ tự kiểm tra.
Nếu chưa có style lock, nền trắng, chữ navy và một màu nhấn chỉ là ví dụ khởi tạo;
deck style lock luôn ghi đè palette, font appearance, icon và bề mặt của ví dụ.
Bố trí theo sơ đồ khung đã chọn. Lề an toàn rộng; chỉ hiển thị CONTENT_LOCK đã duyệt.
Phê bình thao tác, không gán nhãn xấu cho người học.
Không thêm số liệu, logo, chữ tiếng Anh hoặc lời hứa ngoài nội dung nguồn.
```

Prompt thực phải được biên soạn thành bảy phần và gọi native ImageGen theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md); layout không chọn renderer mode.

## Kiểm định

- [ ] Một thông điệp chính, nhãn rõ và không vượt lề.
- [ ] Phê bình thao tác, không gán nhãn xấu cho người học.
- [ ] Đọc được nhãn khi mở ảnh ở kích thước trình chiếu, không chỉ khi phóng to.
- [ ] Ví dụ được nhận diện; nội dung chuyên môn không được tự thêm.

[Xem PNG](../../gallery/layouts/L46.png) · [Xem SVG](../../gallery/layouts/L46.svg) · [Danh mục phân loại](../../INDEX.md)
