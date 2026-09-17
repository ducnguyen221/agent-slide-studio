---
title: "## Task 2: Gộp knowledge và sắp xếp cấu trúc đánh số"
description: "Tài liệu ## Task 2: Gộp knowledge và sắp xếp cấu trúc đánh số trong agent-slide-studio."
document_type: execution-record
status: active
---

### Task 2: Gộp knowledge và sắp xếp cấu trúc đánh số

**Files:**
- Create: `01-design/principles.md`
- Create: `01-design/design-system.md`
- Create: `02-references/INDEX.md`
- Create: `03-workflow/01-read-and-map.md`
- Create: `03-workflow/02-lock-style-and-content.md`
- Create: `03-workflow/03-prompt-and-imagegen.md`
- Create: `03-workflow/04-review-and-handoff.md`
- Create: `04-templates/deck-plan.md`
- Create: `04-templates/slide-prompt.md`
- Create: `04-templates/review-and-handoff.md`
- Consolidate into: `02-references/layouts/`, `02-references/images/`, `02-references/gallery/`, `02-references/sources/`

**Consumes:** migration map and the existing root/nested/v1 sources.

- [ ] Merge design thinking, deck rhythm and role knowledge into two design files; mỗi ý chỉ xuất hiện một lần.
- [ ] Merge all layout/taxonomy INDEX files into one selection table linking L/I to preview and real sample images.
- [ ] Require the agent to open the real image, and record what to learn/not learn from it.
- [ ] Merge process, agent-role, prompt and QA rules into four workflow files.
- [ ] Merge the active templates into three templates with only fields used by the workflow.
- [ ] Move/copy assets only after verifying absolute source/destination paths are inside the repo; never overwrite a non-identical file silently.
- [ ] Preserve originals/legacy only under `02-references/sources/`; they are not on the normal reading path.
- [ ] Leave `v1/` unchanged and leave `slide-design/` intact until final consolidation is verified.
