---
title: "ImageGen-first Knowledge Package Implementation Plan"
description: "Tài liệu ImageGen-first Knowledge Package Implementation Plan trong agent-slide-studio."
document_type: implementation-plan
status: active
---

# ImageGen-first Knowledge Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gộp các Markdown trùng vai, sắp xếp bộ skill theo một đường đọc đánh số, đóng gói sẵn design references và ảnh mẫu, rồi dùng native ImageGen làm đường tạo slide-image mặc định.

**Architecture:** Root là bộ knowledge package active. Nội dung được rút về hai tài liệu design, một reference index, bốn bước workflow và ba template. `v1/` bất biến; Python chỉ giữ vai trò hỗ trợ tùy chọn.

**Tech Stack:** Markdown, JSON registries hiện có, PNG/SVG reference assets, native Codex/Antigravity ImageGen, Python 3 cho validation/packaging tùy chọn.

**Spec:** `docs/plans/2026-09-17-imagegen-first-restructure/spec.md`

## Global Constraints

- Root là canonical; không restore/reset user relocation.
- `v1/` không thay đổi byte nào.
- Không sửa governance files trong wave đầu.
- Không commit, push, publish hoặc cài global.
- Không thêm framework/schema/runtime mới.
- Không dùng Python làm backend tạo slide mặc định.
- Giữ ID L01-L48, I01-I12 và mọi ảnh/preview cần thiết.

## Trạng thái bàn giao và checklist quay lại — 2026-09-18

### Đã hoàn thành

- [x] Task 1: inventory, migration map và baseline byte-level cho `v1/`.
- [x] Task 2: gộp knowledge về cấu trúc đánh số, giữ đủ L01-L48, I01-I12 và ảnh mẫu.
- [x] Task 3: root `SKILL.md` là entrypoint duy nhất; Codex/Antigravity dùng native ImageGen.
- [x] Task 4: explicit payload, installer dry-run, validator cấu trúc, manifest và gallery path hiện hành.
- [x] Task 5 phần tĩnh: link Markdown, registry, manifest và invariant `v1/` đã được kiểm.

### Còn tồn đọng — xử lý theo thứ tự

- [ ] **T4-H1:** `validate.py` phải chặn manifest path tuyệt đối/traversal trước mọi I/O và có regression tương ứng.
- [ ] **T4-H2:** `test_gallery.py` chỉ được `SKIP` khi dependency hoặc browser launch không khả dụng; lỗi DOM sau launch phải `FAIL` với exit khác 0.
- [ ] **T4-H3:** placeholder gate phải đọc cả continuation lines đến section kế tiếp và bắt placeholder nằm ngoài dòng header.
- [ ] **T4-M1:** cập nhật hoặc archive `render_previews.py` và `render_classified.py`; hai script maintenance này còn đọc đường dẫn layout/taxonomy cũ và không thuộc installed payload.
- [ ] **T5-PILOT:** tạo pilot deck và gọi ImageGen thật cho một anchor cùng một slide phụ thuộc; đã hoãn theo yêu cầu người dùng, chưa được đánh dấu PASS.
- [ ] **LOCAL-RENAME:** GitHub repo và remote đã đổi thành `agent-slide-studio`; folder local vẫn mang tên `agent-presentation-studio` vì Windows khóa workspace đang mở. Đóng task/Codex đang giữ folder rồi đổi tên tại `C:\Users\DucNguyen\Code\`.
- [x] **T6-GOV:** đã được người dùng duyệt; đã sửa tên/path/count cũ và thêm frontmatter chuẩn trong `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
- [x] **T6-CLEAN:** đã bỏ compatibility redirect và xóa hai root `references/`, `adapters/`; payload chỉ còn integration active trong `plugin/`.
- [x] **FINAL:** đã chạy lại package/manifest fault injection, gallery test, active-link/frontmatter scan và byte hash `v1/`; runtime ImageGen pilot vẫn là mục T5-PILOT riêng.

### Dọn cấu trúc trong lượt này

- [x] Bỏ các cây rỗng `archetypes/`, `infographics/`, `skills/`, `taxonomy/`, `adapters/codex/`, `adapters/claude-code/` và `agents/`.
- [x] Bỏ `examples/` vì chưa có pilot thật; không giữ placeholder folder.
- [x] Chuyển provenance root cũ vào `02-references/sources/superseded-v2/provenance-root/`.
- [x] Gộp integration và metadata host active vào `plugin/` cho Codex, Claude và Antigravity.
- [x] Root `references/` và `adapters/` đã được xóa sau khi governance chuyển sang đường canonical mới.

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

