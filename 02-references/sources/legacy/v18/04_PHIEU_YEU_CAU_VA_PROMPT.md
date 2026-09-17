# Phiếu yêu cầu và bộ prompt dùng lại
## 1. Phiếu một slide
Sao chép phiếu này vào Chat hoặc Word. Các mục bỏ trống dùng mặc định; chỉ hỏi lại mục ảnh hưởng tới tính đúng hoặc phạm vi.

```text
MÃ SLIDE: AIA102-S01
CHẾ ĐỘ: TƯ VẤN / SOẠN PROMPT / TẠO ẢNH / CHỈNH SỬA
ĐỐI TƯỢNG: [Ai học? Trình độ?]
MỤC TIÊU: [Sau slide, người học hiểu/làm được gì?]
NGUỒN: [Đoạn văn, file, ảnh và vị trí cần đọc]
NỘI DUNG GỐC: [Dán nội dung]
THÔNG ĐIỆP CHÍNH: [Một câu; để AI đề xuất nếu chưa có]
TÊN RIÊNG / THUẬT NGỮ PHẢI GIỮ: [...]
TIÊU ĐỀ: [AI đề xuất / giữ nguyên: “...” / không vẽ]
SẢN PHẨM: P1 / P2 / P3 / P4 / P5
BỐ CỤC: TỰ CHỌN hoặc L01–L18
PHONG CÁCH: TRẮNG PHẲNG / TRẮNG 3D NHẸ / NAVY MINH HỌA
MẬT ĐỘ: TRÌNH CHIẾU / MỞ RỘNG
ẢNH THAM CHIẾU: [Tên file và đặc điểm muốn giữ]
BẤT BIẾN: [Chữ / số / thứ tự / màu / chủ thể]
KHÔNG ĐƯỢC LÀM: [...]
BÀN GIAO: [Ảnh / prompt / Word / tệp dàn trang]
```

## 2. Chu trình cộng tác
**Hiểu yêu cầu:** đọc nguồn thực tế; xác định chủ đề, mức kiến thức, mối quan hệ và các điểm không chắc. Không giả định đã đọc cuộc chat khác chỉ vì người dùng nhắc tên.
**Chuẩn hóa:** trả về mục tiêu, kết luận và chữ hiển thị. Chỉ rõ phần lược bỏ sẽ vào ghi chú. Nếu sửa một khẳng định quan trọng, hiển thị đề xuất để duyệt.
**Chọn khung:** một phương án chính và tối đa một phương án thay thế, giải thích ngắn theo cấu trúc kiến thức. Không trình 8–10 phương án làm người dùng phải tự thiết kế.
**Khóa:** người dùng duyệt chữ, tên riêng, bố cục và vùng không được đổi. Đây là bản nội dung chuẩn cho phiên dựng.
**Dựng:** biên dịch thành prompt tự đủ ngữ cảnh; dùng ảnh tham chiếu cụ thể nếu có. Nếu đã yêu cầu tạo ảnh và thông tin đủ, tạo trực tiếp thay vì yêu cầu duyệt mọi bước.
**Kiểm tra và sửa:** đối chiếu với bản chữ khóa và ranh giới chỉnh sửa. Tách lỗi nội dung, lỗi chữ và lỗi bố cục; không thiết kế lại toàn trang khi chỉ sai một tiêu đề.

## 3. Mẫu prompt dựng toàn trang
```text
MỤC TIÊU SẢN PHẨM
Tạo đúng một ảnh infographic phục vụ bài giảng doanh nghiệp, ngang 16:9.
Sản phẩm: [P1/P2]. Mục tiêu người học: [một câu].

THIẾT KẾ
Khung tham chiếu 1920×1080. Nền trắng #FFFFFF.
Lề trái/phải 100 px, trên 90 px, dưới 80 px; khoảng cách thẻ 24–32 px.
Chữ navy #0A192F, xanh dương #2563EB; nhấn [màu] tại [ý nghĩa].
Biểu tượng [phẳng hai tông/3D nhẹ đồng bộ]. Bo góc 16 px, viền mảnh, bóng rất nhẹ.
Phong cách công nghệ doanh nghiệp, trực diện, không phối cảnh cả trang.

BỐ CỤC
Dùng [mã + tên]. [Mô tả vị trí, số thẻ, tỷ lệ tương đối và thứ tự đọc].
Mỗi biểu tượng phục vụ một ý, không che chữ.
Đường nối: [nguồn → đích; hướng; ý nghĩa]. Không thêm đường nối ngoài danh sách.
[P2: toàn vùng 0–240 px trống hoàn toàn, nội dung bắt đầu từ y=270 px.]

VĂN BẢN HIỂN THỊ — KHÓA NGUYÊN VĂN
Tiêu đề: “...”
Phụ đề: [Không có / “...”]
Thẻ 1: “...” | “...”
Thẻ 2: “...” | “...”
Thẻ 3: “...” | “...”
Thẻ 4: [Không có / “...” | “...”]
Chân trang: [Không có / “...”]
Các nhãn kỹ thuật giữ nguyên: [...]
Chỉ các chuỗi trên được phép xuất hiện trên ảnh; không in tên mục hướng dẫn này.

ĐIỂM TỰA THỊ GIÁC
[Thẻ 1: biểu tượng ...; thẻ 2: ...; điểm nhấn chính: ...]

GIỚI HẠN
Không đổi tiêu đề. Không thêm tiếng Anh ngoài các tên/định danh đã cho.
Không tự thêm số liệu, phụ đề, logo, watermark, bảng chú giải hoặc câu kết mới.
Không chữ giả, không văn bản mẫu, không cắt thẻ sát mép, không hiệu ứng che chữ.
Không thu nhỏ nội dung chính để nhồi chữ. Không gắn nhãn “8K” hay “vector”.

ĐỐI CHIẾU
Số thẻ đúng, thứ tự đúng, mũi tên đúng, tiếng Việt đủ dấu, khoảng trắng còn rõ.
```

