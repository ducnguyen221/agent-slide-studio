---
name: agent-slide-studio
description: >-
  Thiết kế và kiểm định deck slide 16:9 tiếng Việt bằng bố cục L01-L48,
  infographic I01-I12 và ImageGen native của host. Dùng khi cần lập deck map,
  khóa chữ, soạn prompt, tạo hoặc sửa ảnh slide và QA toàn deck.
---

# Thiết kế slide bằng ImageGen

`SKILL_ROOT` là thư mục chứa file này. Mọi đường dẫn dưới đây tính từ `SKILL_ROOT`, không từ thư mục làm việc của người dùng. Root này là entrypoint active duy nhất; `v1/` và `02-references/sources/` chỉ để đối chiếu.

## Đường đọc bắt buộc

1. Đọc [nguyên tắc](01-design/principles.md) và [hệ thiết kế](01-design/design-system.md) một lần cho task.
2. Đọc toàn bộ deck và nguồn liên quan, rồi map **100% slide** theo [bước 01](03-workflow/01-read-and-map.md) và [deck plan](04-templates/deck-plan.md). Chưa map đủ thì chưa tạo prompt hoặc ảnh.
3. Mở [reference index](02-references/INDEX.md), chọn mã L/I cho từng slide, rồi mở đặc tả, preview và **ảnh mẫu thật được bundle** mà index dẫn tới. Ghi rõ điều học và không học từ từng ảnh; không chọn từ thumbnail, tên file hoặc chữ/số trong ảnh.
4. Khóa content và style theo [bước 02](03-workflow/02-lock-style-and-content.md). Nếu thiếu bất kỳ quyết định brand, font appearance hoặc style nào, gom thành **một lượt hỏi người dùng**; chỉ tự chọn khi người dùng đã cho phép auto-choice.
5. Soạn prompt theo [bước 03](03-workflow/03-prompt-and-imagegen.md) và [template](04-templates/slide-prompt.md). Prompt phải có đúng thứ tự `CANVAS`, `OBJECTIVE`, `COMPOSITION`, `STYLE`, `CONTENT`, `CONSTRAINTS`, `NEGATIVE`. `CONTENT` là allowlist đầy đủ: mọi chuỗi nhìn thấy phải xuất hiện nguyên văn, có ID; cấm sinh thêm chữ ngoài allowlist.
6. Dùng integration của host: [Codex](plugin/codex.md), [Claude](plugin/claude.md) hoặc [Antigravity](plugin/antigravity.md). Chỉ gọi capability ImageGen native mà phiên hiện tại thực sự cung cấp; không đoán tên tool, model hoặc API.
7. Mở ảnh đúng revision ở kích thước đầy đủ và QA theo [bước 04](03-workflow/04-review-and-handoff.md). Lỗi chữ, topology, crop, lề, độ đọc hoặc style phải được sửa bằng ImageGen edit/regenerate, tạo revision mới và QA lại **toàn ảnh**. Sau cùng kiểm consistency toàn deck và ghi [handoff](04-templates/review-and-handoff.md).

## Cổng fail-closed

- Thiếu capability tạo/chỉnh ảnh native: trả `CAPABILITY_UNAVAILABLE`, giữ nguyên content lock và bàn giao prompt. Không fallback sang Python, HTML, SVG, browser/screenshot, PPTX overlay hoặc renderer khác.
- Timeout hoặc outcome không rõ: trả `OUTCOME_UNKNOWN`, kiểm lại cùng tác vụ nếu host hỗ trợ; không gửi lại mù.
- Không thấy được ảnh thật đầy đủ hoặc không đo được điều bắt buộc: trạng thái `unverified`, không tuyên bố PASS.
- ImageGen raster chỉ cho phép đánh giá font appearance. Không tuyên bố đã chứng minh font family, point size hoặc editability thật.
