---
title: "L10 — Đúc kết dạng lưới mô-đun"
description: "Tài liệu L10 — Đúc kết dạng lưới mô-đun trong agent-slide-studio."
document_type: layout
status: active
id: "L10"
---

# L10 — Đúc kết dạng lưới mô-đun

**Họ:** Đúc kết. **Nguồn:** Kế thừa bản 20, bổ sung đặc tả v2.

## Mục tiêu và khi sử dụng

Một ý chủ đạo, 2–3 ý hỗ trợ và điều kiện quan trọng.

**Không nên / điều kiện giới hạn:** Thẻ lớn là ý quan trọng nhất, không phải thẻ nhiều chữ nhất.

## Cấu trúc 16:9 và sơ đồ khung

Khung tham chiếu 1920×1080; x=100–1820, tiêu đề y=90–210; nội dung y=250–900.
Dành khoảng 24–32 px giữa vùng. Các khối quá dày phải tách trang, không giảm chữ.
Vùng tiêu đề, lề và khoảng trống lấy từ deck style lock. Phân chia vùng trong sơ đồ
chỉ mô tả topology, không phải số liệu hoặc tọa độ tỷ lệ nghiệp vụ.

```text
[ Ý CHÍNH LỚN ] [ Ý PHỤ A ]
[             ] [ Ý PHỤ B ]
[ ĐIỀU KIỆN / ĐÚC KẾT      ]
```

## Chữ, đường nối, màu và hình neo

Dùng 3–5 đơn vị chính khi phù hợp; trích dẫn chỉ một ý; cây tối đa 2–3 tầng cho tổng quan.
Mỗi khối một nhãn + tối đa hai ý ngắn, ngân sách toàn trang mặc định D1 35–70 đơn vị cách trắng; D2 71–100 chỉ dùng có chủ đích.
Không áp cứng số khối nếu làm mất bước thật. Thông tin bổ sung chuyển sang ghi chú giảng viên.

Đường có mũi tên biểu thị hướng, đường thường biểu thị liên hệ; không đường là nhóm độc lập.
Thẻ lớn là ý quan trọng nhất, không phải thẻ nhiều chữ nhất.

Nếu chưa có style lock, navy, xanh dương, cam và icon phẳng hai tông chỉ là một ví dụ
khởi tạo để người dùng duyệt. Deck style lock luôn ghi đè ví dụ này; màu và bề mặt không được lấn quan hệ/nhãn.

## Prompt mẫu tiếng Việt

```text
Tạo infographic PowerPoint 16:9 theo L10 — Đúc kết dạng lưới mô-đun.
Mục tiêu: Một ý chủ đạo, 2–3 ý hỗ trợ và điều kiện quan trọng.
Sơ đồ theo các vùng đã khóa, lề tham chiếu trái/phải 100, trên 90, dưới 80 px
trong khung 1920×1080. Lấy nền, font appearance, palette, icon và bề mặt từ deck style lock.
Kiểm soát riêng: Thẻ lớn là ý quan trọng nhất, không phải thẻ nhiều chữ nhất.
Chỉ hiển thị chuỗi trong CONTENT_LOCK đính kèm; giữ ngoại lệ tên riêng/cú pháp.
Không thêm tiếng Anh, số liệu, logo hay tuyên bố chức năng ngoài nội dung đã duyệt.
Không thu nhỏ chữ để nhét; nếu vượt ngân sách thì cần biên tập trước khi tạo ảnh.
Chỉ dùng direct text với native ImageGen; không chọn renderer mode hoặc fallback khác tại layout.
```

Điền biến bằng [mẫu prompt](../../../04-templates/slide-prompt.md), rồi preflight và gọi công cụ theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md).
Nếu brief yêu cầu hình không chữ, vẫn dùng native ImageGen và khóa rõ điều cấm ký tự; direct text là mặc định cho slide có chữ.

## Danh sách kiểm định riêng

- [ ] Thẻ lớn là ý quan trọng nhất, không phải thẻ nhiều chữ nhất.
- [ ] Đủ khối/đúng quan hệ/đúng thứ tự và nhánh theo nguồn.
- [ ] Tiếng Việt chính xác; không sót chữ ngoài danh sách ngoại lệ.
- [ ] Lề, cỡ chữ, tương phản và vùng trống được kiểm tra trên ảnh thực.

## Phần kế thừa từ bộ 20

**Dùng khi:** Tóm tắt các nguyên tắc không cùng mức quan trọng.

```text
[Ý CHÍNH LỚN      | Ý PHỤ 1]
[Ý PHỤ 2 | Ý PHỤ 3 | LƯU Ý]
```

**Ràng buộc:** Một thẻ lớn làm điểm neo; 2–3 thẻ nhỏ. Không chia tất cả thành các ô bằng nhau khi có một nguyên tắc chủ đạo.

**Ví dụ:** Bốn nguyên tắc dùng AI an toàn trong công việc.

**Nguồn bố cục:** Kế thừa Archetype 10, tài liệu 01.

[PNG xem trước](../../gallery/layouts/L10.png) · [SVG](../../gallery/layouts/L10.svg) · [Chỉ mục](../../INDEX.md).