Mẫu này là mô tả thiết kế trung lập. Chỉ bổ sung tham số riêng của công cụ khi đã biết cú pháp của công cụ đó; không trộn hậu tố Midjourney vào mọi trình tạo ảnh. Khung px là mục tiêu dàn trang, không bảo đảm bộ sinh sẽ trả đúng kích thước nếu công cụ không hỗ trợ.

## 4. Prompt sửa đúng vùng
```text
Sửa ảnh [tên file thực tế được đính kèm], không tạo một thiết kế mới.
Vùng được sửa: [tọa độ tương đối/vị trí/nhãn thẻ].
Chữ hiện tại: “...”. Chữ thay thế chính xác: “...”.
Giữ nguyên mọi nội dung ngoài vùng sửa: biểu tượng, số liệu, màu, bố cục,
đường nối, tỷ lệ, vị trí, kích thước các thẻ và toàn bộ chữ còn lại.
Không dịch hoặc biên tập thêm. Không đổi kiểu minh họa.
Nếu chữ mới quá dài, báo xung đột trước khi thay đổi phần khác.
```

Nếu cần bất biến từng điểm ảnh, dùng công cụ sửa theo vùng hoặc dàn lại lớp chữ. Tái sinh toàn ảnh chỉ là phương án gần đúng, không phải bảo đảm giữ nguyên.

## 5. Prompt ảnh nền không chữ
```text
Tạo ảnh nền PowerPoint ngang 16:9, phong cách công nghệ cao tinh giản.
Nền navy #0A192F, ánh cyan và mint, điểm tím rất nhẹ.
Chủ thể: [mô tả ẩn dụ, vị trí].
Vùng đặt chữ sau này: [giữa/trái/phải] chiếm [tỷ lệ] phải thật thoáng,
không có chủ thể, mạch sáng, ánh chói hoặc tương phản mạnh đi qua.
Không chữ, không số, không ký tự, không logo chữ, không watermark;
không có >_, /, { }, chữ giả trên sách, màn hình, trang tài liệu hoặc thẻ.
Dùng biểu tượng hình học thuần túy để mô tả chức năng.
Không vẽ khung màn hình, phòng họp hoặc ảnh chụp slide.
```

## 6. Prompt biểu tượng riêng
```text
Tạo một biểu tượng [tên chức năng] để ghép vào thẻ infographic.
Kiểu [phẳng hai tông/3D nhẹ], màu navy và xanh dương, đồng bộ ảnh tham chiếu.
Một chủ thể rõ, cân giữa, có khoảng trống quanh vật thể.
Nền [trắng/alpha trong suốt nếu công cụ hỗ trợ thật].
Không chữ, số, ký tự, logo, watermark và không thêm vật thể phụ không cần thiết.
```

## 7. Làm việc qua Word
Dùng mỗi Heading 1 cho một mô-đun, Heading 2 cho một slide đề xuất. Mỗi slide có cùng các trường: mã, mục tiêu, nguồn, chữ hiển thị, bố cục, ghi chú giảng viên, prompt hình và trạng thái duyệt.
Yêu cầu AI đọc đúng file Word được cung cấp và đề xuất tách slide theo mục tiêu. Không mặc định truy cập được file đang mở trên máy. Khi chưa có tích hợp phù hợp, trao đổi bằng tệp đính kèm.
Cột/khối “Ghi chú giảng viên” phải được tách khỏi “Chữ hiển thị”; nếu không, nội dung dễ bị đưa hết vào ảnh. Khi chỉnh Word, giữ mã slide và bản chữ đã khóa để không mất liên hệ với ảnh.

## 8. Thông tin chuyển giao giữa các cuộc chat
Mang theo: bản chữ duyệt, mã bố cục, phong cách, tên ảnh tham chiếu, các vùng bất biến, số phiên bản và phần đang cần sửa. Không chỉ nói “giống ảnh trước” trong một cuộc chat không có ảnh trước.
Tên bản đề xuất: `AIA102_S07_L11_v01_brief.md`, `AIA102_S07_L11_v01_prompt.md`, `AIA102_S07_L11_v01.png`. Nếu chỉ sửa chữ: tăng phiên bản và ghi đúng thay đổi, không ghi đè bản đã duyệt.
