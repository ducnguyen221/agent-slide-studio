# Agent-Slide-Craft

> **Hệ sinh thái tự động hóa thiết kế Slide bài giảng & Infographic Presentation bằng AI Agent (Codex, Claude, Antigravity).**
> Kết hợp **100% Native Editable PowerPoint Shapes** và **Style-Locked Visual Assets (AI Images)**.

---

## Tính Năng Nổi Bật

- **100% Editable Vector Shapes:** Các khối thẻ (Cards), quy trình (Process Flow), dòng thời gian (Timeline), chỉ số nổi bật (KPIs) được sinh dưới dạng Shape vector gốc của PowerPoint, cho phép click đúp sửa từng chữ và đổi màu trực tiếp.
- **Style DNA Engine:** Khóa chặt phong cách mỹ thuật (Art Style, Color Palette, Negative Space, Aspect Ratio) giữa các slide.
- **Reverse Distillation Engine:** Nạp vào file PowerPoint mẫu (`.pptx`) hoặc ảnh infographic (`.png`) để tự động bóc tách thành Design Profile tái sử dụng (`profiles/<name>/`).
- **Pedagogy & Cognitive Load Auditor:** Tự động kiểm tra độ tương phản màu WCAG ($\ge 7:1$) và giới hạn tải nhận thức ($\le 50$ từ/slide, nguyên lý Mayer).
- **Quy trình 3 Cổng (3-Gateway Workflow):** Duyệt Outline $\rightarrow$ Duyệt Wireframe $\rightarrow$ Biên dịch Slide hoàn chỉnh.

---

## Cài Đặt

```bash
cd agent-slide-craft
pip install python-pptx pydantic pyyaml pillow
```

---

## Hướng Dẫn Sử Dụng CLI

### 1. Biên dịch Slide từ file `deck.yaml`
```bash
# Sử dụng theme mặc định trong deck.yaml
python -m slidecraft.cli.main build --deck sample_lecture_deck.yaml --output "output/my_lecture.pptx"

# Áp dụng theme khác (vd: academic_light hoặc tech_dark_modern)
python -m slidecraft.cli.main build --deck sample_lecture_deck.yaml --profile academic_light --output "output/lecture_light.pptx"
```

### 2. Bóc tách (Distill) Style từ file PowerPoint mẫu
```bash
python -m slidecraft.cli.main distill --input "./sample.pptx" --name "my_custom_theme"
```

### 3. Kiểm toán sư phạm & tải nhận thức
```bash
python -m slidecraft.cli.main audit --deck sample_lecture_deck.yaml
```

---

## Cấu Trúc Repository

```text
agent-slide-craft/
├── profiles/                           # Thư mục chứa các Design Profile đã chuẩn hóa
│   ├── academic_light/                 # Profile bài giảng hàn lâm sáng sủa
│   └── tech_dark_modern/               # Profile công nghệ nền tối
├── src/slidecraft/
│   ├── ir/                             # Canonical Intermediate Representation (Schemas)
│   ├── layout/                         # Geometry, Grid & Text Metrics Engine
│   ├── compile/                        # PPTX Backend Native Shape Compiler
│   ├── distill/                        # PPTX & Visual Reverse Decompiler
│   ├── validate/                       # WCAG Contrast & Cognitive Load Auditor
│   └── cli/                            # Command Line Interface
└── skills/                             # Custom Skills cho Claude, Codex, Antigravity
    ├── slide-craft/                    # Skill tạo bài giảng
    └── design-distill/                 # Skill bóc tách mẫu
```
