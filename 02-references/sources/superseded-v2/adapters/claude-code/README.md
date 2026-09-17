# Claude Code (superseded adapter source)

Skill dự án: `.claude/skills/aia-slide-design/`. Cá nhân: `~/.claude/skills/aia-slide-design/`.

```bash
python scripts/install.py --host claude --scope project --target "D:/Projects/AIA102"
python scripts/install.py --host claude --scope project --target "D:/Projects/AIA102" --apply
```

Tùy chọn sáu vai trò kiểm định đọc-only:

```bash
python scripts/install.py --host claude --scope project --target "D:/Projects/AIA102" --with-claude-agents --apply
```

Dùng tùy chọn này ngay lần cài đầu, hoặc thêm --overwrite khi chấp nhận backup để nâng cấp bản đã có.
Các tệp trong agents/ của adapter dùng frontmatter subagent riêng; không áp schema đó lên
SKILL.md chung. Vai trò kiểm định không có công cụ ghi; agent điều phối thực hiện việc ghi.

Sau cài, thử `/aia-slide-design` và kiểm tra `/agents` trong môi trường hỗ trợ. Model inherit
và kỹ năng preload được cấu hình theo [S04–S06](../../references/sources.md).
CLAUDE.md gốc nhập @AGENTS.md khi làm việc trong kho skill; installer không sửa CLAUDE.md
hiện hữu ở dự án đích. Không cài thêm .claude/commands trùng tên cùng nhiệm vụ.
