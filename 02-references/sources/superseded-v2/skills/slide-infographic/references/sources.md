---
title: Evaluated External Sources
status: evaluated_not_adopted
checked: 2026-09-14
---

# Nguồn đã đánh giá, chưa adopt

**NOT ADOPTED trong revision này.** Các đề xuất từ nguồn ngoài dưới đây chưa được người dùng xác nhận sau cổng khuyến nghị. Bảng này chỉ giữ provenance và quyết định đánh giá; không kích hoạt nội dung upstream, không vendor/copy skill, không thêm dependency. Skill hiện tại được viết độc lập từ yêu cầu của sản phẩm và các vấn đề đã ghi nhận trong dự án.

| Nguồn đã xem | Revision và license | Khuyến nghị để xem xét sau | Loại khỏi phạm vi hiện tại |
|---|---|---|---|
| [Presenton skills — html-format.md](https://github.com/presenton/skills/blob/bab82f10b0a77d4c8248c034f61e6bcb315a4982/skills/presenton/references/html-format.md) | SHA `bab82f10b0a77d4c8248c034f61e6bcb315a4982`; Apache-2.0 theo lần kiểm nguồn của dự án; checked 2026-09-14 | Cân nhắc tiêu chí khung slide, nội dung không tràn và phân biệt chữ riêng với chữ nằm trong ảnh khi đánh giá Phase 2 | Không áp canvas 1280×720 thành chuẩn duy nhất; không dùng API upload/export, CDN, Tailwind/Chart.js bắt buộc hoặc script quản lý file của Presenton |
| [Microsoft/ReDeck — visual_judge.system.md](https://github.com/microsoft/ReDeck/blob/fc2a277c3925d66c5f29f8120b8be54ddb39ec68/app/prompts/evaluator/visual_judge.system.md) | SHA `fc2a277c3925d66c5f29f8120b8be54ddb39ec68`; MIT theo lần kiểm nguồn của dự án; checked 2026-09-14 | Cân nhắc cách yêu cầu reviewer chỉ lỗi thị giác cụ thể với bằng chứng ảnh trong đợt thiết kế eval riêng | Không chép prompt judge, không dùng thang điểm hay điểm tổng của ReDeck làm chứng nhận nội dung/quyền/editability; không chạy pipeline ReDeck |

Hai URL ở trên ghim revision đã đánh giá, không tuyên bố đó là HEAD mới nhất. License ghi theo kiểm tra provenance của dự án, không là giấy phép cho mọi asset/model/dependency liên quan. Nếu sau này adopt, kiểm lại file/license đúng revision, phạm vi quyền và nghĩa vụ attribution trước khi copy hoặc phân phối; ghi rõ phần thật sự được đưa vào.

**Anthropic pptx:** đã loại khỏi phương án sao chép do điều khoản nguồn hạn chế/all-rights-reserved trong lần rà soát dự án. Không sao chép nội dung, prompt hoặc helper của skill đó. Không suy license của thư mục pptx từ license chung của một repository khác; bản hiện tại không phụ thuộc skill đó.

Căn cứ nội bộ cho bản viết độc lập: [đặc tả](../../../docs/superpowers/specs/2026-09-14-slide-infographic-design.md), [kế hoạch specialist](../../../docs/superpowers/plans/2026-09-14-slide-infographic-b-skill.md) và [giới hạn baseline](../evals/cases.md). Những kế hoạch rộng hơn có runtime/HTML là lịch sử thiết kế; phạm vi hoạt động của gói này là Markdown cho Codex Image, không tự mở Phase 2.
