---
title: "## Task 4: Sửa link và Python support tools tối thiểu"
description: "Tài liệu ## Task 4: Sửa link và Python support tools tối thiểu trong agent-slide-studio."
document_type: execution-record
status: active
---

### Task 4: Sửa link và Python support tools tối thiểu

**Files:**
- Modify: `scripts/install.py`
- Modify: `scripts/validate.py`
- Modify: `scripts/test_package.py`
- Modify: `scripts/build_manifest.py`
- Modify: `scripts/test_gallery.py`
- Modify: `scripts/README.md`
- Regenerate: `manifest.json`, `SHA256SUMS`

**Produces:** package/install/validation đúng với root canonical, không trở thành runtime tạo ảnh.

- [ ] Dùng explicit payload; loại `.git/`, `v1/`, `slide-design/`, plan docs, cache, output và temp khỏi install package.
- [ ] Không bắt source repo basename phải bằng installed skill name; validate destination package sau install.
- [ ] Gắn nhãn gallery scripts là maintenance-only, chạy khi được yêu cầu.
- [ ] Validate một entrypoint, hai design files, một reference index, bốn workflow, ba template, 48 L, 12 I và link ảnh/preview.
- [ ] Validate prompt compiler có đủ bảy section và không còn placeholder khi generation.
- [ ] Chạy dry-run và temp project install; không ghi host config/governance.
