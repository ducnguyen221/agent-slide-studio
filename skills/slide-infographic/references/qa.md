---
title: Infographic Image QA and Handoff
status: manual_qa_guide
---

# Kiểm ảnh thật và ghi đúng mức hoàn tất

Áp dụng sau mỗi ảnh tạo/chỉnh sửa. Prompt, tên file và lời tool “thành công” không thay cho số đo và việc mở xem ảnh. Dùng ảnh đúng revision đang bàn giao, không ảnh thumbnail hoặc ảnh cũ.

## Thứ tự kiểm

1. **File và canvas:** lấy width/height từ metadata file bằng công cụ sẵn có; ghi raw dimensions. Tỷ lệ đúng khi width×target-height bằng height×target-width; exact-size còn cần hai chiều pixel bằng yêu cầu. Không đo từ khung preview đã co. Không đọc được dimensions → dimensions unverified.
2. **Toàn cảnh:** xem ảnh như trên slide để kiểm điểm nhìn, hướng đọc, phân cấp, tương phản, khoảng trắng. Kiểm đủ nhóm, thứ tự, loại/hướng cạnh; cycle phải khép vòng. Lề được đo/ước lượng phải ghi đúng loại bằng chứng.
3. **Chi tiết:** mở vùng title, từng card, số liệu và mép ảnh ở độ phân giải đủ đọc. So từng chuỗi với canonical, đặc biệt dấu tiếng Việt, chữ hoa, dấu câu, số thập phân và đơn vị. OCR chỉ hỗ trợ; không thay lần xem trực tiếp. Chữ quá nhỏ/mờ để quyết định → unverified, không “có vẻ đúng”.
4. **Crop và chồng lấn:** kiểm dấu tiếng Việt, icon, card và mũi tên không bị cắt; vùng chữ không đè hình quan trọng. Hình không crop chưa chứng minh khung slide chứa trọn khi chèn; kiểm lại sau insertion nếu bước đó được giao.
5. **Theo mode:** TEXT_SAFE không có chữ nhúng và có vùng đủ trống; bảng chữ đủ nguyên văn nhưng lớp overlay vẫn chưa tạo. DIRECT_TEXT phải đọc đúng từng chuỗi hiển thị. NO_TEXT phải không có chữ/số/giả chữ, kể cả nền và góc ảnh.
6. **Handoff:** prompt đúng bản đã gửi, số call không bỏ sót edit/retry, giới hạn và editability đúng artifact. Chỉ có ảnh thì khai raster; bảng overlay không chứng minh đã có text box PowerPoint.

## Kết luận

| Trạng thái | Điều kiện | Việc tiếp theo |
|---|---|---|
| `passed` | Mọi cổng bắt buộc của output yêu cầu đã có bằng chứng đạt | Bàn giao đúng output; TEXT_SAFE chỉ pass phạm vi ảnh nền + bảng overlay-ready |
| `needs_revision` | Có lỗi cụ thể: sai chữ/số/quan hệ, crop, canvas hoặc đọc khó | Ghi lỗi và vị trí; đề xuất repair trong quyền/lượt còn lại |
| `unverified` | Thiếu ảnh, vision, số đo hoặc evidence cần thiết | Bàn giao phần đã có và phần cần người/tool kiểm; không ghi đạt |

Nếu vừa có lỗi đã biết vừa có phần chưa kiểm, kết luận needs_revision và giữ từng cổng còn thiếu là unverified. Không lặp generation chỉ để đổi trạng thái; hết lượt/repair=0 thì dừng. Timeout có outcome unknown chặn retry tự động kể cả còn trần lý thuyết.

## Mẫu bản ghi QA

Khối này là mẫu Markdown, điền bằng bằng chứng thật; dùng `unknown` cho metadata thiếu.

```markdown
# QA — {slide ID / revision}

- Canonical: {nguồn và revision được chọn; không public đường dẫn riêng}
- Mode / phạm vi output: {TEXT_SAFE/DIRECT_TEXT/NO_TEXT; ảnh nền hay ảnh hoàn chỉnh}
- Prompt: {bản thực đã gửi, revision hoặc file local}
- Artifact: {ảnh thực tương ứng; hash nếu đã đo}
- Canvas yêu cầu: {width×height; exact-size/exact-ratio; safe margins}
- Canvas thực: {width×height từ metadata; công cụ/cách đo hoặc unknown}
- Generation: {tool/host thực; model nếu biết; primary/edit calls; outcome}
- Lượt: {trần project/task biết được; trước/sau; lượt unknown chưa đối soát}
- Token / thời gian / cost: {số đo + cách đo, hoặc unknown; không suy cost=0}
- Transformations: {none hoặc thao tác thực và file kết quả; không ghi kế hoạch thành đã làm}

| Cổng | Trạng thái | Bằng chứng / lỗi / vùng |
|---|---|---|
| Dimensions và ratio | {passed/failed/unverified} | {...} |
| Nội dung, node, quan hệ | {...} | {...} |
| Chính tả, số và khả năng đọc | {...} | {...} |
| Crop, lề, chồng lấn | {...} | {...} |
| Phân cấp, tương phản, thứ tự đọc | {...} | {...} |
| Text policy và vùng overlay | {...} | {...} |
| Editability và bàn giao | {...} | {...} |

- Kết luận: {passed/needs_revision/unverified + phạm vi}
- Giới hạn: {phần chưa kiểm hoặc overlay chưa đặt}
- Repair: {lỗi cần sửa; quyền/lượt còn lại; hoặc dừng và lý do}
- Alt text: {mô tả ngắn hình và quan hệ}
- Chữ chính xác để đặt sau: {bảng overlay nếu TEXT_SAFE; NO_TEXT không có chữ hiển thị}
```

Nếu người dùng chỉ cần ảnh, handoff kết thúc ở đây. Khi được yêu cầu PowerPoint, chèn ảnh thủ công theo [workflow](../workflows/create-slide-infographic.md) rồi mở/xem lại slide thực. Không gọi ảnh nền là nguồn native; chỉ text box đã tạo và kiểm mới có thể được ghi editable.
