---
title: "L21 — Dòng thời gian sự kiện"
description: "Tài liệu L21 — Dòng thời gian sự kiện trong agent-slide-studio."
document_type: layout
status: active
id: "L21"
---

# L21 — Dòng thời gian sự kiện

**Họ:** Quy trình. **Nguồn:** Đề xuất mở rộng của gói; tham khảo quan hệ tại S11–S12.

## Mục tiêu và khi sử dụng

4–6 mốc có thứ tự ngày hoặc giai đoạn rõ.

**Không nên / điều kiện giới hạn:** Không khoảng đều giả thời gian đều; ghi sơ đồ không theo tỷ lệ khi cần.

## Cấu trúc 16:9 và sơ đồ khung

Khung tham chiếu 1920×1080; x=100–1820, tiêu đề y=90–210; nội dung y=250–900.
Dành khoảng 24–32 px giữa vùng. Các khối quá dày phải tách trang, không giảm chữ.
Vùng tiêu đề, lề và khoảng trống lấy từ deck style lock. Phân chia vùng trong sơ đồ
chỉ mô tả topology, không phải số liệu hoặc tọa độ tỷ lệ nghiệp vụ.

```text
    [ B ]         [ D ]
──●───●───●───●──→
[ A ]     [ C ]
```

## Chữ, đường nối, màu và hình neo

Dùng 3–5 đơn vị chính khi phù hợp; trích dẫn chỉ một ý; cây tối đa 2–3 tầng cho tổng quan.
Mỗi khối một nhãn + tối đa hai ý ngắn, ngân sách toàn trang mặc định D1 35–70 đơn vị cách trắng; D2 71–100 chỉ dùng có chủ đích.
Không áp cứng số khối nếu làm mất bước thật. Thông tin bổ sung chuyển sang ghi chú giảng viên.

Đường có mũi tên biểu thị hướng, đường thường biểu thị liên hệ; không đường là nhóm độc lập.
Không khoảng đều giả thời gian đều; ghi sơ đồ không theo tỷ lệ khi cần.

Nếu chưa có style lock, navy, xanh dương, cam và icon phẳng hai tông chỉ là một ví dụ
khởi tạo để người dùng duyệt. Deck style lock luôn ghi đè ví dụ này; màu và bề mặt không được lấn quan hệ/nhãn.

## Prompt mẫu tiếng Việt

```text
Tạo infographic PowerPoint 16:9 theo L21 — Dòng thời gian sự kiện.
Mục tiêu: 4–6 mốc có thứ tự ngày hoặc giai đoạn rõ.
Sơ đồ theo các vùng đã khóa, lề tham chiếu trái/phải 100, trên 90, dưới 80 px
trong khung 1920×1080. Lấy nền, font appearance, palette, icon và bề mặt từ deck style lock.
Kiểm soát riêng: Không khoảng đều giả thời gian đều; ghi sơ đồ không theo tỷ lệ khi cần.
Chỉ hiển thị chuỗi trong CONTENT_LOCK đính kèm; giữ ngoại lệ tên riêng/cú pháp.
Không thêm tiếng Anh, số liệu, logo hay tuyên bố chức năng ngoài nội dung đã duyệt.
Không thu nhỏ chữ để nhét; nếu vượt ngân sách thì cần biên tập trước khi tạo ảnh.
Chỉ dùng direct text với native ImageGen; không chọn renderer mode hoặc fallback khác tại layout.
```

Điền biến bằng [mẫu prompt](../../../04-templates/slide-prompt.md), rồi preflight và gọi công cụ theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md).
Nếu brief yêu cầu hình không chữ, vẫn dùng native ImageGen và khóa rõ điều cấm ký tự; direct text là mặc định cho slide có chữ.

## Danh sách kiểm định riêng

- [ ] Không khoảng đều giả thời gian đều; ghi sơ đồ không theo tỷ lệ khi cần.
- [ ] Đủ khối/đúng quan hệ/đúng thứ tự và nhánh theo nguồn.
- [ ] Tiếng Việt chính xác; không sót chữ ngoài danh sách ngoại lệ.
- [ ] Lề, cỡ chữ, tương phản và vùng trống được kiểm tra trên ảnh thực.

[PNG xem trước](../../gallery/layouts/L21.png) · [SVG](../../gallery/layouts/L21.svg) · [Chỉ mục](../../INDEX.md).
