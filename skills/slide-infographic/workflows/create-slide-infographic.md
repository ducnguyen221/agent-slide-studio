---
title: Slide Infographic Image Process
status: documentation_only
updated: 2026-09-14
---

# Từ nội dung một slide đến ảnh đã kiểm

Quy trình này dành cho Codex host có imagegen, dùng [skill](../SKILL.md) và [hợp đồng agent](../agents/slide-infographic-agent.md). Đây là mốc **Markdown-only**; không có script, CLI mới, lớp overlay tự động hay renderer mới. Đặc tả kiến trúc rộng hơn không phải bằng chứng các capability đã triển khai.

## Lựa chọn trước khi tạo

| Cách làm | Đánh đổi và rủi ro | Công sức | Khi chọn |
|---|---|---|---|
| **TEXT_SAFE — khuyến nghị** | Chữ chính xác giữ riêng; cần bước đặt chữ để thành slide có nội dung đầy đủ | Thấp cho ảnh, thêm thao tác overlay | Chữ Việt cần chính xác, nội dung dài hoặc cần sửa chữ |
| DIRECT_TEXT | Có ảnh hoàn chỉnh nhanh; chữ có thể sai, khó sửa riêng, phải xem từng nhãn | Thấp khi đúng, có thể tăng do repair | Ít nhãn ngắn, chấp nhận best-effort và raster |
| NO_TEXT | Chỉ giao hình; thông điệp dựa vào hình hoặc lớp chữ khác do người dùng quản lý | Thấp | Nền/minh họa không cần chữ |

## Các bước và đầu ra

1. **Intake.** Chọn đúng slide, nội dung, audience, đầu ra và reference. Dùng 1920×1080/16:9/lề 5% khi chưa có lựa chọn khác, nêu đó là giả định. Giữ 4:3 hoặc custom khi đã yêu cầu. Xác định cần exact-size hay chỉ exact-ratio; mặc định exact-size.
2. **Chuẩn hóa canonical.** Lập bảng ID → chữ nguyên văn/số/đơn vị, thứ tự đọc và cạnh. Đối chiếu với nguồn đã chốt; nguồn bất đồng cần hòa giải. Không biên tập âm thầm. Chỉ slide/reference đã chọn đi vào generation.
3. **Chọn mode.** TEXT_SAFE giữ chữ ở bảng overlay; DIRECT_TEXT đưa ít chuỗi ngắn vào ảnh; NO_TEXT không có chữ. Khối lượng chữ không fit thì đề xuất thay layout/chia slide, chưa tự bỏ nội dung.
4. **Biên soạn.** Dùng [bảy section và template](../references/prompt-compiler.md). Chọn số vùng theo số node; giữ hướng/loại quan hệ, style chung một lần. Bảng overlay nằm ngoài prompt ảnh với TEXT_SAFE.
5. **Preflight.** Kiểm đủ nội dung, canvas/lề, mode, vùng chữ, node/cạnh và prompt không còn placeholder. Xác nhận tool khả dụng, quyền task/reference, trần project/host và số call còn lại. Cap=0 thì không call. Nếu project có protocol/accounting bắt buộc, chỉ dùng đường đã được cung cấp và kiểm; thiếu protocol không giả bằng ghi chú thủ công hoặc gọi trực tiếp để vượt cổng. Với task host độc lập, ghi căn cứ và call budget trong QA, không khai đã tạo ledger runtime.
6. **Gọi imagegen một lần.** Dùng prompt đã khóa theo schema tool hiện hành. Lưu prompt và kết quả trả thật; metadata không biết ghi unknown. Mục tiêu một primary attempt, không có bảo đảm lần đầu. Tool chạy còn tiếp diễn thì theo dõi cùng tác vụ; timeout/outcome unknown không gửi lại tự động.
7. **Kiểm ảnh thực.** Dùng [QA](../references/qa.md): đo dimensions, xem toàn ảnh và chi tiết, đối chiếu dấu/số/quan hệ, crop, legibility và phân cấp. Không dùng câu “1920×1080” trong prompt để chứng minh canvas. TEXT_SAFE kiểm vùng đặt chữ, chưa chứng nhận slide hoàn chỉnh.
8. **Kết luận và repair.** Passed chỉ khi đủ evidence cho output đã chốt. Lỗi cụ thể → needs_revision; thiếu evidence → unverified. Repair phải có lỗi/vị trí, còn quyền/lượt, outcome cũ rõ và không vượt trần project. Giữ prompt/ảnh revision trước; ảnh mới phải QA lại toàn bộ phần quan trọng. Hết giới hạn thì bàn giao lỗi còn lại, không lặp vô hạn.
9. **Handoff.** Giao ảnh, prompt thực, canonical/overlay table nếu cần, QA record, alt text và giới hạn. Output riêng ở workspace người dùng đã chọn, không đưa nội dung riêng vào public repo. Chỉ chứa ảnh thì khai raster; không hứa PowerPoint editable. Mốc tài liệu kết thúc ở việc chuẩn bị hướng dẫn và biểu mẫu này; thực nghiệm chạy ảnh có trạng thái riêng trong [evals](../evals/cases.md).

## Chèn PowerPoint thủ công — tùy chọn

Chỉ làm khi người dùng yêu cầu. Chọn kích thước slide đúng tỷ lệ trước, chèn ảnh và giữ tỷ lệ ảnh. Nếu lệch canvas, dùng contain có lề khi được chọn; không kéo méo hoặc crop mất nội dung. Với TEXT_SAFE, tạo text box theo bảng nguyên văn, điều chỉnh vị trí/font để đọc được; giữ chữ đúng, báo nếu không đủ chỗ. Kiểm lại slide tổng thể và từng nhãn sau khi đặt chữ.

Ảnh nền vẫn raster; text box mới là phần sửa được. Ghi “mixed” chỉ khi lớp chữ thực đã tạo và kiểm, không suy từ kế hoạch overlay. Mở/xem slide kết quả khi bàn giao PPTX; chưa làm bước đó thì nói chưa kiểm PowerPoint.

## Sau mốc này

HTML reconstruction, nguồn web sửa từng đối tượng, automatic overlay và tích hợp backend là **Phase 2 planned** hoặc công việc riêng. Không triển khai tiếp chỉ vì tài liệu này có mặt. [Nguồn ngoài](../references/sources.md) giữ trạng thái đã đánh giá/chưa adopt.
