---
title: Slide Infographic Style Library
status: active_profiles
updated: 2026-09-15
---

# Thư viện profile phong cách

Repo chỉ giữ đặc tính thiết kế đã trừu tượng hóa. Ảnh gốc từ chat riêng nằm tại `$PRESENTATION_HOME/style-references/chatgpt-library/` và được nối với profile bằng private manifest. Không suy rằng file riêng có quyền công khai.

| Style ID | Mức | Dùng khi | Không dùng khi | Profile |
|---|---|---|---|---|
| `light-corporate-cards` | gold | 3–5 nhóm ngang hàng, so sánh, năng lực, kiến trúc khái niệm | Quy trình nhiều nhánh hoặc nội dung body dài | [profile](light-corporate-cards.md) |
| `complex-process-flow` | supporting | Chuỗi giai đoạn có handoff, feedback loop và điểm kiểm soát | Slide mở đầu, thông điệp đơn, chữ phải lớn | [profile](complex-process-flow.md) |

## Cách chọn

1. Chọn profile theo quan hệ nội dung, không chọn chỉ vì màu đẹp.
2. Dùng một profile chính. Ảnh phụ chỉ bổ sung một đặc tính được nêu rõ, ví dụ icon hoặc cách nối luồng.
3. Ưu tiên `TEXT_SAFE` khi chữ Việt dài hoặc ảnh nguồn từng có lỗi chữ. `DIRECT_TEXT` chỉ dùng cho ít nhãn ngắn.
4. Nạp style token của profile một lần vào section `STYLE`; không chép toàn profile, manifest hoặc prompt lịch sử vào imagegen.
5. QA nội dung và hình học độc lập với mức giống style. Giống mẫu không bù được sai chữ, sai số, thiếu node hoặc sai canvas.

Muốn thêm profile, chạy [workflow distill](../../workflows/distill-style-reference.md) và dùng [template](style-card-template.md). Ví dụ binary công khai, nếu có quyền rõ ràng, tuân [asset policy](../../assets/style-examples/POLICY.md).
