---
title: "Slide Design Playbook"
description: "Canonical design principles and end-to-end ImageGen workflow for ChatGPT Projects."
document_type: project-knowledge
status: active
---

# Slide Design Playbook

Đọc file này để hiểu toàn bộ quy trình, quy tắc thiết kế, content lock, style lock, cách gọi ImageGen và tiêu chuẩn QA. Nội dung đã được gộp từ các nguồn canonical; các liên kết nội bộ của repository đã được bỏ để file hoạt động độc lập khi upload.

---

## Điểm vào và các cổng bắt buộc

### Thiết kế slide bằng ImageGen

`SKILL_ROOT` là thư mục chứa file này. Mọi đường dẫn dưới đây tính từ `SKILL_ROOT`, không từ thư mục làm việc của người dùng. Root này là entrypoint active duy nhất; `v1/` và `02-references/sources/` chỉ để đối chiếu.

#### Đường đọc bắt buộc

1. Đọc nguyên tắc và hệ thiết kế một lần cho task.
2. Đọc toàn bộ deck và nguồn liên quan, rồi map **100% slide** theo bước 01 và deck plan. Chưa map đủ thì chưa tạo prompt hoặc ảnh.
3. Mở reference index, chọn mã L/I cho từng slide, rồi mở đặc tả, preview và **ảnh mẫu thật được bundle** mà index dẫn tới. Ghi rõ điều học và không học từ từng ảnh; không chọn từ thumbnail, tên file hoặc chữ/số trong ảnh.
4. Khóa content và style theo bước 02. Nếu thiếu bất kỳ quyết định brand, font appearance hoặc style nào, gom thành **một lượt hỏi người dùng**; chỉ tự chọn khi người dùng đã cho phép auto-choice.
5. Soạn prompt theo bước 03 và template. Prompt phải có đúng thứ tự `CANVAS`, `OBJECTIVE`, `COMPOSITION`, `STYLE`, `CONTENT`, `CONSTRAINTS`, `NEGATIVE`. `CONTENT` là allowlist đầy đủ: mọi chuỗi nhìn thấy phải xuất hiện nguyên văn, có ID; cấm sinh thêm chữ ngoài allowlist.
6. Dùng integration của host: Codex, Claude hoặc Antigravity. Chỉ gọi capability ImageGen native mà phiên hiện tại thực sự cung cấp; không đoán tên tool, model hoặc API.
7. Mở ảnh đúng revision ở kích thước đầy đủ và QA theo bước 04. Lỗi chữ, topology, crop, lề, độ đọc hoặc style phải được sửa bằng ImageGen edit/regenerate, tạo revision mới và QA lại **toàn ảnh**. Sau cùng kiểm consistency toàn deck và ghi handoff.

#### Cổng fail-closed

- Thiếu capability tạo/chỉnh ảnh native: trả `CAPABILITY_UNAVAILABLE`, giữ nguyên content lock và bàn giao prompt. Không fallback sang Python, HTML, SVG, browser/screenshot, PPTX overlay hoặc renderer khác.
- Timeout hoặc outcome không rõ: trả `OUTCOME_UNKNOWN`, kiểm lại cùng tác vụ nếu host hỗ trợ; không gửi lại mù.
- Không thấy được ảnh thật đầy đủ hoặc không đo được điều bắt buộc: trạng thái `unverified`, không tuyên bố PASS.
- ImageGen raster chỉ cho phép đánh giá font appearance. Không tuyên bố đã chứng minh font family, point size hoặc editability thật.

---

## Nguyên tắc kiến trúc slide

### Nguyên tắc thiết kế slide

Đọc file này một lần trước khi lập deck. Đây là nguồn canonical cho tư duy slide, mạch bài, mật độ và nhịp toàn bài; quy tắc hình thức nằm ở design-system.md.

#### Slide phục vụ một kết quả

Mỗi slide có một vai trò trong mạch bài, một thông điệp có thể nói thành câu và một quan hệ thị giác chính. Tiêu đề nên nêu kết luận hoặc hành động, không chỉ gọi tên chủ đề. Tách chữ hiển thị khỏi ghi chú giảng viên và nguồn; slide đào tạo phải hỗ trợ người học theo dõi, ghi nhớ và tra cứu nhưng không biến thành trang tài liệu đặc chữ.

