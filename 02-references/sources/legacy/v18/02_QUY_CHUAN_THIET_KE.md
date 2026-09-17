# Quy chuẩn thiết kế và biên tập
## 1. Phạm vi kế thừa
Kế thừa tài liệu 01: mục tiêu giảng dạy, chia cụm kiến thức, tiêu đề hành động, 10 dạng bố cục và quy trình chuyển hóa văn bản. Kế thừa tài liệu 02: hệ màu navy–xanh dương–cam, khung thẻ, lề, khoảng cách, hình phẳng mặc định và kiểm định. Các ngưỡng điều chỉnh dưới đây là quyết định thiết kế cho project, không phải trích nguyên văn tài liệu gốc. [S1, S2]

## 2. Ba lớp nội dung
**Lớp hiển thị:** chỉ những gì phải xuất hiện trên slide: kết luận, từ khóa, mối quan hệ, điều kiện thiết yếu.
**Lớp giảng viên:** giải thích, dẫn chứng, câu hỏi gợi mở và hướng dẫn thao tác. Đưa vào Chat, Word hoặc ghi chú PowerPoint, không vẽ vào ảnh.
**Lớp kiểm chứng:** tài liệu nguồn, điều kiện áp dụng, ngày kiểm tra và phần còn chưa chắc. Lưu cùng phiếu slide; chỉ đưa mã nguồn ngắn lên ảnh khi thực sự cần.

Không xóa điều kiện làm thay đổi ý nghĩa khi rút gọn. “Tự động trong phạm vi đã được cấp quyền” không được rút thành “Tự động mọi việc”.

## 3. Chế độ sản phẩm
| Mã | Sản phẩm | Quy tắc |
|---|---|---|
| P1 | Slide hoàn chỉnh | Có tiêu đề, nội dung, tối đa một câu đúc kết. |
| P2 | Infographic chừa tiêu đề | 0–240 px trên cùng hoàn toàn trống; nội dung từ y=270 px. Vẫn là ảnh 16:9. |
| P3 | Minh họa kiến thức không chữ | Biểu tượng và quan hệ trực quan, không ký tự giả. Chữ sẽ đặt ở lớp PowerPoint. |
| P4 | Nền bài thuyết trình | Trang trí ở rìa; khoảng trống chính theo vị trí chữ đã yêu cầu. |
| P5 | Thiết kế tách lớp | Chỉ tạo minh họa bằng ảnh; tiêu đề, thân bài, mũi tên và số liệu dàn bằng đối tượng có thể sửa. |

Với P2, không tự thay vùng trống bằng câu định nghĩa lớn. Với P4, không để ánh sáng mạnh hoặc chi tiết dày sau vùng đặt chữ. Với P5, cần công cụ dàn trang phù hợp; prompt sinh ảnh một mình không tạo ra các đối tượng PowerPoint riêng biệt.

## 4. Hình học 16:9
PowerPoint có lựa chọn Widescreen 16:9; kích thước Widescreen thường dùng là 13⅓ × 7,5 inch. [W1]
Khung tham chiếu của project: 1920 × 1080 px. Có thể dùng 3840 × 2160 khi công cụ thật sự hỗ trợ; không lấy từ “4K” trong prompt làm bằng chứng độ phân giải.

| Thuộc tính | Quy ước project ở 1920 × 1080 |
|---|---|
| Lề trái/phải | 100 px mỗi bên, khoảng 5,2% chiều rộng |
| Lề trên | 90 px, khoảng 8,3% chiều cao |
| Lề dưới | 80 px, khoảng 7,4% chiều cao |
| Phạm vi ngang nội dung | x=100 đến x=1820 |
| Vùng tiêu đề P1 | y=90 đến khoảng y=230 |
| Vùng nội dung chính P1 | khoảng y=270 đến y=850 |
| Thanh đúc kết khi dùng | khoảng y=900 đến y=1000 |
| Khoảng cách giữa thẻ | 24–32 px; tăng khi có mũi tên |
| Khoảng đệm trong thẻ | 24–36 px |
| Bo góc / viền | khoảng 16 px / 1–2 px |

