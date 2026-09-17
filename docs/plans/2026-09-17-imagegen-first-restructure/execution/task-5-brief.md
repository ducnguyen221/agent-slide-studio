---
title: "## Task 5: Kiểm định, pilot và bàn giao"
description: "Tài liệu ## Task 5: Kiểm định, pilot và bàn giao trong agent-slide-studio."
document_type: execution-record
status: active
---

### Task 5: Kiểm định, pilot và bàn giao

**Files:**
- Create: `07-quality/acceptance.md` only if a compact quality file is still needed; otherwise keep QA canonical in workflow/template.
- Create: `examples/pilot-deck/` with one deck plan and prompts for 4-6 representative slides.
- Create: `docs/plans/2026-09-17-imagegen-first-restructure/verification.md`

**Produces:** evidence that the compact package works and remains consistent.

- [ ] Scan active Markdown for duplicated normative paragraphs and competing mode names.
- [ ] Verify every selected layout links to a readable reference/preview and images are bundled with relative paths.
- [ ] Build a small deck plan covering cover, process, comparison, cycle and summary; create prompts from the canonical template.
- [ ] If native ImageGen is available in the executing host, generate one anchor and at least one dependent slide, inspect full-size text/margins/style and record the real tool evidence. If unavailable, record `NOT_RUN` or `CAPABILITY_UNAVAILABLE` rather than faking PASS.
- [ ] Run link, registry, manifest, package and installer checks.
- [ ] Re-hash `v1/`; any byte difference blocks completion.
- [ ] List remaining governance pointer changes separately for approval.
