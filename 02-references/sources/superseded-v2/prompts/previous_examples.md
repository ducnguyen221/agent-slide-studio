> Bản nguồn kế thừa v20. Khi có khác biệt, dùng SKILL.md và tài liệu hiện hành; xem references/migration.md.

# Mẫu yêu cầu và bộ prompt tạo ảnh

Các mẫu là đặc tả biên tập cho dự án, không phải tuyên bố tính năng chính thức của bất kỳ sản phẩm nào. Chọn đúng chế độ và bỏ phần không áp dụng; không in các chỉ dẫn kỹ thuật lên ảnh.


## Phiếu yêu cầu slide

- Mã slide / phiên bản: [AIA102-Sxx / v01]
- Mục tiêu: [Người xem hiểu hoặc làm được điều gì?]
- Người xem: [Nhân viên hành chính / quản lý / học viên kỹ thuật...]
- Nguồn và nội dung gốc: [Dán nội dung hoặc nêu tệp/trang]
- Thông điệp cần giữ: [Một câu]
- Kiểu đầu ra: [A hoàn chỉnh / B chừa tiêu đề / C không chữ]
- Tiêu đề: [Giữ nguyên / đề xuất / để trống]
- Bố cục: [Mã L01–L20 / AI tự chọn]
- Mật độ: [Gọn / tiêu chuẩn / chi tiết]
- Phong cách: [TRANG-SANG / MO-CHUONG-TOI / ảnh tham chiếu]
- Từ phải giữ nguyên: [Tên sản phẩm, AGENTS.md, SKILL.md...]
- Phạm vi tham chiếu ảnh: [Màu / biểu tượng / bố cục / toàn bộ]
- Điều không được thay đổi: [...]
- Đầu ra lượt này: [Phác thảo / prompt / ảnh / bản Word]


## Công thức prompt tạo ảnh độc lập

## 1. Sản phẩm và mục tiêu
Tạo [một infographic hoàn chỉnh / infographic chừa tiêu đề / hình không chữ] dùng trong PowerPoint 16:9. Mục tiêu người xem: [mục tiêu]. Chỉ làm một trang, không ghép nhiều slide vào một ảnh.

## 2. Hình học
Khung thiết kế 1920 × 1080; lề trái/phải 100 px, trên 90 px, dưới 80 px. [Chỉ định vùng trống nếu có]. Nội dung quan trọng nằm hoàn toàn trong vùng an toàn.

## 3. Bố cục và đường đọc
Dùng [Lxx — tên bố cục]. Sắp xếp [vị trí, tỷ trọng từng vùng]. Có chính xác [n] cụm. Đường nối: [điểm đầu, điểm cuối, chiều, ý nghĩa]. Vùng trọng tâm là [vùng].

## 4. Phong cách
Nền [màu], chữ navy #0A192F, nhấn [hai màu]. Thẻ bo góc, bóng nhẹ, biểu tượng [vector hoặc 3D mềm] đồng nhất. Chữ phẳng rõ; không ánh sáng đi qua vùng chữ; không thêm thương hiệu.

## 5. Chữ chính xác phải xuất hiện
Tiêu đề: “[tiêu đề đã duyệt]”
Phụ đề: “[nếu có]”
Cụm 1: “[tên]” / “[ý 1]” / “[ý 2]” / “[đầu ra nếu cần]”.
Cụm 2: [...]
Nhãn mũi tên: [...]
Chân trang: “[một câu đã duyệt, nếu cần]”.
Chỉ các mục trong danh sách này được render; chỉ dẫn bố cục không được in lên ảnh.

## 6. Hình neo
Cụm 1: [biểu tượng cụ thể, vật liệu, màu, hướng nhìn].
Cụm 2: [...]
Không dùng lại một robot chung cho mọi ý; mỗi hình phải giải thích đúng chức năng.

## 7. Ràng buộc loại trừ
Không tự thêm chữ; không Anh hóa ngoài danh sách ngoại lệ; không đổi số bước; không ký tự sai hoặc mất dấu; không tiêu đề bị cắt; không đường nối xuyên qua chữ; không watermark; không số liệu hoặc tuyên bố ngoài nguồn.

