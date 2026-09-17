---
title: "Công cụ hỗ trợ tùy chọn"
description: "Tài liệu Công cụ hỗ trợ tùy chọn trong agent-slide-studio."
document_type: tooling-guide
status: active
---

# Công cụ hỗ trợ tùy chọn

Đọc skill và tạo/chỉnh ảnh bằng ImageGen native không cần Python. Python trong gói này chỉ hỗ trợ cài đặt, kiểm cấu trúc/link/hash/package và kiểm tra gallery. Các script không được tạo slide deliverable, chèn chữ lên ảnh hoặc làm fallback khi host thiếu ImageGen.

## Công cụ được đóng gói

- `install.py`: dry-run mặc định; chỉ `--apply` mới ghi. Script cài explicit payload và xác minh hash ngay trên từng destination đã stage/cài.
- `validate.py`: cần PyYAML; kiểm active package, registries, preview, ảnh mẫu, link Markdown/HTML, prompt bảy phần và manifest. Nó không kiểm hành vi model hoặc runtime host.
- `build_manifest.py`: tạo deterministic `manifest.json` từ explicit payload allowlist mà installer/validator dùng.
- `test_package.py`: fault injection và thử cài project/user trong thư mục tạm; không sửa cấu hình thật.
- `test_gallery.py`: **maintenance-only, chỉ chạy khi được yêu cầu rõ**. Nếu thiếu Playwright/browser, script trả `SKIP` và không tự cài dependency.

```bash
python scripts/build_manifest.py .
python scripts/validate.py . --require-manifest
python scripts/test_package.py
python scripts/test_gallery.py .
```

Không tự chạy `pip`. Phụ thuộc kiểm định được liệt kê trong `requirements-check.txt`.

## Ranh giới payload

Allowlist canonical nằm trong `build_manifest.py`. Bản cài không chứa `.git/`, `v1/`, `slide-design/`, `.superpowers/`, `docs/plans/`, cache/output/temp, governance root, `02-references/sources/superseded-v2/` hoặc script renderer nguồn. Hai collection `sources/originals/` và `sources/legacy/` được giữ vì `02-references/INDEX.md` trỏ rõ tới nguồn đối chiếu; validator loại chúng khỏi active scans.

## Bảo trì gallery trong source repo

`render_previews.py` và `render_classified.py` là công cụ nguồn cũ để bảo trì asset, **không nằm trong installed payload và chỉ chạy khi có yêu cầu bảo trì gallery riêng**. Output hiện hành ở `02-references/gallery/`. Không dùng hai script này để tạo slide bàn giao hoặc thay ImageGen.
