# Quy chuẩn thiết kế hiện hành — 2.0.0

Kế thừa hai nguồn người dùng và bộ 20; các điều chỉnh được ghi ở [migration](migration.md).
Nguồn ngoài tại [ma trận bằng chứng](evidence_matrix.md). Số lề/chữ là quy ước của gói trừ nơi ghi rõ nguồn.

## Khung hình và vùng

Theo S09, PowerPoint Widescreen là 16:9, 13,333×7,5 inch. Dùng 1920×1080 px làm hệ tham chiếu.
Ở hệ này 1 pt tương đương khoảng 2 px; không coi 20 px là 20 pt. Không hứa pixel thật từ prompt.

| Thành phần | Thông số nội bộ |
|---|---|
| Lề trái/phải | 100/100 px |
| Lề trên/dưới | 90/80 px |
| Tiêu đề FULL | y=90–210, tối đa hai dòng |
| Nội dung FULL | y=250–900; có thể tới 1000 khi bỏ chân trang |
| TITLE_RESERVED | y=0–240 trống hoàn toàn, nội dung từ y=270 |
| Khoảng giữa thẻ / đệm | 24–32 px, tăng cho đường nối |
| Bo góc | khoảng 16 px, không ép mọi vật thành thẻ |
| EDITABLE_OVERLAY | Hình và chữ cần sửa là lớp khác nhau |
| NO_TEXT | Không chữ/số/ký tự, kể cả >_, /, { }, logo chữ |

Các số co giãn theo tỷ lệ. Huy hiệu nhô lên và đầu mũi tên cũng phải ở trong lề.

## Chữ và mật độ

Phông không chân hỗ trợ tiếng Việt: chọn theo máy đích, ví dụ Aptos, Arial, Noto Sans.
Không phân phối font. Kiểm tra đủ dấu ghép và không cắt dấu trên đầu chữ.
Tiêu đề 32–40 pt; tên khối 22–26 pt; nội dung 20–24 pt; chú thích quan trọng ưu tiên ≥18 pt.
S10 khuyên từ 18 pt; gói tăng mục tiêu cho trình chiếu. Phải kiểm tra phòng chiếu thực.

Một slide một thông điệp và một cấu trúc chính. Dùng 3–5 khối làm điểm khởi đầu,
không ép bỏ bước thật. 60–100 đơn vị cách trắng là ngân sách tham khảo tiếng Việt;
trang ít chữ 30–60, trang quá 120–140 thường nên tách. Đây là quy ước biên tập, không giới hạn trí nhớ.
Không giảm chữ để nhét; tách chữ hiển thị và ghi chú. Chân trang chỉ một ý nếu cần, không bắt chiếm 25%.

## Màu và chất liệu

| Vai trò | Màu |
|---|---|
| Nền | #FFFFFF / #F8FAFC |
| Chữ chính / phụ | #0A192F / #475569 |
| Nhấn chính | #2563EB |
| Xanh ngọc chữ | #0F766E |
| Kết quả đã xác minh | #15803D |
| Cam đồ họa / cam chữ | #F97316 / #9A3412 |
| Tím | #6D28D9 |
| Viền trang trí | #E2E8F0 |

Viền nhạt không thay đường nối mang ý nghĩa. Không dùng màu sáng cho chữ nhỏ trên trắng.
Ngưỡng tham khảo S13: 4,5:1 chữ thường, 3:1 chữ lớn theo định nghĩa WCAG; đo màu thực,
không gọi toàn slide đạt WCAG chỉ qua phép đo này. Dùng nhãn/hình thay cho chỉ đỏ–xanh.

TRANG-SANG: nền trắng, 2D/vector hai tông; 3D mềm opt-in, ít và đồng bộ.
MO-CHUONG-TOI: navy, cyan/mint nhẹ ở viền; dùng cho mở chương/nền ít hoặc không chữ.
Không robot ở mọi thẻ, không neon làm nhòe chữ, không 3D làm sai tỷ lệ biểu đồ.

## Nhịp bộ trang và bản chỉnh sửa

Giữ màu, lề, cấp chữ và chất liệu; chọn layout theo quan hệ kiến thức.
Thứ tự gợi ý: L01 → L06 → L11 → L07 → L13 → L05 → L12 → L09 → L10.
Không tự thêm logo KPIM/COMPA Class. “Chỉ sửa tiêu đề” là khóa toàn bộ phần còn lại.
PNG có vector look không là vector; PNG đặt trong PPTX không là SmartArt gốc hoặc chữ sửa riêng.


## Bổ sung v2.1 — mật độ mặc định

Theo [quy tắc infographic gọn](compact_infographic_rules.md): ưu tiên D1 35–70 đơn vị cách trắng.
D2 71–100 chỉ dùng có chủ đích; các ví dụ cũ 60–100 không là mặc định mới. Đây là quy ước
biên tập theo yêu cầu người dùng, không luật nhận thức hoặc số token. Khi xung đột với quy tắc
mật độ trong tài liệu trước hợp nhất, phần bổ sung này được ưu tiên cho nhiệm vụ mới.