Đây là lưới khởi điểm, không phải hàng rào bắt mọi bố cục có cùng chiều cao. Bỏ thanh đúc kết thì mở rộng vùng chính nhưng vẫn giữ lề. Ở ảnh 3840 × 2160, nhân các kích thước px với 2. Nếu công cụ xuất ảnh khác tỷ lệ, mở rộng nền hoặc dàn lại thay vì kéo méo sơ đồ; kiểm tra kích thước tệp sau cùng.

## 5. Cỡ chữ để trình chiếu
| Vai trò | Cỡ chữ đề xuất trong PowerPoint |
|---|---|
| Tiêu đề trang | 32–40 pt, tối đa hai dòng |
| Tiêu đề thẻ | 22–26 pt, ngắn và đồng nhất |
| Nội dung chính | 20–24 pt; 18 pt chỉ dùng ngoại lệ đã kiểm tra |
| Nhãn sơ đồ / đúc kết | 18–22 pt |
| Nguồn, mã tham chiếu không trọng tâm | 14–16 pt; không dùng cho luận điểm chính |

Gợi ý kiểu chữ khi dàn trang: Aptos, Arial, Noto Sans hoặc Inter, sau khi kiểm tra dấu tiếng Việt trong môi trường đích. Dùng tối đa hai họ chữ; với ảnh sinh bằng AI, xem đây là chỉ dẫn hình thức, không phải bảo đảm công cụ sẽ nhúng đúng phông.
Trên khung PowerPoint rộng 960 pt được ánh xạ sang ảnh 1920 px, 1 pt tương đương 2 px về tỷ lệ dàn trang: chữ 20 pt tương ứng cỡ danh nghĩa khoảng 40 px. Đây không phải công thức cố định cho mọi ảnh hoặc quan hệ CSS pt/px. Khi ảnh bị thu nhỏ trong slide, chữ cũng nhỏ theo.

Tiêu đề Việt ưu tiên kiểu câu: “Bốn thành phần tạo nên một tác nhân AI”, không viết hoa từng từ theo tiếng Anh. Chỉ dùng chữ hoa cho nhãn ngắn. Tránh phông siêu hẹp, viền chữ phát sáng và đoạn văn căn giữa.

## 6. Ngân sách chữ
Tài liệu 01 đặt ngưỡng 40–60 từ. Để dùng được với tiếng Việt mà không lệ thuộc bộ tách từ, project đếm các đơn vị phân cách bằng khoảng trắng; tính cả tiêu đề, nhãn, ghi chú hiển thị. Đây là quy ước vận hành, không phải đo giới hạn nhận thức. [S1]

**Trình chiếu:** mục tiêu 40–60 đơn vị. Thẻ có thể chỉ gồm tiêu đề + một dòng + biểu tượng; không ép đủ mọi lớp thẻ trong tài liệu 02.
**Mở rộng:** 60–100 đơn vị khi cần giữ định nghĩa hoặc so sánh; phải có chủ đích và kiểm tra chữ đủ lớn.
**Tham khảo:** trên 100 đơn vị nên tách thành slide tổng quan và slide chi tiết hoặc tài liệu Word. Không chuyển sang mức này chỉ vì muốn giữ tất cả câu chữ.

Chỉ giữ một luồng trực quan chính. Không cộng dồn quy trình + ma trận + ví dụ + công thức + hai câu đúc kết lên cùng trang. Khối chân trang hỗ trợ kết luận; không mặc định chiếm 25% chiều cao.

## 7. Bảng màu và chất liệu
| Vai trò | Màu đề xuất |
|---|---|
| Nền nội dung | #FFFFFF hoặc #F8FAFC |
| Tiêu đề / chữ chính | #0A192F, #0F2744 hoặc #334155 |
| Chữ phụ | #475569 |
| Điểm nhấn chính | #2563EB |
| Nhấn phụ cyan / xanh ngọc | #00B0F0, #14B8A6 cho đường/hình; chữ nhỏ cần màu tối hơn |
| Thành công / xác minh | #16A34A cho biểu tượng, #166534 cho chữ nhỏ |
| Phê duyệt / cảnh báo | #F97316 cho viền/điểm nhấn, #9A3412 cho chữ nhỏ |
| Viền | #E2E8F0 |

Chọn một màu chính và một đến hai màu nhấn. Không mặc định gắn bốn dải màu Google lên mọi slide; chỉ dùng dấu hiệu thương hiệu khi có chủ đích. Không tự chèn logo KPIM, COMPA Class hoặc Google nếu không được yêu cầu/cung cấp.

