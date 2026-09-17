---
title: "L20 — Minh họa hoặc nền không chữ"
description: "Tài liệu L20 — Minh họa hoặc nền không chữ trong agent-slide-studio."
document_type: layout
status: active
id: "L20"
---

# L20 — Minh họa hoặc nền không chữ

**Họ:** Minh họa. **Nguồn:** Kế thừa bản 20, bổ sung đặc tả v2.

## Mục tiêu và khi sử dụng

Ẩn dụ ở rìa, vùng trống lớn để chèn nội dung.

**Không nên / điều kiện giới hạn:** Cấm mọi chữ/số/ký tự, kể cả trên vật thể.

## Cấu trúc 16:9 và sơ đồ khung

Khung tham chiếu 1920×1080; giữ các vùng hình thuần thị giác trong safe margin của deck.
Dành khoảng 24–32 px giữa vùng; vùng trống và điểm nhấn lấy từ deck style lock. Phân chia vùng trong sơ đồ
chỉ mô tả topology, không phải số liệu hoặc tọa độ tỷ lệ nghiệp vụ.

```text
[ CHI TIẾT ] [ VÙNG TRỐNG ≥50% ] [ CHI TIẾT ]
```

## Chữ, đường nối, màu và hình neo

Density bắt buộc là `D0`: không nhãn, không title, không body, không chú thích và không footer trên ảnh.
Chỉ dùng hình học, ánh sáng, vật liệu, khoảng trắng và vật thể không mang ký tự. Mọi nội dung chữ nếu có
thuộc artifact khác ngoài ảnh L20; không đưa nó vào prompt ImageGen của layout này.

Đường có mũi tên biểu thị hướng, đường thường biểu thị liên hệ; không đường là nhóm độc lập.
Cấm mọi chữ/số/ký tự, kể cả trên vật thể.

Nếu chưa có style lock, navy, xanh dương, cam và icon phẳng hai tông chỉ là một ví dụ
khởi tạo để người dùng duyệt. Deck style lock luôn ghi đè ví dụ này; màu và bề mặt không được lấn quan hệ/nhãn.

## Prompt mẫu tiếng Việt

```text
Tạo infographic PowerPoint 16:9 theo L20 — Minh họa hoặc nền không chữ.
Mục tiêu: Ẩn dụ ở rìa, vùng trống lớn để chèn nội dung.
Sơ đồ theo các vùng đã khóa, lề tham chiếu trái/phải 100, trên 90, dưới 80 px
trong khung 1920×1080. Lấy nền, palette, vật liệu, icon không chữ và bề mặt từ deck style lock.
Kiểm soát riêng: Cấm mọi chữ/số/ký tự, kể cả trên vật thể.
Không render bất kỳ chữ cái, chữ số, nhãn, từ, glyph dạng ký hiệu được dùng như chữ, tên tệp,
logo chữ, watermark, ký hiệu lập trình, ký tự thật hoặc ký tự giả nào, kể cả trên vật thể,
màn hình, sách, nhãn và chi tiết trang trí.
Chỉ dùng `NATIVE_IMAGEGEN_NO_TEXT`; không chọn chính sách sinh chữ, renderer mode hoặc fallback khác tại layout.
```

Điền biến bằng [mẫu prompt](../../../04-templates/slide-prompt.md), rồi preflight và gọi công cụ theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md).
L20 luôn là hình không chữ: giữ toàn bộ điều cấm ký tự trong prompt và kiểm ảnh thật theo workflow canonical.

## Danh sách kiểm định riêng

- [ ] Cấm mọi chữ/số/ký tự, kể cả trên vật thể.
- [ ] Đủ khối/đúng quan hệ/đúng thứ tự và nhánh theo nguồn.
- [ ] Không có chữ cái, chữ số, nhãn, từ, glyph dạng ký hiệu được dùng như chữ hoặc bất kỳ ký tự thật/giả nào; không có ngoại lệ chữ hiển thị.
- [ ] Lề, tương phản thị giác, vùng trống và việc không có chữ được kiểm tra trên ảnh thực.

## Phần kế thừa từ bộ 20

**Dùng khi:** Tạo ẩn dụ, bìa, nền công nghệ hoặc hình neo riêng.

```text
[HẠT / SÓNG] → [VÙNG TRỐNG] → [CẤU TRÚC / CÔNG CỤ]
```

**Ràng buộc:** Không chữ, số, tên tệp hoặc ký hiệu lập trình; vùng nội dung trống 40–55% theo bố cục. Không bắt buộc có thẻ, số bước hoặc chân trang.

**Ví dụ:** Sóng ánh sáng chuyển thành cấu trúc thực thi; bộ não số ba tầng.

**Nguồn bố cục:** Mở rộng từ nhóm ảnh concept art và nền không chữ đã trao đổi.

[PNG xem trước](../../gallery/layouts/L20.png) · [SVG](../../gallery/layouts/L20.svg) · [Chỉ mục](../../INDEX.md).
