---
title: "ImageGen-first Knowledge Package Specification"
description: "Tài liệu ImageGen-first Knowledge Package Specification trong agent-slide-studio."
document_type: implementation-plan
status: active
---

# ImageGen-first Knowledge Package Specification

## Mục tiêu

Làm gọn `agent-slide-studio` thành một bộ skill dễ đọc theo đúng trình tự làm slide. Các Markdown trùng vai giữa `SKILL`, integration host, `processes`, `prompts`, `templates` và `qa` phải được hợp nhất về một nguồn canonical. Bộ skill mang sẵn nguyên tắc thiết kế, thư viện bố cục, preview và ảnh mẫu để agent xem trực tiếp trước khi viết prompt hoặc gọi ImageGen.

Luồng tạo ảnh mặc định dùng ImageGen native của host AI hiện tại. Python chỉ phục vụ kiểm link/hash/package, cài đặt tùy chọn và bảo trì gallery khi được gọi rõ; Python không phải backend tạo slide mặc định.

## Ranh giới nguồn

- Root `agent-slide-studio/` là bản hiện hành duy nhất.
- `v1/` là snapshot cũ bất biến; không sửa, không di chuyển, không thêm file.
- `slide-design/` và `skills/slide-infographic/` là nguồn cũ để đối chiếu và hợp nhất, không được tiếp tục chứa một bộ hướng dẫn active đầy đủ cạnh root.
- Không restore/reset 105 tracked deletions đã được người dùng chuyển nguyên nội dung vào `v1/`.
- Không sửa `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` nếu chưa qua cổng phê duyệt governance riêng.

## Cấu trúc đích tối giản

```text
agent-slide-studio/
  README.md
  SKILL.md
  AGENTS.md / CLAUDE.md / GEMINI.md
  CHANGELOG.md
  01-design/
    principles.md
    design-system.md
  02-references/
    INDEX.md
    layouts/                 # L01-L48, I01-I12 và preview tương ứng
    images/                  # ảnh mẫu thực, có phạm vi học/không học
    gallery/                 # contact sheet và HTML gallery
    sources/                 # originals/legacy, chỉ dùng đối chiếu
  03-workflow/
    01-read-and-map.md
    02-lock-style-and-content.md
    03-prompt-and-imagegen.md
    04-review-and-handoff.md
  04-templates/
    deck-plan.md
    slide-prompt.md
    review-and-handoff.md
  plugin/
    README.md                # cài đặt đa host
    codex.md
    claude.md
    antigravity.md
    openai.yaml              # metadata giao diện Codex
  scripts/                   # công cụ hỗ trợ tùy chọn
  docs/plans/
  v1/                        # bất biến
```

Không tạo thêm framework, schema, state machine hoặc bộ specialist-agent Markdown riêng nếu nội dung đã nằm trong bốn bước workflow.

## Một ý, một nguồn canonical

| Nội dung | Nguồn canonical sau hợp nhất |
|---|---|
| Tư duy slide, action title, deck story, density, nhịp toàn bài | `01-design/principles.md` |
| Grid, margin, màu, font appearance, icon, vật liệu, title/footer | `01-design/design-system.md` |
| Chọn L/I theo mục tiêu và quan hệ; dẫn tới preview/ảnh mẫu | `02-references/INDEX.md` |
| Đọc deck và lập bản đồ 100% slide | `03-workflow/01-read-and-map.md` |
| Khóa brand/font/style, chữ, số liệu, nguồn và reference | `03-workflow/02-lock-style-and-content.md` |
| Prompt bảy phần và gọi ImageGen native | `03-workflow/03-prompt-and-imagegen.md` |
| QA ảnh thật, consistency toàn deck và bàn giao | `03-workflow/04-review-and-handoff.md` |
| Brief + slide map + style lock | `04-templates/deck-plan.md` |
| Content lock + prompt từng slide + generation record | `04-templates/slide-prompt.md` |
| QA từng ảnh + toàn deck + handoff | `04-templates/review-and-handoff.md` |

Các file role như instructional designer, information architect, visual director, Vietnamese editor, fact checker và QA reviewer không còn là nguồn quy tắc riêng. Nội dung hữu ích được gộp vào design/workflow; boilerplate vai trò được bỏ khỏi luồng active.

