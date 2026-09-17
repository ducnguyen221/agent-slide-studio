---
title: "Task 4 Report — Python support tools và package payload"
description: "Tài liệu Task 4 Report — Python support tools và package payload trong agent-slide-studio."
document_type: execution-record
status: active
---

# Task 4 Report — Python support tools và package payload

## PLAN

- Dùng một allowlist explicit làm nguồn chung cho manifest, installer và validator.
- Cài theo dry-run mặc định; apply chỉ vào destination skill, stage và xác minh destination trước/sau replace.
- Chỉ scan package active; loại `v1/`, nguồn superseded, plan, governance, cache/output/temp và renderer khỏi installed payload/active validation.
- Kiểm chính cấu trúc ImageGen-first: một active skill, hai design, một reference index canonical, bốn workflow, ba template, L01–L48, I01–I12, registries, previews, ảnh mẫu và link.
- Giữ Python ở vai trò support/validation/package/gallery; không render slide deliverable và không làm ImageGen fallback.

## CHANGESET

- `scripts/build_manifest.py`
  - Khai báo allowlist file/tree explicit và filter cache/output/temp.
  - Tạo deterministic `manifest.json`/`SHA256SUMS` từ đúng payload này.
- `scripts/install.py`
  - Bỏ yêu cầu basename checkout phải bằng tên skill.
  - Copy từng file trong explicit payload thay vì `copytree` toàn repository.
  - Không cài governance, host config hoặc Claude agents ngoài skill package.
  - Stage, kiểm manifest/hash ngay trên destination package, rollback khi lỗi; dry-run vẫn là mặc định.
  - Chặn Windows junction/reparse/symlink thoát project/home scope và recheck trước promotion.
  - Rollback best-effort qua mọi destination, giữ lỗi gốc và báo riêng secondary rollback errors.
- `scripts/validate.py`
  - Scan active explicit payload và active Markdown/HTML links; bỏ `v1/` và sources lịch sử khỏi active scans.
  - Kiểm đúng cấu trúc canonical, registry/taxonomy, 48 L, 12 I, 60 PNG, 60 SVG, ảnh mẫu full-size và hash.
  - Kiểm prompt compiler/template có bảy section đúng thứ tự. Template trống được phép; prompt generation-ready có trường rỗng/placeholder bị fail.
  - Resolve và kiểm containment/payload membership trước khi đọc mọi path từ registry.
  - Manifest được so với chính allowlist có thứ tự, không so với toàn checkout.
- `scripts/test_package.py`
  - 27 regression/fault-injection checks trong temp project/home, gồm installed-destination validation, governance/config preservation, destination/source-ancestor junction, hardlink/traversal/encoding boundaries, overwrite backup/rollback, link/registry/BOM/aspect/prompt faults và manifest determinism/atomic rollback.
- `scripts/test_gallery.py`
  - Dùng `02-references/gallery/index.html`; maintenance-only/on request; trả `SKIP` trung thực khi thiếu Playwright/browser.
- `scripts/README.md`
  - Ghi rõ vai trò từng script, payload boundary và cấm dùng Python renderer làm fallback/deliverable path.
- `INSTALL.md` (cập nhật tối thiểu để lệnh và hành vi cài đặt đúng thực tế)
  - Bỏ hướng dẫn `--with-claude-agents` đã nằm ngoài explicit payload.
  - Mô tả destination validation, temp checks và cam kết không ghi governance/host config.
- `manifest.json`, `SHA256SUMS`
  - Regenerate deterministic từ allowlist chung.
  - Build qua temp files, từ chối symlink/junction/reparse/hardlink và phục hồi cặp integrity khi replace một tệp lỗi.

## VERIFICATION

- `py_compile.compile(..., cfile=<OS temp>)` cho năm script Task 4 với `PYTHONIOENCODING=utf-8`
  - PASS 5/5; bytecode được ghi trong OS temp rồi tự dọn, không để cache trong package.
- `python scripts/validate.py . --require-manifest`
  - PASS: 278 payload files; 252 active files; 87 active Markdown; 819 local links; 48 layouts; 12 infographics; 60 PNG; 60 SVG; 13 full-size samples; manifest checked.
  - Cảnh báo có chủ đích: governance root là repository-only và chờ Task 6 approval; không nằm trong install/active-link scan.
- `python scripts/test_package.py`
  - PASS 27/27: dry-run, temp project/user apply, installed destination validation, exclusions, backup/overwrite, symlink/junction (gồm ancestor junction trong source), hardlink/traversal/encoding boundaries, rollback/CLI-exit fault injection và deterministic/atomic manifest.
- `python scripts/test_gallery.py`
  - PASS 8/8 DOM/filter/JavaScript checks trong môi trường hiện tại.
- Dry-run + apply thủ công vào project dưới `%TEMP%`, sau đó chạy validator từ chính `.agents/skills/aia-slide-design/`:
  - apply exit `0`; installed validator exit `0`; temp project đã dọn sau kiểm tra.
- Explicit manifest exclusion scan:
  - 278 entries; `0` path thuộc `.git/`, `v1/`, `slide-design/`, `.superpowers/`, `docs/plans/`, `superseded-v2`, cache/output/temp.
- `v1/` invariant theo thuật toán trong inventory:
  - 281 files; tree SHA-256 `9e537498a83b9167a68a98af156a8aecc44bdcc58337ecb472eef1d3dc12c8d4` — khớp baseline.
- Python review độc lập:
  - APPROVE; không còn finding CRITICAL/HIGH/MEDIUM trong năm script Task 4.
  - Reviewer xác nhận các fix junction/reparse, cp1252 redirect, traversal-before-I/O, rollback propagation, hardlink và atomic integrity; AST 5/5, validator PASS và package suite 27/27.
  - Một lần I08 lỗi transient trong lúc review; exact repro và full rerun đều PASS nên không có finding tái hiện được. Static analyzers bổ sung không có trong môi trường.

## HANDOFF

- Cần regenerate integrity sau mọi thay đổi payload: `python scripts/build_manifest.py .`, rồi chạy validator/package tests.
- Gallery scripts là maintenance-only và chỉ chạy khi có yêu cầu; chúng không tham gia luồng tạo slide.
- Không sửa governance trong Task 4. Validator ghi cảnh báo dependency này thay vì quét link governance cũ như nội dung active.
- Rollback: khôi phục bảy file Task 4, `INSTALL.md`, `manifest.json` và `SHA256SUMS`; không cần tác động `v1/` hoặc host config.
- Artifact tạm do Task 4 tạo đã được dọn; không commit/push/install global.