## 8. Kiểm tra
Rà soát đủ chữ/đủ bước, dấu tiếng Việt, vùng an toàn và hướng đọc. Kích thước tệp thực và tính chỉnh sửa được phải mô tả trung thực; không suy ra từ các từ “8K”, “vector” hoặc “PowerPoint-ready”.


## Prompt mẫu — Quy trình 4 bước, không tự hứa năng lực sản phẩm

Tạo một infographic PowerPoint ngang 16:9, bố cục L05, nền trắng. Đây là quy trình vận hành đề xuất, không phải ảnh chụp hoặc mô tả tính năng mặc định của một phần mềm.

Khung 1920 × 1080, lề trái/phải 100 px, trên 90 px, dưới 80 px. Tiêu đề ở trên; bốn thẻ ngang cân đối chiếm phần giữa; một thanh kết luận ở cuối. Chữ navy #0A192F, điểm nhấn xanh #2563EB và xanh ngọc đậm #0F766E. Bước 4 dùng xanh lá; biểu tượng 3D mềm đồng nhất; bóng nhẹ, không viền phát sáng dày.

Tiêu đề chính xác: “4 bước xây dựng môi trường làm việc cho tác nhân AI”.
Phụ đề: “Chuẩn hóa dữ liệu, quy tắc và cách kiểm tra trước khi mở rộng”.

Thẻ 1, huy hiệu “1”, tên “Tổ chức không gian làm việc”. Biểu tượng cây thư mục. Hai ý: “Tách dữ liệu đầu vào và đầu ra”; “Lưu tài liệu tham chiếu theo nhóm”. Nhãn đáy: “Đầu ra: Cấu trúc thư mục”.

Thẻ 2, huy hiệu “2”, tên “Xác định quy tắc”. Biểu tượng khiên và bút. Hai ý: “Nêu phạm vi và giới hạn quyền”; “Chỉ rõ việc cần phê duyệt”. Nhãn đáy: “Đầu ra: AGENTS.md”.

Thẻ 3, huy hiệu “3”, tên “Chuẩn hóa quy trình”. Biểu tượng cẩm nang quy trình. Hai ý: “Mô tả các bước xử lý”; “Định nghĩa biểu mẫu kết quả”. Nhãn đáy: “Đầu ra: SKILL.md”.

Thẻ 4, huy hiệu “4”, tên “Kiểm thử và hiệu chỉnh”. Biểu tượng danh sách kiểm tra với dấu tích. Hai ý: “Chạy trên dữ liệu mẫu”; “Kiểm tra trước khi áp dụng”. Nhãn đáy: “Đầu ra: Quy trình đã thử nghiệm”.

Nối thẻ 1 → 2 → 3 → 4 bằng mũi tên một chiều trong khoảng trống; không nối qua nội dung thẻ.

Chân trang chính xác: “Bắt đầu bằng môi trường rõ ràng, không chỉ bằng câu lệnh dài hơn.”

Chỉ giữ nguyên AGENTS.md và SKILL.md; mọi nhãn khác phải tiếng Việt. Không thêm các từ Workspace, Blueprint, Gate, Code, Output. Không thêm logo, chữ ký hoặc tỷ lệ hiệu quả.


## Prompt mẫu — Vòng lặp đúc kết kinh nghiệm

Tạo infographic L12, tỷ lệ 16:9, nền trắng, navy và xanh dương; bước 3 nổi bật bằng cam san hô. Bốn thẻ bố trí thành vòng khép kín, thứ tự: 1 góc trên trái → 2 góc trên phải → 3 góc dưới phải → 4 góc dưới trái → quay lại 1. Mũi tên nằm trong khoảng trống, không xuyên qua thẻ. Trung tâm là biểu tượng hai mũi tên tuần hoàn, không phải thẻ thứ năm.

Giữ lề 100 px hai bên, 90 px trên, 80 px dưới ở khung 1920 × 1080. Tiêu đề: “Biến kinh nghiệm thực tế thành quy tắc có thể tái sử dụng”.