Không ép nội dung vào số card có sẵn. Giữ đúng số bước, nhánh, tầng, tiêu chí và ngoại lệ của nghiệp vụ. Khi một trang cần hai luồng chính hoặc chữ phải thu nhỏ mới vừa, tách trang theo nhịp tổng quan → giải thích → ví dụ → thực hành.

#### Tổ chức nhận thức

- Dùng chữ và hình để bổ sung cho nhau. Hình neo, icon, card và đường nối phải giải thích ý nghĩa; chúng không chỉ trang trí.
- Gom các ý cùng chức năng thành cụm có ranh giới rõ. Ba đến năm cụm là điểm bắt đầu biên tập, không phải giới hạn khoa học.
- Thiết kế một đường đọc có chủ đích. Cấp bậc thường đi từ kicker/chủ đề → action title → hình neo hoặc khối chính → chi tiết → kết luận cần thiết.
- Dùng mũi tên chỉ khi có hướng, chuyển giao hoặc nhân quả. Vòng lặp phải có cạnh quay về; so sánh phải dùng cùng tiêu chí; ma trận phải có hai trục có nghĩa.
- Mỗi trang chỉ có một lớp trọng tâm. Công thức, cảnh báo hoặc takeaway chỉ thêm khi chúng hoàn tất thông điệp, không tạo một slide thứ hai ở chân trang.

#### Mật độ và bản chữ

`D0` không có chữ; `D1` là mặc định gọn; `D2` chỉ dùng khi người xem cần đọc sâu. Các ngưỡng 35–70 và 71–100 đơn vị cách trắng là quy ước biên tập của gói, không phải luật nhận thức hay token. Ưu tiên nhãn ngắn, một câu có ích cho mỗi khối và khoảng trắng đủ phân nhóm. Không bỏ ý, đổi số hoặc thu chữ để đạt ngân sách.

Mọi chữ hiển thị phải có ID ổn định và nguồn. Giữ nguyên tên riêng, cú pháp, số, dấu thập phân và đơn vị đã khóa. Phân biệt rõ nội dung từ nguồn, bổ sung có dẫn chứng, ví dụ giả định và đề xuất. Không tự thêm tỷ lệ hiệu quả, cam kết tuyệt đối hoặc tính năng chưa được xác minh.

#### Nhịp toàn bài

Sáu pattern `P01–P06` được giữ như nhãn nhịp, không phải bộ file riêng:

| ID | Mạch đề xuất | Khi dùng |
|---|---|---|
| P01 | Mở → bối cảnh → khái niệm → ví dụ → thực hành → chốt | Bài đào tạo chuẩn |
| P02 | Mục tiêu → đầu vào/đầu ra → tổng quan bước → điểm duyệt → thao tác → thực hành → việc tiếp theo | Hướng dẫn quy trình từ kết quả mong muốn đến làm thử có kiểm soát |
| P03 | Điều cần hiểu → các tầng → năng lực nền → mô-đun → ranh giới quyền → kiểm tra/đúc kết → lộ trình | Giải thích kiến trúc và năng lực từ tổng thể đến trách nhiệm từng phần |
| P04 | Đề xuất chính → vấn đề hiện tại → trạng thái cần chuyển → phương án → bằng chứng → điều kiện chọn → quyết định | Đề xuất thay đổi dựa trên vấn đề, lựa chọn, bằng chứng và quyết định |
| P05 | Kết luận → chỉ số chính → biến động → đóng góp tăng/giảm → yếu tố tác động → hành động | Báo cáo dữ liệu từ thông điệp đến chỉ số, lý giải và hành động |
| P06 | Kết quả buổi học → nguyên lý → đọc mẫu → lỗi thường gặp → bài tập → rút bài học → áp dụng | Workshop thực hành theo nhịp hiểu mẫu, xem cách làm, tự làm và phản hồi |

Chọn pattern theo outcome, rồi thay đổi layout theo quan hệ thật. Một mạch deck mới không khớp sáu pattern dùng `custom`; không đổi nghĩa P01–P06 để ép khớp. Không luân phiên mẫu chỉ để tạo cảm giác đa dạng. Dùng slide neo đại diện để kiểm style trước khi sinh cả deck.

#### Cổng quyết định

Trước khi sang workflow tạo ảnh, deck phải có đủ slide ID, vai trò, thông điệp, nguồn, exact visible text, topology, mã L/I, density, reference và trạng thái. Chọn mã bằng INDEX, rồi mở đặc tả và ảnh thật tương ứng; không quyết định từ thumbnail hoặc tên mẫu.

