---
title: "Ma trận tương thích"
description: "Tài liệu Ma trận tương thích trong agent-slide-studio."
document_type: reference-guide
status: active
---

# Ma trận tương thích

Đối chiếu tài liệu S01–S08 được ghi trong hồ sơ provenance của repository, kiểm tra ngày 2026-09-17. Phân biệt đối chiếu tài liệu,
kiểm tra cấu trúc, cài thử filesystem với việc chạy host thật. Bản này chưa chạy
đăng nhập trên Codex, Claude Code hoặc Antigravity của người dùng.

| Hạng mục | Codex | Claude Code | Antigravity |
|---|---|---|---|
| Dự án | .agents/skills/agent-slide-studio/ | .claude/skills/agent-slide-studio/ | .agents/skills/agent-slide-studio/ |
| Cá nhân | ~/.agents/skills/agent-slide-studio/ | ~/.claude/skills/agent-slide-studio/ | ~/.gemini/config/skills/agent-slide-studio/ |
| Điểm vào | SKILL.md | SKILL.md | SKILL.md |
| Header | name + description | Cùng header | Cùng header |
| Hướng dẫn kho | AGENTS.md | CLAUDE.md nhập @AGENTS.md | Rule workspace tạo qua Customizations |
| Gọi rõ ràng | $agent-slide-studio hoặc chọn /skills | /agent-slide-studio | Yêu cầu sử dụng tên skill, xác nhận đã nạp |
| Integration active | plugin/codex.md | plugin/claude.md | plugin/antigravity.md |
| Metadata giao diện | plugin/openai.yaml | Không cần | Không cần |

Codex không hợp nhất tự động skill trùng tên. Tránh cài đồng thời nhiều bản ở user/project
mà không biết bản nào được nạp. Antigravity hỗ trợ .agent/skills cũ nhưng bản mới dùng .agents.
Cài project cho Codex và Antigravity chỉ tạo một đích dùng chung, không hai bản trùng.
Không áp thứ tự ưu tiên hoặc schema của nền tảng này sang nền tảng khác.

Installer không sửa AGENTS.md/CLAUDE.md/GEMINI.md ngoài thư mục skill; muốn hợp nhất luật kho
phải đọc và duyệt riêng. Skill không tự mang image generator, quyền shell hoặc subagent runtime.