Bước 1: “Ghi nhận kết quả”. Nội dung: “Lưu sự cố hoặc bài học sau nhiệm vụ”. Hình neo: kính lúp và dấu cảnh báo.
Bước 2: “Phân tích nguyên nhân”. Nội dung: “Tách bối cảnh, nguyên nhân và cách xử lý”. Hình neo: phễu chắt lọc.
Bước 3: “Cập nhật có kiểm soát”. Nội dung: “Đề xuất chỉnh AGENTS.md hoặc SKILL.md”; “Rà soát và phê duyệt trước khi áp dụng”. Hình neo: bánh răng đồng bộ. Bên dưới có hai nhãn tệp nhỏ, không thêm một nhánh quy trình mới.
Bước 4: “Áp dụng và kiểm tra lại”. Nội dung: “Nạp quy tắc phù hợp và theo dõi kết quả”. Hình neo: khiên dấu tích.

Nhãn trung tâm: “Học từ kết quả”. Chân trang: “Mục tiêu: Giảm lỗi lặp lại; không thay thế kiểm thử và giám sát.”

Chỉ sử dụng bộ chữ trên; không giữ các từ Task, WHAT, HOW, Sync hoặc Reflection Loop. Không thêm cam kết “miễn nhiễm sai sót” hay “tự động áp dụng trong mọi phiên”. Nội dung là quy trình đề xuất cho bài giảng, không xác nhận cơ chế tự cập nhật mặc định của sản phẩm.


## Prompt mẫu — Giải phẫu tài liệu

Tạo infographic 16:9 L13, nền trắng. Nửa trái khoảng 55% là khung tài liệu màu slate đậm; nửa phải khoảng 40% là bốn thẻ chú giải; khoảng giữa 5% cho đường nét đứt. Bốn vùng tài liệu được đánh số 1–4 và nối đúng tới bốn thẻ tương ứng. Màu chủ đạo navy–blue; thêm xanh ngọc và cam cho phân biệt nhóm. Giữ lề an toàn, không đặt một cửa sổ IDE nhiều chi tiết quá nhỏ.

Tiêu đề: “SKILL.md giúp mô tả nhiệm vụ thành hướng dẫn có cấu trúc”.

Vùng 1 của tài liệu: nhãn “Mô tả kỹ năng”; đoạn mã minh họa ngắn có hai khóa nguyên bản `name:` và `description:`. Nội dung mô tả bằng tiếng Việt. Không thêm các khóa cấu hình được ngụ ý là chuẩn bắt buộc.
Vùng 2: tiêu đề “Đầu vào và phạm vi”; hai dòng “Dữ liệu nguồn” và “Điều kiện cần có”.
Vùng 3: tiêu đề “Các bước xử lý”; ba dòng “1. Đọc dữ liệu”; “2. Tổng hợp chỉ số”; “3. Soạn báo cáo”.
Vùng 4: tiêu đề “Đầu ra và kiểm tra”; hai dòng “Biểu mẫu kết quả”; “Đối chiếu dữ liệu nguồn”.

Bốn thẻ phải có đúng nội dung:
1. “Nhận diện nhiệm vụ” — “Mô tả mục đích và trường hợp sử dụng”.
2. “Ranh giới rõ ràng” — “Nêu điều kiện đầu vào và phạm vi xử lý”.
3. “Quy trình từng bước” — “Giúp thực hiện và kiểm tra nhất quán hơn”.
4. “Đầu ra chuẩn hóa” — “Định nghĩa hình thức và tiêu chí nghiệm thu”.

Chân trang: “Cấu trúc cụ thể cần phù hợp với công cụ sử dụng.”

Không thêm “loại bỏ ảo giác” hoặc “bảo đảm kết quả đúng mọi lần”. Đây là minh họa cấu trúc; khi cần đoạn mã đọc và sao chép chính xác, dùng lớp chữ chỉnh sửa riêng thay vì giao hoàn toàn cho công cụ tạo ảnh.


## Prompt mẫu — Hình nền mở chương không chữ

