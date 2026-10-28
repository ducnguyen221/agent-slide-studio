---
title: "Cài đặt và cập nhật"
description: "Tài liệu Cài đặt và cập nhật trong agent-slide-studio."
document_type: installation-guide
status: active
---

# Cài đặt và cập nhật

Đọc [ma trận](02-references/tooling/host-compatibility.md) và [schema frontmatter](02-references/tooling/frontmatter-policy.md). Tên checkout nguồn không cần trùng tên skill; installer xác định package bằng `SKILL.md`, manifest và explicit payload.

## 1. Mức dự án — khuyến nghị để thử

Từ gốc repository:

```bash
python scripts/install.py --host codex --scope project --target "D:/Projects/AIA102"
python scripts/install.py --host claude --scope project --target "D:/Projects/AIA102"
python scripts/install.py --host antigravity --scope project --target "D:/Projects/AIA102"
```

Đó là các lựa chọn riêng; không cần chạy cả ba. Dùng `--host all` để lập kế hoạch cho mọi host. Mọi lệnh trên chỉ in kế hoạch; thêm `--apply` mới ghi.

Codex và Antigravity dùng chung đích project `.agents/skills/agent-slide-studio`; Claude dùng `.claude/skills/agent-slide-studio`. Installer chỉ ghi skill package vào các đích này. Nó không ghi `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, agent profile hoặc cấu hình host của dự án.

## 2. Mức cá nhân

```bash
python scripts/install.py --host all --scope user
python scripts/install.py --host all --scope user --apply
```

Ba đích user là `~/.agents/skills`, `~/.claude/skills` và `~/.gemini/config/skills`. Không dùng `--target` với `scope=user`; `--home` chỉ đặt home thay thế cho kiểm thử. Installer không sửa governance hay cấu hình ở home.

### Máy đã cài OpcOS: cài qua plugin

Trên máy có OpcOS, **không** chạy installer user-scope cho Claude hay Codex. OpcOS cài repo này như plugin `agent-slide-studio@agent-slide-studio` bằng `system/bootstrap/sync-skills.ps1`:

- **Claude và Codex:** qua plugin cache. Nếu còn bản installer trong `~/.claude/skills` hoặc `~/.agents/skills`, mỗi harness sẽ thấy skill hai lần (`verify-parity` báo `DOUBLE-LISTING`).
- **Antigravity:** plugin native dựng từ chính explicit payload trong `manifest.json`. Gói installer ở `~/.gemini/config/skills` chỉ còn phục vụ các gốc skill của Antigravity, và `sync-skills` tự làm mới nó bằng `--host antigravity`.

Repo giữ dòng LF qua `.gitattributes`, vì `manifest.json` băm byte đã commit. Checkout CRLF (ví dụ do `core.autocrlf=true`) làm installer báo `Hash payload sai`.

## 3. Explicit payload và xác minh destination

Installer dùng allowlist trong `scripts/build_manifest.py`, không copy cả repository. Gói cài loại `v1/`, `.git/`, `.superpowers/`, `docs/plans/`, nguồn superseded, cache/output/temp và governance repository. Python renderer nguồn cũng không được cài.

Mỗi destination được stage và đối chiếu `manifest.json` rồi mới thay bản đang có. Sau khi đặt destination, installer đọc lại và xác minh chính destination đó. Nếu xác minh lỗi, thao tác bị rollback.

## 4. Nâng cấp và hoàn tác

Mặc định script từ chối đích đã tồn tại. Xem kế hoạch, sau đó thêm `--overwrite --apply` để nâng cấp có backup. Backup nằm ở `.aia-skill-backups` bên ngoài vùng discovery.

Muốn hoàn tác: đóng phiên đang dùng skill, kiểm tra backup phù hợp rồi khôi phục thủ công. Script từ chối nguồn/đích symlink và đích chồng lấn nguồn.

## 5. Kiểm tra trong thư mục tạm

```bash
python scripts/build_manifest.py .
python scripts/validate.py . --require-manifest
python scripts/test_package.py
```

`test_package.py` tự tạo project/home tạm, chạy dry-run và apply, xác minh installed package rồi xóa vùng tạm. Không cần và không được thử apply vào project/home thật chỉ để test.

Sau khi cài thật theo yêu cầu: Codex chọn trong `/skills` hoặc gọi `$agent-slide-studio` khi giao diện hỗ trợ; Claude Code thử `/agent-slide-studio`; Antigravity yêu cầu đọc skill `agent-slide-studio`. Những bước đó là runtime check riêng và không được suy ra từ static validator.

## 6. Cài riêng như plugin Claude Code

Thư mục `.claude-plugin/` khai báo gói là một plugin độc lập (`plugin.json` + `marketplace.json`, `source` là `./`, `skills` trỏ vào gốc nơi có `SKILL.md`). Chỉ áp cho Claude Code; Codex và Antigravity vẫn cài theo mục 1-2.

```bash
claude plugin marketplace add <đường-dẫn-tới-checkout-này>
claude plugin install agent-slide-studio@agent-slide-studio
```

Claude Code sao chép cả cây vào cache của plugin (khoảng 76 MB), không chỉ phần trong allowlist ở mục 3. Cài một phần skill chưa hỗ trợ trên Claude: chọn nguyên plugin. Gỡ bằng `claude plugin uninstall agent-slide-studio@agent-slide-studio` rồi `claude plugin marketplace remove agent-slide-studio`. Số phiên bản trong `.claude-plugin/*.json` phải khớp `PACKAGE_VERSION` và tag.