---

## Hệ thiết kế

### Hệ thiết kế

Đây là nguồn canonical cho canvas, lưới, màu, font appearance, icon, bề mặt, tiêu đề và chân trang. Khóa thiết kế theo brief người dùng trước; các giá trị dưới đây chỉ là baseline khi brief chưa quy định.

#### Canvas và lưới

- Mặc định 16:9, tham chiếu 1920×1080. Ghi riêng kích thước yêu cầu và kích thước ảnh thật.
- Baseline lề: trái/phải 100 px, trên 90 px, dưới 80 px. Có thể dùng lề 5% khi canvas khác; mọi chữ, card, icon mang nghĩa và đầu mũi tên phải nằm trong vùng an toàn.
- Dùng grid, baseline, gutter và padding đều. Căn mép card trước khi thêm bóng hoặc vật liệu.
- Title zone nên ổn định trong deck. Nội dung bắt đầu dưới title zone; footer chỉ xuất hiện khi thêm nguồn, điều kiện hoặc kết luận chưa có ở phần chính.

#### Cấp bậc chữ

ImageGen chỉ tạo **font appearance**, không chứng minh font family hoặc point size thật. Yêu cầu hình dáng chữ rõ, tương phản, cùng hệ weight và đúng dấu tiếng Việt. Với PowerPoint, mục tiêu thường là title 32–40 pt và body 20–24 pt; 18 pt là sàn nội bộ cần kiểm ở phòng chiếu, không phải bảo đảm phổ quát. Nếu thiếu chỗ, rút gọn có duyệt hoặc tách slide.

#### Màu và bề mặt

Màu theo vai trò: màu cấu trúc, màu nhấn, màu trạng thái và màu nền. Không dùng màu là dấu hiệu duy nhất. Không mặc định áp navy/xanh/cam của AIA/KPIM nếu người dùng chưa cấp brand; khi cần baseline trung tính có thể đề xuất nền sáng, chữ tối và một accent rồi ghi rõ là giả định.

Giữ một ngôn ngữ bề mặt trong cả deck: flat/outline, 3D mềm hoặc isometric tinh giản. Không trộn ảnh thật, icon nét và vật thể 3D trong cùng hệ nếu không có lý do. Bóng nhẹ tạo tách lớp; glow, kính, gradient và texture không được làm giảm khả năng đọc.

#### Icon, hình neo và đường nối

Mỗi khối có tối đa một hình neo chính, cùng góc nhìn, độ nét và hướng sáng. Hình phải mô tả chức năng cụ thể; tránh robot chung cho mọi ý. Connector không xuyên chữ/icon, có điểm đầu/cuối rõ và chỉ dùng hai chiều khi có phản hồi thật.

#### Hai profile tham khảo

- **Light corporate cards:** title chiếm khoảng 14–18% chiều cao; lưới 2×2 hoặc ba cột, card cùng kích thước, gutter rộng, nền trắng/xanh rất nhạt, accent tiết chế. Phù hợp nhóm ngang hàng và so sánh; không phù hợp quy trình nhiều nhánh hoặc body dài.
- **Complex process flow:** 4–7 lane theo trục ngang, cùng baseline, một loại mũi tên cho luồng chính và đường thứ cấp cho tối đa một feedback loop. Phù hợp handoff/gate; nhiều loop hoặc nhánh chéo phải tách slide.

#### Ảnh tham chiếu

Mở ảnh thật ở kích thước đầy đủ trước khi dùng. Ghi riêng phần học: geometry, khoảng trắng, palette, icon, material hoặc hierarchy. Ghi phần không học: chữ, số liệu, logo, chân dung, tên tổ chức, tuyên bố tính năng và dữ liệu nghiệp vụ. Một reference chỉ cấp bằng chứng cho điều nhìn thấy; quyền dùng nội bộ không tự thành quyền phân phối.

#### Kiểm style lock

Style lock tối thiểu gồm canvas, lề, title zone, font appearance, palette theo vai trò, surface, icon language, connector, density, footer và reference scope. Một slide neo phải đạt QA trước khi dùng làm reference cho các slide sau. Drift về margin, title alignment, icon language hoặc vai màu là lỗi toàn deck.

---

## Workflow 01 — Đọc và lập bản đồ deck

### 01 — Đọc nguồn và lập bản đồ deck

