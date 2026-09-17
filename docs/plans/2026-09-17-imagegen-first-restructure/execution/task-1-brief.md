---
title: "## Task 1: Chốt inventory và nguồn canonical"
description: "Tài liệu ## Task 1: Chốt inventory và nguồn canonical trong agent-slide-studio."
document_type: execution-record
status: active
---

### Task 1: Chốt inventory và nguồn canonical

**Files:**
- Create: `docs/plans/2026-09-17-imagegen-first-restructure/inventory.json`
- Create: `docs/plans/2026-09-17-imagegen-first-restructure/migration-map.md`
- Read only: `v1/**`, `slide-design/**`, root package

**Produces:** baseline hash `v1/`, bảng file trùng/drift và mapping nguồn→đích.

- [ ] Ghi branch, HEAD, git status và hash từng file trong `v1/`.
- [ ] So root với `slide-design/` và `skills/slide-infographic/`; phân loại `identical`, `root_newer`, `source_only`, `conflict`.
- [ ] Chọn root v2.1 làm canonical cho L01-L48, I01-I12, taxonomy, gallery và user references.
- [ ] Ghi rõ file Markdown nào được merge vào từng canonical file trong spec.
- [ ] Không move hoặc sửa source trong task này.
- [ ] Parse `inventory.json` và kiểm mọi path tồn tại.
