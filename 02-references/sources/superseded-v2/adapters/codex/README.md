# Codex (superseded adapter source)

Cài toàn bộ thư mục skill vào `.agents/skills/aia-slide-design/` của dự án,
hoặc `~/.agents/skills/aia-slide-design/` cho người dùng. Chạy script từ thư mục skill:

```bash
python scripts/install.py --host codex --scope project --target "D:/Projects/AIA102"
python scripts/install.py --host codex --scope project --target "D:/Projects/AIA102" --apply
```

SKILL.md có name/description; agents/openai.yaml là metadata giao diện tùy chọn.
Không tự coi agents/*.md là khai báo native subagent của Codex. Không cấp quyền tool bằng skill.

Sau cài, mở lại phiên hoặc kiểm tra danh sách kỹ năng của môi trường; thử gọi
`$aia-slide-design` hoặc chọn trong `/skills` khi giao diện hỗ trợ. Xác nhận skill đã được nạp,
không chỉ thấy tệp trên đĩa. Nếu có xung đột global/project, kiểm tra bản đang dùng.

AGENTS.md của kho này dùng khi làm việc trực tiếp trong kho skill. Installer không chép đè
AGENTS.md ở dự án đích. Căn cứ: [S01–S03](../../references/sources.md).