TRẮNG PHẲNG là kiểu chuẩn. TRẮNG 3D NHẸ kế thừa điểm hấp dẫn của mẫu AIA-102 nhưng chỉ dùng khi được chọn. NAVY MINH HỌA dùng cho nền, bìa, chuyển chương: navy đậm, cyan, mint, tím nhẹ hoặc vàng rất tiết chế. Không dùng kính trong suốt phía sau đoạn chữ dày.

Một thẻ một biểu tượng chính. Biểu tượng thường chiếm khoảng 15–25% diện tích thẻ ở slide kiến thức; đây là điểm khởi đầu, không phải chỉ tiêu cứng. Bóng mờ nhẹ, vi mạch ở rìa, hiệu ứng phát sáng không đè lên chữ. Không pha biểu tượng 2D, ảnh thật và đồ vật 3D khác chất liệu trong cùng nhóm chức năng.

## 8. Tương phản và khả năng tiếp cận
Tham chiếu WCAG 2.2 SC 1.4.3: tỷ lệ tương phản tối thiểu 4,5:1 cho chữ thường và 3:1 cho chữ lớn. Đây là tiêu chí tương phản mượn từ thiết kế nội dung số, không đồng nghĩa slide đã được chứng nhận toàn bộ WCAG. [W2]
Project nên nhắm 4,5:1 cho hầu hết chữ để có dư địa trình chiếu. Không dùng màu làm dấu hiệu duy nhất: trạng thái phải có nhãn hoặc biểu tượng. Không tuyên bố “đạt WCAG AA” nếu chưa đo các cặp màu thực tế.
Ảnh chứa chữ không thay thế được lớp chữ có thể truy cập. Khi bàn giao bản dùng rộng rãi, cung cấp bản chữ/ghi chú và mô tả thay thế cho ảnh; ưu tiên P5 cho tài liệu cần sửa, tìm kiếm và tái sử dụng. [W2]

## 9. Từ điển Việt hóa
| Từ xuất hiện trong đề bài | Cách trình bày ưu tiên |
|---|---|
| Workflow / Task / Output | Quy trình / Nhiệm vụ / Đầu ra |
| Gate / Checkpoint | Điểm kiểm soát / Điểm phê duyệt |
| Template / Checklist | Mẫu / Danh sách kiểm tra |
| Workspace / File Explorer | Không gian làm việc / Trình quản lý tệp |
| Memory / Tool / Skill / Plugin | Bộ nhớ / Công cụ / Kỹ năng / Tiện ích mở rộng |
| Prompt Engineering | Thiết kế câu lệnh |
| Harness Engineering | Thiết kế môi trường điều phối tác nhân AI |
| Reflection Loop | Vòng lặp đúc kết kinh nghiệm |
| AI Agent | Tác nhân AI; chỉ giữ AI Agent khi người dùng khóa thuật ngữ |
| System Instructions | Bộ chỉ dẫn hệ thống |
| Code / Run script | Mã lệnh / Chạy tập lệnh |
| Artifacts | Sản phẩm đầu ra; không dịch thành “tác vụ” |

Không dịch khóa `name`, `description`, cú pháp YAML, tên tệp `AGENTS.md`, `SKILL.md`, lệnh CLI và đường dẫn nếu đang hướng dẫn sử dụng thật. Trong nhãn giao diện mô phỏng, có thể Việt hóa phần diễn giải; với ảnh chụp giao diện thật, phân biệt bản địa hóa chú thích với sửa nội dung giao diện.

## 10. Chính xác hơn hình ảnh mẫu
Các ảnh cũ là mẫu về thị giác, không phải tài liệu chứng minh các tuyên bố như “giảm 70% token”, “không ảo giác” hoặc “miễn nhiễm mọi lỗi”. Không tái sử dụng các câu này nếu không có nguồn và điều kiện phù hợp. Khi muốn sửa nội dung của người dùng, nêu rõ câu gốc, vấn đề và câu đề xuất trước khi khóa chữ.
Không coi SKILL.md là mã máy được thực thi chỉ vì tên gọi trong mẫu. Không coi một tên hiển thị do người dùng đặt là tên sản phẩm chính thức. Không coi kiến trúc minh họa hoặc ảnh giao diện mô phỏng là ảnh chụp sản phẩm thật.
