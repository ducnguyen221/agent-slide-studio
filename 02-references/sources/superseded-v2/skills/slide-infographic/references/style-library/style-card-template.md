---
title: Style Card Template
status: markdown_template
updated: 2026-09-15
---

# Mẫu hồ sơ phong cách

Mỗi profile chỉ mô tả một ngôn ngữ thiết kế đã được kiểm từ ảnh thật. Không chép nội dung riêng của ảnh mẫu.

```markdown
## Identity

- style_id: <kebab-case>
- evidence: gold | supporting
- use_when: <quan hệ nội dung phù hợp>
- avoid_when: <trường hợp dễ hỏng>
- private_reference: <đường tương đối dưới selected/ hoặc none>

## Geometry

- canvas: <tỷ lệ/canvas ưu tiên>
- safe_margin: <tỷ lệ từng cạnh>
- reading_order: <trái-phải/trên-dưới/vòng>
- regions: <số và vai trò vùng>
- spacing: <gutter/padding/rhythm>

## Visual language

- background: <vai màu>
- palette: <vai màu, không chỉ mã hex>
- surface: <flat/glass/outline/...>
- icons: <hệ icon>
- emphasis: <cách tạo cấp bậc>

## Content ceiling

- preferred_mode: <TEXT_SAFE/DIRECT_TEXT/NO_TEXT>
- title: <giới hạn thực dụng>
- labels: <số lượng/độ dài>
- body: <khi nào phải tách slide>

## Prompt token

STYLE | <một câu đủ dùng, không lặp geometry/content>.
NEGATIVE add-on | <chỉ lỗi đặc thù profile>.

## QA fingerprints

- Must: <3–6 dấu hiệu bắt buộc>
- Reject: <3–6 dấu hiệu khiến style fail>
```

Đường private chỉ nằm trong private reference map; profile public dùng đường tương đối quy ước, không hardcode tên user, thread ID hoặc đường temp. Một profile không được tự nâng `supporting` thành `gold` nếu chưa có ảnh thật và đánh giá riêng.
