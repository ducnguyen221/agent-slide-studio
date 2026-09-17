---
title: "ChatGPT Project Upload Package"
description: "Instructions and upload order for the self-contained ChatGPT Project package."
document_type: packaging-guide
status: active
---

# ChatGPT Project Upload Package

Folder này là gói độc lập để đưa Agent Slide Studio vào một ChatGPT Project.

## Thiết lập

1. Mở `PROJECT_INSTRUCTIONS.md`, sao chép phần nằm giữa hai mốc vào **Project settings → Project instructions**.
2. Upload bốn file kiến thức theo đúng tên:
   - `01_SLIDE_DESIGN_PLAYBOOK.md`
   - `02_LAYOUT_CATALOG.md`
   - `03_SLIDE_TEMPLATES.md`
   - `04_IMAGE_REFERENCE_INDEX.md`
3. Upload tối thiểu 10 ảnh nhóm `G01.png`–`G09B.png` trong `images/`.
4. Để tăng chất lượng bắt chước phong cách, upload thêm `R01–R07` và sáu file `REF01–REF06`.
5. Với mỗi deck, upload thêm PPTX/PDF nguồn, brief, dữ liệu, brand guide và logo liên quan.

Không cần upload `.nojekyll`, manifest, scripts, plugin, governance, kế hoạch triển khai, nguồn lịch sử hoặc `v1/`.

## Thứ tự ưu tiên nếu giới hạn file

1. Bốn file Markdown.
2. Mười ảnh `G`.
3. Chỉ các ảnh `R`/`REF` liên quan đến deck đang làm.
4. Tài liệu và dữ liệu của deck hiện tại.

Không upload ZIP nếu muốn ChatGPT đọc trực tiếp từng nguồn và ảnh. Giữ nguyên tên file để instructions định tuyến đúng.