**Đầu vào:** deck/tài liệu thật, mục tiêu, người xem, phạm vi và nguồn liên quan.  
**Đầu ra:** deck-plan đã map 100% slide.

1. Đọc toàn bộ deck và các nguồn được giao; không coi snippet là toàn tài liệu. Ghi tệp, mục/trang, revision và phần chưa đọc.
2. Xác định outcome, thông điệp xuyên suốt và nhịp P01–P06 hoặc mạch riêng trong principles.
3. Với mỗi slide, gán ID ổn định, vai trò, một thông điệp, exact visible text, số/đơn vị, nguồn, topology, density và trạng thái.
4. Phân biệt chữ hiển thị, ghi chú giảng viên, căn cứ và đề xuất mới. Không sửa luận điểm hoặc làm mất ngoại lệ để vừa bố cục.
5. Mở reference INDEX, chọn một mã L/I chính và tối đa hai ứng viên. Chọn intent/topology trước style.
6. Mở đặc tả layout và PNG/SVG thật của mã đã chọn. Nếu dùng ảnh mẫu, mở file ảnh gốc và ghi rõ học/không học; thumbnail và tên file không đủ.
7. Kiểm nhịp toàn deck: không lặp layout vô thức; chuyển hợp lý từ khái niệm đến bằng chứng, ứng dụng và thực hành.

Claim cập nhật, số liệu hoặc tính năng phải có nguồn chính thức/đáng tin cậy, ngày hoặc phiên bản khi cần. Ảnh mẫu không là nguồn nội dung. Claim chưa xác minh phải được đánh dấu, sửa có duyệt hoặc bỏ khỏi visible text.

Chỉ chuyển bước khi mọi slide đều được map. Thiếu source, ảnh đích hoặc quyết định có thể đổi nghĩa thì gom câu hỏi thành một lượt ngắn; không hỏi lại điều đã có.

---

## Workflow 02 — Khóa style và nội dung

### 02 — Khóa style và nội dung

**Đầu vào:** deck plan đủ slide, nguồn, layout/ảnh đã mở.  
**Đầu ra:** style lock và content lock cho từng slide.

1. Khóa canvas, lề, title zone, font appearance, palette theo vai trò, surface, icon, connector, density và footer theo design system. Thiếu brand/font/style thì hỏi một lượt, trừ khi user đã cho phép tự chọn; không tự áp nhận diện AIA navy/xanh/cam.
2. Chọn một ảnh neo đạt chất lượng. Với mỗi reference, ghi file thực đã mở, đặc tính học và đặc tính cấm kế thừa. Không trộn sáu style thành collage.
3. Gán ID cho mọi chuỗi hiển thị. Khóa chính tả, dấu, tên riêng, cú pháp, số, đơn vị, node, cạnh, thứ tự và ngắt dòng được phép.
4. Mọi chữ nhìn thấy dùng tiếng Việt, trừ tên chính thức, tên tệp hoặc cú pháp đã khóa. Không tự thêm bản dịch tiếng Anh trong ngoặc.
5. Tách nguồn người dùng, bổ sung có nguồn, ví dụ giả định và đề xuất. Khi nguồn mâu thuẫn, ghi khác biệt và quyết định; không hòa giải âm thầm.
6. Với edit, mở đúng ảnh đích, mô tả vùng được sửa và vùng khóa; lưu revision mới. Không hứa giữ pixel ngoài vùng nếu công cụ không bảo đảm.
7. Chọn slide neo và khóa đầy đủ brief của nó: content lock, layout, style lock, reference scope, prompt constraints và tiêu chí QA. Bước này chưa gọi ImageGen và chưa tạo ảnh.

Không sang bước 03 nếu còn placeholder, chữ chưa khóa, reference chưa mở, brand decision chưa chốt hoặc nội dung không fit. Cách xử lý là biên tập có duyệt, đổi layout hoặc tách slide; không thu chữ hay bỏ ý âm thầm. Bước 03 là điểm duy nhất được generation.

---

## Workflow 03 — Soạn prompt và gọi ImageGen

### 03 — Soạn prompt và gọi ImageGen

**Đầu vào:** deck plan, style lock, content lock và ảnh tham chiếu đã mở.  
**Đầu ra:** prompt tự đủ nghĩa, generation record và ảnh thật hoặc trạng thái fail-closed.

#### Prompt bảy phần

Mỗi prompt có đúng thứ tự sau; nội dung chỉ xuất hiện một lần:

