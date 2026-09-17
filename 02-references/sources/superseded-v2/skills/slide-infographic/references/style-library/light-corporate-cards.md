---
title: Light Corporate Cards
status: gold_profile
updated: 2026-09-15
---

# `light-corporate-cards`

## Identity

- evidence: `gold`, chắt từ hai ảnh slide riêng đã mở và đo; câu chữ trong ảnh không phải canonical.
- use_when: 3–5 nhóm ngang hàng, so sánh cột, năng lực hoặc kiến trúc khái niệm.
- avoid_when: quy trình nhiều nhánh, body dài hoặc cần hơn hai tầng phân cấp trong mỗi card.
- private_reference: `selected/gold/light-corporate-cards.png`; ảnh so sánh phụ `selected/gold/three-column-comparison.png`.

## Geometry

- Canvas ưu tiên 16:9; title nằm trong dải trên khoảng 14–18% chiều cao.
- Nội dung là lưới 2×2 hoặc 3 cột cân bằng; card cùng kích thước, mép thẳng hàng.
- Safe margin tối thiểu 5% mỗi cạnh; gutter giữa card khoảng 2–3% chiều rộng; padding trong card rộng và đều.
- Mỗi card có một điểm nhìn icon/mini-scene và một vùng chữ riêng; thứ tự đọc trái→phải, trên→dưới.

## Visual language

- Nền trắng hoặc trắng xanh rất nhạt; card trắng với viền/bóng mềm, không tạo khối nặng.
- Navy/blue là màu cấu trúc; teal, purple và amber làm accent có vai trò, không rải ngẫu nhiên.
- Icon 3D mềm hoặc isometric tối giản, cùng góc nhìn và độ hoàn thiện; không trộn ảnh thật với icon vector thô.
- Cấp bậc rõ bằng title lớn, tên card đậm, body nhỏ hơn; khoảng trắng là thành phần chính.

## Content ceiling

- `TEXT_SAFE` là mode ưu tiên khi có body tiếng Việt. `DIRECT_TEXT` phù hợp với một title và 3–4 nhãn ngắn.
- Mỗi card chỉ nên có một ý, tối đa hai dòng mô tả ngắn; dài hơn thì dùng overlay hoặc tách slide.
- Không học chính tả, tên riêng, logo hoặc dữ kiện từ ảnh mẫu.

## Prompt token

```text
STYLE | Light premium corporate infographic; white-blue canvas, equal rounded cards, soft depth, restrained navy/teal/purple accents, consistent polished 3D icons, generous whitespace, crisp hierarchy.
NEGATIVE add-on | Không card lệch kích thước, không bóng nặng, không gradient chói, không icon lẫn phong cách, không chữ chen sát mép.
```

## QA fingerprints

- Must: title thoáng; card thẳng hàng; gutter đều; icon đồng nhất; accent có vai trò; không chi tiết chạm lề.
- Reject: card co giãn theo lượng chữ; hơn ba font style; icon quá lớn lấn chữ; nền trang trí cạnh tranh với nội dung; dùng body của ảnh mẫu.
