---
title: "L15 — Cây phân cấp"
description: "Tài liệu L15 — Cây phân cấp trong agent-slide-studio."
document_type: layout
status: active
id: "L15"
---

# L15 — Cây phân cấp

**Họ:** Kiến trúc. **Nguồn:** Kế thừa bản 20, bổ sung đặc tả v2.

## Mục tiêu và khi sử dụng

Quan hệ cha–con 2–3 tầng; tối đa 7–9 nút cho tổng quan.

**Không nên / điều kiện giới hạn:** Không dùng cây cho mạng nhiều cha; cấp tên phải nhất quán.

## Cấu trúc 16:9 và sơ đồ khung

Khung tham chiếu 1920×1080; x=100–1820, tiêu đề y=90–210; nội dung y=250–900.
Dành khoảng 24–32 px giữa vùng. Các khối quá dày phải tách trang, không giảm chữ.
Vùng tiêu đề, lề và khoảng trống lấy từ deck style lock. Phân chia vùng trong sơ đồ
chỉ mô tả topology, không phải số liệu hoặc tọa độ tỷ lệ nghiệp vụ.

```text
        [ GỐC ]
      ┌────┴────┐
    [ A ]    [ B ]
   ┌─┴─┐      └[ C ]
```

## Chữ, đường nối, màu và hình neo

Dùng 3–5 đơn vị chính khi phù hợp; trích dẫn chỉ một ý; cây tối đa 2–3 tầng cho tổng quan.
Mỗi khối một nhãn + tối đa hai ý ngắn, ngân sách toàn trang mặc định D1 35–70 đơn vị cách trắng; D2 71–100 chỉ dùng có chủ đích.
Không áp cứng số khối nếu làm mất bước thật. Thông tin bổ sung chuyển sang ghi chú giảng viên.

Đường có mũi tên biểu thị hướng, đường thường biểu thị liên hệ; không đường là nhóm độc lập.
Không dùng cây cho mạng nhiều cha; cấp tên phải nhất quán.

Nếu chưa có style lock, navy, xanh dương, cam và icon phẳng hai tông chỉ là một ví dụ
khởi tạo để người dùng duyệt. Deck style lock luôn ghi đè ví dụ này; màu và bề mặt không được lấn quan hệ/nhãn.

## Prompt mẫu tiếng Việt

```text
Tạo infographic PowerPoint 16:9 theo L15 — Cây phân cấp.
Mục tiêu: Quan hệ cha–con 2–3 tầng; tối đa 7–9 nút cho tổng quan.
Sơ đồ theo các vùng đã khóa, lề tham chiếu trái/phải 100, trên 90, dưới 80 px
trong khung 1920×1080. Lấy nền, font appearance, palette, icon và bề mặt từ deck style lock.
Kiểm soát riêng: Không dùng cây cho mạng nhiều cha; cấp tên phải nhất quán.
Chỉ hiển thị chuỗi trong CONTENT_LOCK đính kèm; giữ ngoại lệ tên riêng/cú pháp.
Không thêm tiếng Anh, số liệu, logo hay tuyên bố chức năng ngoài nội dung đã duyệt.
Không thu nhỏ chữ để nhét; nếu vượt ngân sách thì cần biên tập trước khi tạo ảnh.
Chỉ dùng direct text với native ImageGen; không chọn renderer mode hoặc fallback khác tại layout.
```

Điền biến bằng [mẫu prompt](../../../04-templates/slide-prompt.md), rồi preflight và gọi công cụ theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md).
Nếu brief yêu cầu hình không chữ, vẫn dùng native ImageGen và khóa rõ điều cấm ký tự; direct text là mặc định cho slide có chữ.

## Danh sách kiểm định riêng

- [ ] Không dùng cây cho mạng nhiều cha; cấp tên phải nhất quán.
- [ ] Đủ khối/đúng quan hệ/đúng thứ tự và nhánh theo nguồn.
- [ ] Tiếng Việt chính xác; không sót chữ ngoài danh sách ngoại lệ.
- [ ] Lề, cỡ chữ, tương phản và vùng trống được kiểm tra trên ảnh thực.

## Phần kế thừa từ bộ 20

**Dùng khi:** Trình bày cấu trúc thư mục, vai trò hoặc nhóm tác nhân.

```text
          [GỐC]
        /   |   \
      [A]  [B]  [C]
```

**Ràng buộc:** Khoảng 2–3 cấp; dùng nhánh cho quan hệ chứa/thuộc, không dùng mũi tên thời gian. Không giả định mọi nhánh có cùng quyền hạn.

**Ví dụ:** Cấu trúc thư mục đầu vào, đầu ra và tài liệu tham chiếu.

**Nguồn bố cục:** Mở rộng từ khung tư duy và mẫu phân cấp AIA-102.

[PNG xem trước](../../gallery/layouts/L15.png) · [SVG](../../gallery/layouts/L15.svg) · [Chỉ mục](../../INDEX.md).