```text
CANVAS | kích thước/tỷ lệ; safe margins; nền; title zone.
OBJECTIVE | một câu về thông điệp, người xem và vai trò slide.
COMPOSITION | vùng, topology, thứ tự đọc, node/cạnh và điểm nhấn.
STYLE | style lock, font appearance, palette, icon, material.
CONTENT | ID + exact visible text, số, đơn vị và ngắt dòng cho phép.
CONSTRAINTS | bất biến, reference scope, số node/cạnh, vùng khóa.
NEGATIVE | lỗi thị giác/nội dung phải tránh, không lặp phần trên.
```

Prompt phải tự đủ nghĩa; ImageGen không thể đọc repo hoặc bảng ngoài prompt. ID là chỉ dẫn, không được in trừ khi nó là visible text. Direct text là mặc định theo hợp đồng ImageGen-only. Nếu lượng chữ không thể đọc được, đề xuất biên tập/tách slide trước khi gọi; không tự chuyển sang overlay, Python, SVG, HTML, screenshot hoặc renderer khác.

#### Gọi và ghi nhận

1. Kiểm tool native của host, quyền dùng reference và phạm vi task. Không hardcode model/API không được host công bố.
2. Chạy preflight cho slide neo đã khóa ở bước 02: prompt đủ bảy phần, không placeholder, content/style/reference lock đầy đủ, tool/capability và outcome trước đó rõ ràng.
3. Tại đây, gọi ImageGen đúng một lần đầu tiên cho slide neo. Mở ảnh neo thật và QA theo bước 04; chỉ khi ảnh neo đạt mới dùng nó làm style reference nếu tool hỗ trợ.
4. Sau anchor gate, gọi ImageGen cho từng slide phụ thuộc với prompt đã khóa. Tạo mới không đính kèm reference không cần thiết; edit phải truyền đúng ảnh đích.
5. Ghi slide ID, revision, host, tool/model nếu biết, prompt thực, reference, output path/handle, kích thước thật và outcome. Trường thiếu ghi `unknown`.
6. Timeout/chưa rõ kết quả trả `OUTCOME_UNKNOWN`; kiểm cùng tác vụ nếu host cho phép, không gửi lại mù. Thiếu capability trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt, không fallback renderer.
7. Mọi repair phải gắn lỗi QA cụ thể, tạo revision mới và QA lại toàn ảnh.

---

## Workflow 04 — Review và bàn giao

### 04 — Review ảnh thật và bàn giao

**Đầu vào:** ảnh đúng revision, prompt, deck plan, style/content lock.  
**Đầu ra:** review-and-handoff với `passed`, `needs_revision` hoặc `unverified`.

1. Đọc metadata file để ghi width×height thật; phân biệt exact size với exact ratio.
2. Mở toàn ảnh ở kích thước đầy đủ. Kiểm điểm nhìn, thứ tự đọc, phân cấp, khoảng trắng, style lock và vai màu.
3. So từng chuỗi với content lock: dấu tiếng Việt, chữ hoa, dấu câu, tên riêng, số, đơn vị và ngắt dòng. Một ký tự sai là lỗi.
4. Kiểm node, cạnh, thứ tự, nhánh và topology; cycle phải khép kín, mũi tên không xuyên chữ.
5. Kiểm crop, overlap, safe margin, title/footer, độ đọc khi trình chiếu và chi tiết giả chữ/watermark/logo.
6. Kiểm consistency toàn deck: canvas, title alignment, palette, font appearance, icon/material, card radius, connector và density.
7. Sửa theo thứ tự: nghĩa/nội dung → chữ/số → topology → crop/lề/độ đọc → style/trang trí. Mỗi edit phải QA lại.

`passed` chỉ khi mọi cổng bắt buộc có bằng chứng. Lỗi cụ thể là `needs_revision`; thiếu ảnh, vision hoặc số đo là `unverified`. Prompt/tool success/tên file không thay bằng chứng nhìn ảnh. Raster không chứng minh font metadata hoặc editability; nếu user yêu cầu exact font family/point size, ghi giới hạn ImageGen-only.

Bàn giao gồm ảnh đúng revision, prompt thực, content lock, generation record, QA từng slide, QA toàn deck, alt text, phần chưa kiểm và cách mở artifact. Chỉ tạo PowerPoint khi được giao riêng; ảnh đặt vào PPTX vẫn là raster.