### Task 3: Viết lại SKILL, README và plugin ImageGen đa host

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`
- Create or consolidate: `plugin/codex.md`
- Create or consolidate: `plugin/claude.md`
- Create or consolidate: `plugin/antigravity.md`
- Keep as needed: `plugin/openai.yaml`
- Convert to short redirect if required: `skills/slide-infographic/SKILL.md`, `slide-design/SKILL.md`

**Produces:** một entrypoint active và native ImageGen routing.

- [ ] SKILL chỉ điều hướng theo đường đọc bắt buộc; không chép lại design/workflow chi tiết.
- [ ] Bắt buộc map toàn deck, chọn L/I và mở ảnh mẫu thật trước khi tạo prompt.
- [ ] Thiếu brand/font/style thì hỏi user một lượt; chỉ tự chọn khi user đã cho phép.
- [ ] Prompt dùng đúng bảy phần và exact visible-text allowlist.
- [ ] Codex/Antigravity dùng native ImageGen thực sự có trong host; không đoán tên tool/model/API.
- [ ] Thiếu capability phải trả `CAPABILITY_UNAVAILABLE`, không fallback Python/HTML/SVG/browser.
- [ ] Text/layout failure được sửa bằng ImageGen edit/regenerate và phải QA lại ảnh thật.
- [ ] README phân biệt root current, `v1/` legacy và Python support tools.
- [ ] Entry point cũ chỉ còn redirect ngắn hoặc được đánh dấu superseded; không giữ bộ quy tắc đầy đủ thứ hai.

### Task 4: Sửa link và Python support tools tối thiểu

**Files:**
- Modify: `scripts/install.py`
- Modify: `scripts/validate.py`
- Modify: `scripts/test_package.py`
- Modify: `scripts/build_manifest.py`
- Modify: `scripts/test_gallery.py`
- Modify: `scripts/README.md`
- Regenerate: `manifest.json`

**Produces:** package/install/validation đúng với root canonical, không trở thành runtime tạo ảnh.

- [ ] Dùng explicit payload; loại `.git/`, `v1/`, `slide-design/`, plan docs, cache, output và temp khỏi install package.
- [ ] Không bắt source repo basename phải bằng installed skill name; validate destination package sau install.
- [ ] Gắn nhãn gallery scripts là maintenance-only, chạy khi được yêu cầu.
- [ ] Validate một entrypoint, hai design files, một reference index, bốn workflow, ba template, 48 L, 12 I và link ảnh/preview.
- [ ] Validate prompt compiler có đủ bảy section và không còn placeholder khi generation.
- [ ] Chạy dry-run và temp project install; không ghi host config/governance.

### Task 5: Kiểm định, pilot và bàn giao

**Files:**
- Create: `07-quality/acceptance.md` only if a compact quality file is still needed; otherwise keep QA canonical in workflow/template.
- Future artifact: pilot deck plan and prompts for 4-6 representative slides; không giữ folder placeholder trước khi task được resume.
- Create: `docs/plans/2026-09-17-imagegen-first-restructure/verification.md`

**Produces:** evidence that the compact package works and remains consistent.

- [ ] Scan active Markdown for duplicated normative paragraphs and competing mode names.
- [ ] Verify every selected layout links to a readable reference/preview and images are bundled with relative paths.
- [ ] Khi resume, build a small deck plan covering cover, process, comparison, cycle and summary; create prompts from the canonical template.
- [ ] If native ImageGen is available in the executing host, generate one anchor and at least one dependent slide, inspect full-size text/margins/style and record the real tool evidence. If unavailable, record `NOT_RUN` or `CAPABILITY_UNAVAILABLE` rather than faking PASS.
- [ ] Run link, registry, manifest, package and installer checks.
- [ ] Re-hash `v1/`; any byte difference blocks completion.
- [ ] List remaining governance pointer changes separately for approval.

### Task 6: Governance alignment — mandatory approval gate

**Files:**
- Potentially modify: root and nested `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`

- [ ] Present exact wording, file locations, behavior impact, benefit, risk and rollback.
- [ ] Wait for explicit user approval.
- [ ] Update only stale path/count/validation pointers after approval.
- [ ] Re-run final validation.

## Verification commands

Use the current repo scripts after Task 4, plus a Markdown link scan, registry counts, installer dry-run and byte-level `v1/` comparison. Record commands and outputs in `verification.md`. Runtime ImageGen status must remain host-specific and evidence-backed.

## Rollback

No source package is deleted in the first wave. Roll back only files created/changed by this plan and reverse moves according to `migration-map.md`. `v1/` remains untouched.
