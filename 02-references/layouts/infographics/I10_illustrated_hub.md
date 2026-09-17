---
title: "I10 — Lõi và ba hệ thống hỗ trợ"
description: "Tài liệu I10 — Lõi và ba hệ thống hỗ trợ trong agent-slide-studio."
document_type: infographic
status: active
id: "I10"
---

# I10 — Lõi và ba hệ thống hỗ trợ

**Loại:** Mẫu infographic minh họa hoàn chỉnh với nội dung ví dụ, không chỉ khung SmartArt.
**Cấu trúc nền:** L11. **Nhóm:** G09B.
**Nguồn thị giác:** R03 trong [sổ ảnh tham chiếu](../../INDEX.md).

## Ý đồ

Lõi hình minh họa ở tâm, ba khối lập kế hoạch, tri thức, công cụ nối có nhãn.

Đây là đề xuất thiết kế mới; ảnh nguồn được học về cách dùng icon, khối và khoảng cách.
Không kế thừa các tỷ lệ tự chủ, cam kết tuyệt đối hoặc tên giao diện như dữ kiện đã xác minh.

## Chữ mẫu đã khóa

**Tiêu đề:** Lõi và ba hệ thống hỗ trợ

| Thành phần | Chữ trong thẻ |
|---|---|
| Lập kế hoạch | Chia nhiệm vụ |
| Tri thức | Tra cứu nguồn |
| Công cụ | Thực hiện thao tác |

**Thông điệp phụ/tâm:** Lõi AI

**Lưu ý:** Trao đổi theo nhiệm vụ và quyền đã cấp.

Toàn bộ là ví dụ biên tập để xem thiết kế; khi triển khai thay bằng dữ liệu và chữ đã duyệt.
Trong ảnh xem trước có thể lược thông điệp phụ nếu trùng tiêu đề, để giữ mật độ nhẹ.

## Đặc tả hình

Canvas 16:9. Nền trắng, navy, xanh dương, teal và cam chỉ là palette ví dụ khi chưa có style lock;
deck style lock luôn ghi đè màu, font appearance, icon và bề mặt của ví dụ.
Biểu tượng bán phẳng, chuyển sắc nhẹ và bóng mờ nhỏ; hình có ngữ nghĩa, không robot trang trí mọi ô.
3–5 khối chính. Mỗi khối một biểu tượng, một nhãn 2–5 đơn vị cách trắng và một câu 4–8 đơn vị.
Ngân sách mặc định D1: 35–70 đơn vị cách trắng trên slide, không tính mã mẫu của thư viện.
Đây là quy ước của project, không phải giới hạn nhận thức hay số token của mô hình.
Tiêu đề và lời mô tả không được chồng lên đường nối. Không đưa đoạn văn ra ngoài vòng làm tăng tải chữ.
Không thêm đồng thời hàng lợi ích, hàng ví dụ và hàng kết luận ở chân.

## Prompt tạo hình

```text
Tạo infographic 16:9 tiếng Việt, nền trắng, mẫu I10 — Lõi và ba hệ thống hỗ trợ.
Thiết kế: Lõi hình minh họa ở tâm, ba khối lập kế hoạch, tri thức, công cụ nối có nhãn.
Giữ deck style lock; nếu chưa có thì dùng palette ví dụ navy–xanh dương–teal và nhấn cam tiết chế để người dùng duyệt.
Dùng lề an toàn; chữ đậm, rõ dấu; 3–5 khối, mỗi khối một nhãn và một câu ngắn.
Chỉ vẽ văn bản trong bản khóa chữ đi kèm. Không thêm tiếng Anh, số %, khẳng định chưa kiểm chứng.
Không chỉ vẽ khung trống: phải có biểu tượng mang nghĩa và nội dung ví dụ ngắn.
Bản mẫu thư viện đánh rõ I10 — Lõi và ba hệ thống hỗ trợ; bản trình chiếu cuối bỏ mã nếu người dùng yêu cầu.
```

Prompt thực phải được biên soạn thành bảy phần và gọi native ImageGen theo
[workflow canonical](../../../03-workflow/03-prompt-and-imagegen.md); layout không chọn renderer mode.

## Kiểm định

- [ ] Có biểu tượng, nội dung ngắn và quan hệ đúng; không chỉ hộp rỗng.
- [ ] Không sao chép mật độ chữ cao của ảnh nguồn.
- [ ] Không có tỷ lệ hoặc cam kết tuyệt đối chưa được nguồn hỗ trợ.
- [ ] Mã đúng; đủ các thành phần; không cắt nhãn ở mép.

[Xem PNG](../../gallery/infographics/I10.png) · [Xem SVG](../../gallery/infographics/I10.svg) · [Danh mục](../../INDEX.md)
