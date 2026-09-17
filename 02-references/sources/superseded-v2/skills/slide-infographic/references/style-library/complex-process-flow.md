---
title: Complex Process Flow
status: supporting_profile
updated: 2026-09-15
---

# `complex-process-flow`

## Identity

- evidence: `supporting`, chắt từ một ảnh quy trình nhiều giai đoạn; chỉ dùng để học geometry và luồng.
- use_when: 4–7 giai đoạn có hướng, handoff, kiểm soát và một feedback loop rõ.
- avoid_when: slide mở đầu, một thông điệp duy nhất, chữ thuyết trình phải lớn hoặc hơn bảy giai đoạn.
- private_reference: `selected/supporting/complex-process-flow.png`.

## Geometry

- Canvas 16:9; title gọn ở trên; vùng quy trình chiếm trục ngang trung tâm.
- Mỗi giai đoạn là một lane/cột; header, hành động chính và output xếp theo cùng baseline.
- Luồng chính trái→phải dùng một loại mũi tên; feedback loop dùng đường thứ cấp và màu riêng.
- Safe margin tối thiểu 5%; khoảng giữa lane đủ để mũi tên không xuyên chữ hoặc icon.

## Visual language

- Nền trung tính sáng; lane phân biệt bằng accent tiết chế, không biến thành cầu vồng.
- Icon phẳng/outline đồng nhất; badge hoặc checkpoint dùng hình học riêng nhưng cùng độ nét.
- Nhấn mạnh bottleneck, gate và outcome bằng kích thước/viền, không bằng thêm quá nhiều chữ.

## Content ceiling

- `TEXT_SAFE` gần như bắt buộc khi có hơn bốn stage hoặc body tiếng Việt.
- Mỗi stage giữ một nhãn và tối đa một micro-description; chi tiết vận hành chuyển sang speaker notes hoặc slide kế tiếp.
- Nếu có nhiều hơn một feedback loop hoặc nhiều nhánh chéo, tách sơ đồ thay vì thu nhỏ chữ.

## Prompt token

```text
STYLE | Structured enterprise process map; clean horizontal lanes, consistent flat icons, restrained stage accents, explicit primary arrows and one secondary feedback loop, generous routing space, crisp hierarchy.
NEGATIVE add-on | Không mũi tên xuyên chữ, không connector mơ hồ, không lane chen chúc, không rainbow palette, không chữ siêu nhỏ.
```

## QA fingerprints

- Must: đủ stage; hướng luồng đọc được; loop quay đúng đích; lane thẳng hàng; connector không che nội dung.
- Reject: dùng màu thay cho mũi tên; đảo thứ tự stage; loop mở; text nhỏ để nhét chi tiết; sao chép dữ liệu nghiệp vụ của ảnh mẫu.