Tạo hình nền thuyết trình doanh nghiệp 16:9, nền navy #0A192F, công nghệ hiện đại tối giản, concept art 3D tinh tế. Bên trái là sóng sáng mềm và hạt năng lượng cyan; bên phải là các khối kính hình học kết nối với đường mạch, mô-đun công cụ và bánh răng tối giản. Dòng năng lượng chuyển dần từ mềm sang có cấu trúc. Điểm xuyết mint và tím rất nhẹ; ánh vàng chỉ xuất hiện ở vài nút kết nối.

Giữ vùng giữa khoảng 45% bề rộng yên, ít tương phản và không có vật thể chính để thêm nội dung trong PowerPoint. Vật thể tập trung sát hai phía nhưng không bị cắt cụt vô ý. Không robot người thật, không màn hình có chữ. Không chia thẻ kiến thức hoặc thêm chân trang.

Tuyệt đối không chữ, số, tiêu đề, logo, dấu ngoặc, dấu gạch chéo, ký hiệu dòng lệnh hay ký tự giả. Dùng biểu tượng bằng hình học, không dùng ký hiệu văn bản để thay thế.


## Prompt mẫu — Bộ hình neo tách riêng

Tạo bốn biểu tượng 3D mềm đồng nhất: cây thư mục, khiên với bút, cẩm nang quy trình, danh sách kiểm tra có dấu tích. Màu navy–blue–teal, chất liệu mờ tinh tế, cùng góc nhìn ba phần tư và cùng hướng sáng. Mỗi biểu tượng là một vật thể độc lập, không chạm vật thể khác, không nối mũi tên, không nhãn hoặc chữ.

Bố trí trên nền trắng sạch để dễ tách, hoặc nền trong suốt khi được hỗ trợ thực sự. Chừa khoảng đệm đều xung quanh từng vật thể. Không dùng bóng đổ đậm hoặc chi tiết ánh sáng làm khó tách hình. Đây là tài sản hình ảnh để ghép vào slide, không phải một slide có nội dung.


## Prompt mẫu — Chỉ sửa một vùng

Dùng đúng ảnh tôi đính kèm làm ảnh đích. Phạm vi được thay đổi: chỉ dòng tiêu đề trên cùng, trong khoảng y = 0–15% chiều cao ảnh.

Thay tiêu đề bằng: “Các năng lực cốt lõi của Google Antigravity”.

Khóa tất cả vùng còn lại: không dịch lại tên các thẻ, không sửa đoạn mô tả, không đổi logo, biểu tượng, màu sắc, số thứ tự, vị trí thẻ, đường nối, lề và tỷ lệ. Khớp kiểu chữ, độ đậm và màu tiêu đề với ảnh gốc. Không tự thêm phụ đề.

Ưu tiên sửa cục bộ; không tái sáng tạo toàn ảnh. Nếu công cụ có thể làm thay đổi ngoài vùng, nêu rõ giới hạn và dùng phương án ghép sửa khi cần giữ nguyên từng pixel. Nếu chưa có ảnh đích khả dụng, yêu cầu cung cấp ảnh thay vì tạo lại từ trí nhớ.


## Những yêu cầu hội thoại ngắn có thể dùng

“L05; bốn bước; nền trắng; có tiêu đề; giữ nguyên tên tệp; tạo ảnh ngay từ nội dung sau.”

“L11; một lõi và ba vệ tinh; chừa 22% phía trên để tôi đặt tiêu đề; chỉ dùng nhãn ngắn.”

“Cho ba phương án bố cục khác cấu trúc, cùng bộ màu; chưa tạo ảnh.”

“Việt hóa toàn bộ chữ, kể cả chú giải và chân trang; chỉ giữ những từ trong danh sách tên riêng sau.”

“Giữ style đã duyệt; giảm mật độ bằng cách tách thành hai slide, không giảm cỡ chữ.”

“Xuất phiếu nội dung và đặc tả trang sang Word; đánh dấu phần chưa được duyệt.”

Các câu trên là quy ước giao việc trong hội thoại, không phải lệnh chức năng tích hợp sẵn.
