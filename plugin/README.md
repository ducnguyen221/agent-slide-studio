---
title: "Plugin cài đặt đa agent"
description: "Cài cùng một skill canonical cho Codex, Claude và Antigravity."
document_type: integration
status: active
---

# Plugin cài đặt đa agent

Đây là folder integration active duy nhất. Nó thay thế cả `adapters/` và `agents/`, đồng thời nối một skill canonical ở root với ba host:

- [Codex](codex.md)
- [Claude](claude.md)
- [Antigravity](antigravity.md)

## Cài trực tiếp

Từ root repository, chọn đúng host hoặc dùng `all`:

```bash
python scripts/install.py --host codex --scope project --target "D:/Projects/MyDeck" --apply
python scripts/install.py --host claude --scope project --target "D:/Projects/MyDeck" --apply
python scripts/install.py --host antigravity --scope project --target "D:/Projects/MyDeck" --apply
python scripts/install.py --host all --scope user --apply
```

Installer lấy explicit payload từ `manifest.json`, đặt cùng một bộ skill vào đúng thư mục discovery của từng host và không sửa governance hay cấu hình host. Xem [INSTALL.md](../INSTALL.md) để biết dry-run, overwrite, backup và kiểm định destination.

Các file trong folder này chỉ nối workflow canonical với capability native của host. Quy tắc thiết kế, prompt và QA vẫn nằm ở `SKILL.md` và `03-workflow/`; plugin không tạo bộ hướng dẫn thứ hai. Metadata giao diện Codex nằm ở [openai.yaml](openai.yaml). Tài liệu adapter cũ được lưu dưới `02-references/sources/superseded-v2/adapters/` và không thuộc đường đọc active.
