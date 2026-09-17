---
title: Slide Infographic Evaluation Rubric
status: evaluation_guide
updated: 2026-09-14
---

# Rubric: quyết định đúng và ảnh đạt là hai kết quả riêng

Áp dụng cho [cases](cases.md), [skill](../SKILL.md) và [workflow](../workflows/create-slide-infographic.md). Đây là hướng dẫn chấm thủ công; không có scorer/runtime trong gói này.

## Các cổng độc lập

| Cổng | Đạt khi | Bằng chứng tối thiểu |
|---|---|---|
| C1 — Phạm vi và nội dung | Chọn đúng slide; giữ chữ, số, đơn vị, quan hệ; không tự tóm tắt/đổi dữ kiện | Canonical và prompt/bảng overlay đối chiếu theo ID |
| C2 — Quyền và call | Đúng tool/quyền/trần; không dispatch khi cap=0; unknown không tự retry | Quyết định và lịch sử call thực; giả định phải ghi rõ |
| C3 — Prompt và mode | Đủ bảy section, mode hợp nội dung, style không lặp, không đưa body vào TEXT_SAFE | Prompt thực gửi, bảng nội dung đi kèm |
| C4 — Ảnh | Đúng canvas đã chốt; không crop nội dung; đủ node/cạnh; chữ đúng và đọc được | Ảnh đúng revision, số đo file, xem tổng thể và chi tiết |
| C5 — Claim và bàn giao | Khai raster/overlay-ready chính xác; đủ prompt, ảnh, QA, giới hạn | Artifact hiện có và bản ghi [QA](../references/qa.md) |

Mỗi cổng nhận `passed`, `failed`, `unverified` hoặc `not_applicable` kèm lý do. `not_applicable` chỉ dùng khi tiêu chí không thuộc output yêu cầu, ví dụ chính tả chữ nhúng với NO_TEXT; kiểm không có chữ vẫn áp dụng. Thiếu ảnh hoặc không vision là `unverified` cho C4. Trả lời đúng trong tình huống giả định có thể đạt quyết định C1–C3, nhưng C4 và generation thực vẫn `unverified`.

Không lấy điểm thẩm mỹ trung bình bù lỗi nội dung/quyền. Một lỗi dấu, một số liệu sai, một cạnh bắt buộc mất, hoặc khai raster thành editable khiến output tương ứng `needs_revision`. Lỗi phạm vi/quyền chặn dispatch; ảnh đẹp không đổi kết luận.

## Nhận xét thiết kế có thể hành động

Ghi cụ thể vị trí và hệ quả: “card 5 bị cắt ở mép phải” hoặc “mũi tên cuối chưa quay về nút 1”. Xem phân cấp, thứ tự đọc, khoảng trắng, nhất quán icon/màu và mức đọc được khi đặt lên slide mục tiêu. Không ghi “rất đẹp” thay bằng chứng. Không có số đo công cụ thì mô tả là quan sát thị giác, không bịa metric.

## Báo cáo thực nghiệm

Mỗi case ghi riêng: số control, số variant, số pass/fail/unverified theo cổng, evidence đọc được, call thực, thời gian và token/cost nếu đo được. Ghi độ phân tán giữa các lần, không chỉ chọn ảnh đẹp nhất. Token ước tính phải nêu cách ước tính; thiếu tokenizer thì dùng số ký tự/từ và ghi token `unknown`.

Thay wording sau khi thấy lỗi thì chạy lại case đó và regression liên quan. Không sửa expected để hợp output. Phân biệt “đã kiểm cấu trúc tài liệu”, “đã kiểm hành vi agent”, “đã sinh/xem ảnh”, “đã chèn/mở PowerPoint”; chỉ chứng nhận phần có evidence.

Mốc hiện tại chỉ bàn giao hướng dẫn Markdown. Không đánh dấu GREEN, đạt first-try, sẵn sàng release hoặc đã tối ưu tỷ lệ thành công khi chưa chạy thực nghiệm tương ứng.
