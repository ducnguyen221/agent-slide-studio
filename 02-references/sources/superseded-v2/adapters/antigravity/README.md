# Google Antigravity (superseded adapter source)

Theo tài liệu kiểm tra ngày 2026-09-17, đường dẫn workspace ưu tiên là
`.agents/skills/aia-slide-design/`; toàn cục là `~/.gemini/config/skills/aia-slide-design/`.
Đường `.agent/skills` cũ còn được hỗ trợ nhưng gói không cài song song hai bản.

```bash
python scripts/install.py --host antigravity --scope project --target "D:/Projects/AIA102"
python scripts/install.py --host antigravity --scope project --target "D:/Projects/AIA102" --apply
```

Trong cùng dự án, Codex và Antigravity có thể dùng chung đích .agents/skills.
Sau cài, yêu cầu agent dùng kỹ năng aia-slide-design và xác nhận đúng tệp đã được đọc.
Không giả mọi phiên đều tự nạp GEMINI.md ở gốc dự án.

[rule.md](rule.md) và [workflow.md](workflow.md) là nội dung tham khảo thuần Markdown
để đưa vào mục tùy chỉnh của ứng dụng khi cần. Installer không tự kích hoạt chúng,
không bịa schema frontmatter cho các chế độ kích hoạt UI. Không ghi đè ~/.gemini/GEMINI.md.
Căn cứ: [S07–S08](../../references/sources.md).
