---
title: "Nhật ký thay đổi"
description: "Tài liệu Nhật ký thay đổi trong agent-slide-studio."
document_type: changelog
status: active
---

# Nhật ký thay đổi

## 2.2.0 — 2026-09-18

- Đổi tên skill và package thành `agent-slide-studio`.
- Hợp nhất integration của Codex, Claude và Antigravity vào `plugin/`; bỏ các root `adapters/` và `agents/` cũ.
- Chuẩn hóa frontmatter, đường dẫn governance và reference theo cấu trúc đánh số hiện hành.
- Dùng một `manifest.json` làm sổ payload; bỏ `SHA256SUMS` trùng chức năng.
- Chuyển hồ sơ triển khai về `docs/plans/2026-09-17-imagegen-first-restructure/`.

## 2.1.0 — 2026-09-17

- Giữ L01–L36 và liên kết cũ, bổ sung 12 cấu trúc L37–L48.
- Thêm 12 infographic I01–I12 có nội dung mẫu/biểu tượng; bám bảy ảnh tham chiếu mới.
- CATALOG + registry + taxonomy nhiều chiều; chín nhóm chính, mười bảng xem trước.
- Thêm thư viện lọc ngoại tuyến và sáu mạch presentation mẫu.
- Giảm mật độ mặc định còn D1 35–70 đơn vị cách trắng, không kế thừa các tỷ lệ chưa có nguồn.
- Không thay frontmatter/platform adapter từ v2.0. Không có chứng nhận runtime mới.

## Nội dung nhật ký v2.0

# Nhật ký thay đổi

## 2.0.0 — 2026-09-17

Hợp nhất hai bộ 18 và 20 bố cục; giữ L01–L20 của bộ 20 và thêm L21–L36.
Bổ sung cấu trúc SKILL.md, references, agents, processes, templates, prompts, qa và adapter.
Có script cài an toàn, kiểm tra cấu trúc, manifest và preview từng bố cục.
Không chứa DOCX, tệp font hoặc template thương mại.

Tách quy tắc hiện hành khỏi nguồn lịch sử nguyên byte. Không áp YAML cho mọi Markdown.
Nghiên cứu bổ sung trực tiếp từ nguồn chính thức ngày 2026-09-17; không coi lời gọi
Deep Research trước là một report hoàn tất khi chưa có tệp kết quả được cung cấp.