## Đường đọc bắt buộc

1. Đọc `01-design/principles.md` và `01-design/design-system.md` một lần cho task.
2. Đọc toàn bộ deck và nguồn liên quan theo `03-workflow/01-read-and-map.md`.
3. Mở `02-references/INDEX.md`, phân loại toàn bộ slide theo L/I, rồi chỉ mở các layout đã chọn.
4. Mở xem ảnh mẫu thật được layout/INDEX dẫn tới. Ghi rõ dùng ảnh để học bố cục, màu, icon hay vật liệu; không lấy chữ/số liệu trong ảnh làm nguồn nội dung.
5. Khóa brand, font appearance, style, margin và nội dung theo bước 02. Thiếu nhận diện thì hỏi user một lượt gọn, trừ khi user đã cho phép tự chọn.
6. Viết prompt theo bước 03 và adapter host; gọi ImageGen thật cho từng slide.
7. Xem ảnh thật ở kích thước đầy đủ, sửa bằng ImageGen, kiểm toàn deck và bàn giao theo bước 04.

## Hợp đồng deck và ImageGen

- Mọi slide có ID ổn định, nguồn, vai trò, một thông điệp, exact visible text, số/đơn vị khóa, topology, L/I, density, reference và trạng thái QA.
- Chỉ tạo ảnh sau khi đã map đủ deck và style lock đã chốt.
- Prompt có đúng bảy phần theo thứ tự: `CANVAS`, `OBJECTIVE`, `COMPOSITION`, `STYLE`, `CONTENT`, `CONSTRAINTS`, `NEGATIVE`.
- Prompt tự đủ nghĩa; ImageGen không được giả là có thể đọc repo.
- Mặc định dùng direct text trong ImageGen theo yêu cầu 100% ImageGen. Sửa chữ hoặc hình học bằng edit/regenerate của ImageGen, không tự chèn text qua Python/SVG/HTML/PPTX.
- Codex dùng ImageGen native đang được phiên cung cấp. Antigravity dùng khả năng tạo/chỉnh ảnh native mà host thực sự công bố. Không hardcode tool/model/API không được xác minh.
- Thiếu ImageGen trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt; không fallback Python hay screenshot.
- Timeout chưa rõ kết quả trả `OUTCOME_UNKNOWN`; không gửi lại mù.
- Sinh một slide neo đại diện trước; khi tool hỗ trợ, dùng ảnh neo đạt QA làm style reference cho các slide sau.
- Ghi host, tool/model thực nếu biết, prompt, reference, revision, output path/handle và kích thước ảnh thật. Trường không biết ghi `unknown`.

## Chất lượng và giới hạn trung thực

Một slide không được PASS nếu sai một ký tự/dấu/số/đơn vị; sai node/cạnh/thứ tự; crop/overlap; xâm phạm margin; chữ không đọc được; drift khỏi style lock; hoặc ảnh thật chưa được xem.

Ảnh raster không chứng minh font family hoặc point size thật. Skill chỉ được yêu cầu và đánh giá font appearance. Nếu user yêu cầu exact font metadata, phải nói rõ ImageGen-only không chứng minh được yêu cầu đó.

## Acceptance criteria

- `v1/` khớp byte-level hash trước và sau task.
- Root là entrypoint hiện hành duy nhất; không còn ba bộ hướng dẫn đầy đủ cạnh tranh.
- Chỉ còn hai file design, một reference index, bốn workflow và ba template active.
- 48 layout ID, 12 infographic ID và ảnh/preview liên quan còn truy cập được.
- SKILL bắt buộc xem reference/ảnh mẫu thật trước khi tạo prompt.
- Không có bước tạo ảnh mặc định nào gọi Python renderer.
- Thiếu brand/font/style thì hỏi; không tự áp AIA navy/blue/orange nếu user chưa cho phép.
- Codex và Antigravity có adapter ImageGen trung thực, fail closed khi host thiếu capability.
- Link, manifest, installer dry-run và package validation pass.
- Governance chỉ được cập nhật sau approval riêng.
