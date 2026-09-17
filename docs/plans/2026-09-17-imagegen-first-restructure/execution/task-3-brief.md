---
title: "## Task 3: Viết lại SKILL, README và adapter ImageGen"
description: "Tài liệu ## Task 3: Viết lại SKILL, README và adapter ImageGen trong agent-slide-studio."
document_type: execution-record
status: active
---

### Task 3: Viết lại SKILL, README và adapter ImageGen

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`
- Create or consolidate: `adapters/codex.md`
- Create or consolidate: `adapters/antigravity.md`
- Keep as needed: `agents/openai.yaml`
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
