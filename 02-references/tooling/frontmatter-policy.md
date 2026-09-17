---
title: Frontmatter cho tài liệu active
description: Schema YAML tối thiểu để agent cài đặt, phân loại và tham chiếu tài liệu trong agent-slide-studio.
document_type: metadata-policy
status: active
---

# Frontmatter cho tài liệu active

Mọi Markdown thuộc payload active phải bắt đầu bằng YAML frontmatter UTF-8 không BOM.
Nguồn bất biến trong `v1/`, `originals/`, `legacy/` và `superseded-v2/` giữ nguyên byte và không áp schema mới.

## Schema

| Loại | Trường bắt buộc | Trường tùy chọn |
|---|---|---|
| `SKILL.md` | `name`, `description` | Không thêm trường vendor-specific |
| Tài liệu active khác | `title`, `description`, `document_type`, `status` | `id`, `step`, `host` khi có nghĩa |
| Metadata host `plugin/openai.yaml` | YAML thuần theo host | Không bọc frontmatter Markdown |
| Governance root | Cùng schema tài liệu; vẫn phải giữ directive/import mà harness yêu cầu | Không thêm quyền tool/model |

`status` của tài liệu hiện hành là `active`. `document_type` dùng danh từ ổn định như
`design-guide`, `layout`, `infographic`, `workflow`, `template`, `integration`,
`reference-index`, `installation-guide` hoặc `repository-doc`.

Không dùng frontmatter để tự cấp quyền, chọn model hoặc thay quy tắc an toàn. Link trong metadata
không thay thế link Markdown có thể kiểm tra. Mỗi file chỉ có một nguồn canonical; redirect phải ghi
rõ `document_type: compatibility-redirect` và được xóa khi không còn consumer.
