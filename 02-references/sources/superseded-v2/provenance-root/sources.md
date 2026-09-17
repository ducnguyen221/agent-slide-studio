# Danh mục nguồn nghiên cứu bổ sung

Ngày đối chiếu: 2026-09-17. 22 trang đã truy cập, 2 nguồn hạn chế truy cập (S15, S24).
Đây là nghiên cứu trực tiếp, không giả là report từ phiên Deep Research chưa được cung cấp.

## S01 — Specification

**OFFICIAL · Agent Skills.** [Nguồn](https://agentskills.io/specification) · Truy cập 2026-09-17.

SKILL.md có name và description; name khớp thư mục. Tài nguyên bổ trợ được phép.

**Giới hạn:** Đối chiếu schema, không chứng nhận runtime.

## S02 — Build skills

**OFFICIAL · OpenAI.** [Nguồn](https://developers.openai.com/codex/skills) · Truy cập 2026-09-17.

Codex dùng .agents/skills; agents/openai.yaml là metadata tùy chọn.

**Giới hạn:** Đã chuyển hướng sang learn.chatgpt.com/docs/build-skills; không suy ra quyền tool.

## S03 — AGENTS.md

**OFFICIAL · OpenAI.** [Nguồn](https://developers.openai.com/codex/guides/agents-md) · Truy cập 2026-09-17.

Hướng dẫn kho được đọc theo phạm vi thư mục; AGENTS.md là Markdown.

**Giới hạn:** Không biến AGENTS.md thành YAML khai báo subagent.

## S04 — Skills

**OFFICIAL · Anthropic.** [Nguồn](https://code.claude.com/docs/en/skills) · Truy cập 2026-09-17.

Claude Code dùng .claude/skills; có trường điều khiển riêng.

**Giới hạn:** Không áp các trường context, agent riêng của Claude cho mọi host.

## S05 — Subagents

**OFFICIAL · Anthropic.** [Nguồn](https://code.claude.com/docs/en/sub-agents) · Truy cập 2026-09-17.

Subagent có name/description; có thể chọn tools, model và preload skills.

**Giới hạn:** Vai trò Markdown chung không tự thành tiến trình phụ.

## S06 — Memory

**OFFICIAL · Anthropic.** [Nguồn](https://code.claude.com/docs/en/memory) · Truy cập 2026-09-17.

CLAUDE.md có thể nhập @AGENTS.md để dùng chung hướng dẫn.

**Giới hạn:** Không ghi đè cấu hình người dùng; không giả mọi host đọc CLAUDE.md.

## S07 — Antigravity skills

**OFFICIAL · Google.** [Nguồn](https://antigravity.google/docs/skills) · Truy cập 2026-09-17.

Workspace .agents/skills; toàn cục ~/.gemini/config/skills; .agent/skills còn tương thích cũ.

**Giới hạn:** Đối chiếu 2026-09-17; tránh cài cả hai đường trùng tên.

## S08 — Antigravity rules

**OFFICIAL · Google.** [Nguồn](https://antigravity.google/docs/rules-workflows) · Truy cập 2026-09-17.

Rules là Markdown, workspace .agents/rules; toàn cục ~/.gemini/GEMINI.md; có kiểu kích hoạt trong giao diện.

**Giới hạn:** Không đủ bằng chứng cho schema YAML workflow phổ quát; cung cấp mẫu trung tính.

## S09 — Slide size

**OFFICIAL · Microsoft.** [Nguồn](https://support.microsoft.com/en-us/powerpoint/change-the-size-of-your-powerpoint-slides) · Truy cập 2026-09-17.

Widescreen 16:9 dùng 13,333×7,5 inch.

**Giới hạn:** Lề pixel trong gói là quy ước, không phải tiêu chuẩn Microsoft.

## S10 — Accessibility

**OFFICIAL · Microsoft.** [Nguồn](https://support.microsoft.com/en-us/office/make-your-powerpoint-presentations-accessible-to-people-with-disabilities-6f7772b2-2f33-4bd2-8ca7-dae3b2b3ef25) · Truy cập 2026-09-17.

Khuyến nghị phông không chân từ 18 pt, khoảng trắng, tiêu đề, mô tả thay thế và thứ tự đọc.

**Giới hạn:** Ảnh có chữ không tự có cấu trúc tiếp cận như văn bản thực.

## S11 — Choose SmartArt

**OFFICIAL · Microsoft.** [Nguồn](https://support.microsoft.com/en-us/office/graphics-visuals/choose-a-smartart-graphic) · Truy cập 2026-09-17.

Chọn theo quan hệ: list, process, cycle, hierarchy, relationship, matrix, pyramid, picture.

**Giới hạn:** Đường thường khác mũi tên có hướng; infographic giống SmartArt không phải đối tượng gốc.

## S12 — All SmartArt graphics

**OFFICIAL · Microsoft.** [Nguồn](https://support.microsoft.com/en-us/office/graphics-visuals/all-smartart-graphics-described) · Truy cập 2026-09-17.

Danh mục mô tả bố cục để tra mục đích.

**Giới hạn:** Tên mẫu thực tế cần kiểm tra trên PowerPoint người dùng.

## S13 — Contrast Minimum

**OFFICIAL · W3C.** [Nguồn](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · Truy cập 2026-09-17.

Ngưỡng 4,5:1 cho chữ thường và 3:1 cho chữ lớn theo định nghĩa WCAG.

**Giới hạn:** Không gọi cả PPTX đạt WCAG chỉ vì cặp màu đạt ngưỡng.

## S14 — The magical number 4

**EVIDENCE · Nelson Cowan / Cambridge.** [Nguồn](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/magical-number-4-in-shortterm-memory-a-reconsideration-of-mental-storage-capacity/44023F1147D4A1D44BDC0AD226838496) · Truy cập 2026-09-17.

Nghiên cứu 2001 về dung lượng trí nhớ ngắn hạn trong các điều kiện đo.

**Giới hạn:** Không gán 4±1 cho Miller; không suy ra mọi slide phải có bốn thẻ.

## S15 — Nine Ways to Reduce Cognitive Load

**EVIDENCE · Mayer & Moreno.** [Nguồn](https://www.tandfonline.com/doi/abs/10.1207/S15326985EP3801_6) · Truy cập 2026-09-17.

Nguồn nghiên cứu dự kiến đọc bổ sung.

**Giới hạn:** Lần mở này lỗi truy cập; không nhận đã đọc toàn văn, không dùng làm bằng chứng mới trong gói.

## S16 — Visual design principles

**HEURISTIC · Nielsen Norman Group.** [Nguồn](https://www.nngroup.com/articles/principles-visual-design/) · Truy cập 2026-09-17.

Phân cấp, tỷ lệ, tương phản, cân bằng và nhóm thị giác là tham khảo thiết kế.

**Giới hạn:** Chuyển từ UX sang slide là vận dụng của gói, không là phép đo hiệu quả slide.

## S17 — F-shaped reading

**EVIDENCE · Nielsen Norman Group.** [Nguồn](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/) · Truy cập 2026-09-17.

F là một trong nhiều kiểu đọc trên web, không phải quy luật duy nhất.

**Giới hạn:** Không áp như luật mắt luôn quét F/Z trên slide.

## S18 — The Glance Test

**HEURISTIC · Duarte.** [Nguồn](https://www.duarte.com/resources/guides-tools/the-glance-test/) · Truy cập 2026-09-17.

Phép thử nhận ra điểm chính nhanh và giảm nhiễu.

**Giới hạn:** Thời gian nhìn nhanh là phương pháp thực hành, không hằng số sinh học.

## S19 — Slideuments

**HEURISTIC · Garr Reynolds.** [Nguồn](https://www.presentationzen.com/presentationzen/2006/04/slideuments_and.html) · Truy cập 2026-09-17.

Phân biệt tài liệu đọc với phương tiện hỗ trợ nói.

**Giới hạn:** Không đồng nghĩa slide đào tạo phải chỉ có một từ và một hình.

## S20 — Approach

**HEURISTIC · Assertion-Evidence.** [Nguồn](https://www.assertion-evidence.com/) · Truy cập 2026-09-17.

Tiêu đề nêu thông điệp và bằng chứng thị giác thay cho danh sách chủ đề.

**Giới hạn:** Đã đọc trang giới thiệu; không tải hoặc phân phối template của tác giả.

## S21 — Presentation templates

**INSPIRATION · Microsoft.** [Nguồn](https://create.microsoft.com/en-us/templates/presentations) · Truy cập 2026-09-17.

Tham khảo bộ mẫu chính hãng và nhịp trang.

**Giới hạn:** Không đóng gói tài nguyên của nhà cung cấp.

## S22 — Infographics

**INSPIRATION · Slidesgo.** [Nguồn](https://slidesgo.com/infographics) · Truy cập 2026-09-17.

Tham khảo biến thể infographic và nhóm hình.

**Giới hạn:** Không là bằng chứng khoa học; kiểm tra giấy phép tài nguyên trước dùng.

## S23 — Presentation templates

**INSPIRATION · Envato.** [Nguồn](https://elements.envato.com/presentation-templates) · Truy cập 2026-09-17.

Tham khảo nhiều dạng trang và thiết kế theo bộ.

**Giới hạn:** Không sao chép template trả phí vào gói.

## S24 — Presentation templates

**INSPIRATION · Canva.** [Nguồn](https://www.canva.com/presentations/templates/) · Truy cập 2026-09-17.

Trang trả Unsupported client trong lần mở.

**Giới hạn:** Chưa đánh giá mẫu cụ thể; không dùng làm căn cứ kết luận.
