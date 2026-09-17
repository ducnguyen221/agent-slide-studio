# Quy chuẩn thiết kế và Việt hóa

## 1. Nguồn gốc và phạm vi
Kế thừa tài liệu 01 về mục tiêu đào tạo, thông điệp chính, gom cụm, hình neo và 10 kiểu bố cục. Kế thừa tài liệu 02 về bảng màu navy–blue–orange, thẻ mô-đun, vùng an toàn và khối tiện ích. Các con số dưới đây là cấu hình dự án được chuẩn hóa; phần thay đổi so với bản gốc được ghi ở hồ sơ nguồn.

Không gắn các con số mật độ hoặc kích thước với một “quy luật khoa học bắt buộc”. Chúng là điểm xuất phát để thiết kế, cần kiểm tra với nội dung, máy chiếu và khoảng cách xem thực tế.

## 2. Khung hình, lề và vùng nội dung

| Thành phần | Cấu hình dự án tại 1920 × 1080 |
|---|---|
| Tỷ lệ | 16:9, nằm ngang |
| Vùng an toàn | Trái/phải 100 px; trên 90 px; dưới 80 px |
| Vùng có nội dung | x = 100–1820; y = 90–1000 |
| Khoảng giữa thẻ | 24–32 px; tăng thêm khi có mũi tên |
| Đệm trong thẻ | 24–32 px |
| Bo góc | Khoảng 16 px; đồng nhất trong một chuỗi |
| Chữ và đường nối | Không cắt, chạm mép hoặc chồng đè lên nhau |
| Đầu ra mục tiêu | PNG 1920 × 1080 hoặc lớn hơn, nếu công cụ hỗ trợ |

Khung PowerPoint Widescreen được Microsoft mô tả là 13,333 × 7,5 inch, tương đương khoảng 33,867 × 19,05 cm. [N3]

**Quy đổi khi ghép nguyên ảnh phủ toàn slide:** 100 px ở khung 1920 tương đương khoảng 0,694 inch; 90 px khoảng 0,625 inch; 80 px khoảng 0,556 inch. Đây là tính toán tỷ lệ, không phải kích thước pixel cố định của PowerPoint.

**A — Có tiêu đề:** vùng tiêu đề tham chiếu y = 90–245; nội dung chính y = 280–850; đúc kết y = 895–990. Có thể điều chỉnh để vừa nội dung, nhưng không xâm phạm lề.

**B — Chừa tiêu đề:** vùng y = 0–240 để trắng; tuyệt đối không có tiêu đề giả hoặc chỉ dẫn đặt chữ. Bắt đầu nội dung từ y ≈ 270. Cần thiết kế sẵn vùng trống, không tạo slide đầy rồi thu toàn bộ ảnh xuống để nhét dưới tiêu đề.

**C — Không chữ:** giữ vùng trống ở giữa hoặc bên trái theo yêu cầu; mục tiêu 40–55% diện tích là vùng ít chi tiết. Có thể tràn nền trang trí ra mép, nhưng vật thể quan trọng không bị cắt.

Nếu ảnh xuất không đúng 16:9, ưu tiên mở rộng nền hoặc đặt trên canvas 16:9; chỉ cắt vùng không chứa thông tin; không kéo méo. Kiểm tra kích thước thật thay vì tin câu “4K/8K” trong prompt.

## 3. Chữ và mật độ

| Cấp chữ | Mục tiêu khi dựng trong PowerPoint | Quy đổi tham chiếu sang ảnh 1920 px phủ toàn slide |
|---|---|---|
| Tiêu đề trang | 32–40 pt | Khoảng 64–80 px |
| Tiêu đề thẻ | 20–24 pt | Khoảng 40–48 px |
| Nội dung chính | 18–22 pt | Khoảng 36–44 px |
| Ghi chú không thiết yếu | 14–16 pt, hạn chế | Khoảng 28–32 px |

Quy đổi trên dùng bề rộng slide gần 960 pt tương ứng 1920 px; không phải công thức CSS pt–px. Với ảnh AI, kích thước chữ chỉ là mục tiêu thị giác, cần kiểm tra ảnh thực. Microsoft khuyến nghị phông không chân, cỡ từ 18 pt và khoảng trắng đủ cho khả năng tiếp cận. [N4]

Tiêu đề ưu tiên một kết luận ngắn, thường 8–16 từ; tối đa hai dòng. Không bắt buộc in hoa toàn bộ. Tiêu đề có tên dài cần rút gọn phần diễn giải hoặc bỏ phụ đề trước khi giảm cỡ chữ.

Mỗi thẻ: tiêu đề tối đa hai dòng; 2–3 ý; mỗi ý tối đa 1–2 dòng. Bộ chữ hiển thị phải được chốt trước khi tạo ảnh. Không dùng đoạn văn dài làm phần trang trí trong cửa sổ chat.

Ba mức mật độ tham khảo: Gọn khoảng 60–100 từ; Tiêu chuẩn khoảng 100–170 từ; Chi tiết khoảng 170–230 từ. Đây không phải hạn mức cứng: tiếng Việt, mã nguồn và tên tệp cần đo theo độ dài dòng thực. Quá tải thì tách slide hoặc chuyển phần giải thích sang ghi chú, không thu nhỏ chữ.

## 4. Bảng màu và ngữ nghĩa

| Vai trò | Màu đề xuất | Cách dùng |
|---|---|---|
| Nền | #FFFFFF / #F8FAFC | Giảng dạy, sơ đồ, so sánh |
| Chữ chính | #0A192F / #0F2744 | Tiêu đề, nội dung quan trọng |
| Chữ phụ | #334155 / #475569 | Mô tả và chú giải |
| Xanh chính | #2563EB | Nhánh chủ đạo, bước đang xét |
| Xanh ngọc đậm | #0F766E | Nhóm chức năng phụ |
| Thành công | #15803D | Kết quả đạt, kiểm thử qua |
| Cam | #F97316 | Viền, biểu tượng, điểm phê duyệt |
| Chữ cảnh báo | #9A3412 trên #FFF7ED | Cảnh báo có nội dung đọc |
| Tím | #7C3AED | Nhóm thứ ba, tri thức/cấu hình |
| Viền | #E2E8F0 | Thẻ và phân cách nhẹ |

Một slide thường dùng navy, neutral và 2–3 màu nhấn. Có thể dùng bốn màu phân loại cho bốn thành phần, nhưng không thêm màu chỉ để trang trí. Không dùng xanh mint, cyan hoặc cam sáng làm chữ nhỏ trên nền trắng.

Dùng tỷ lệ tương phản WCAG làm mục tiêu tham chiếu: ít nhất 4,5:1 cho chữ thường, 3:1 cho chữ lớn theo định nghĩa WCAG. Đây không phải chứng nhận slide đạt toàn bộ WCAG; không tuyên bố đã đạt khi chưa đo. [N5]

Không chỉ dùng màu để phân biệt; thêm nhãn, hình dạng hoặc biểu tượng. Nền chuyển sắc không đi qua vùng nội dung khiến một phần chữ khó đọc.

## 5. Hai nhánh nhận diện

**TRANG-SANG — Infographic giảng dạy:** nền trắng, thẻ bo góc, bóng nhẹ, hình vector hai tông hoặc 3D mềm, chữ phẳng sắc nét. Trang trí góc ít và không nằm sau chữ. Đây là mặc định.

**MO-CHUONG-TOI — Minh họa mở chương:** nền navy, ánh cyan/mint/tím nhẹ, kính 3D, đường hạt tinh tế. Phù hợp nền không chữ, tiêu đề chương, ẩn dụ chuyển hóa. Không sử dụng cho các bảng hoặc tài liệu có chữ dày nếu người dùng không yêu cầu.

Cùng phong cách nghĩa là cùng màu, kiểu chữ, độ bo, hình neo, độ dày đường và cách đánh số; không nghĩa là cùng vị trí từng thẻ. Không dùng robot, cuốn sách và bộ não lặp lại ở mọi thẻ nếu chúng không giải thích chức năng.

## 6. Ngôn ngữ sơ đồ

Mũi tên liền một chiều: trình tự hoặc luồng truyền. Hai chiều: trao đổi có thật. Nét đứt: chú giải, phản hồi hoặc ranh giới tùy ngữ cảnh, cần nhất quán. Đường không mũi tên: quan hệ thành phần. Hình thoi: câu hỏi quyết định, có nhánh điều kiện rõ ràng.

Chu trình phải có đường quay về hợp lý. So sánh phải có các tiêu chí cùng hàng. Ma trận phải có hai trục và nhãn. Kiến trúc phải phân biệt công cụ, dữ liệu, bộ nhớ, con người và môi trường, không đặt cùng tầng chỉ để đẹp.

Phê duyệt và an toàn nên là nhãn/điểm kiểm soát hoặc vùng bao, không phải lời hứa mọi thao tác đều an toàn tuyệt đối.

## 7. Từ điển Việt hóa

| Thuật ngữ nguồn | Cách thể hiện mặc định |
|---|---|
| Prompt | Câu lệnh / yêu cầu |
| Prompt Engineering | Thiết kế câu lệnh |
| Harness Engineering | Thiết kế môi trường điều phối AI |
| Workflow | Quy trình |
| Workspace | Không gian làm việc |
| Task | Nhiệm vụ |
| Output | Đầu ra |
| Input | Đầu vào |
| Checklist | Danh sách kiểm tra |
| Approval Gate | Điểm phê duyệt |
| Human-in-the-Loop | Con người tham gia giám sát/phê duyệt |
| Reflection Loop | Vòng lặp đúc kết kinh nghiệm |
| Artifacts | Sản phẩm đầu ra |
| Canvas | Vùng làm việc trực quan |
| Memory | Bộ nhớ |
| Tool | Công cụ |
| Plugin | Tiện ích mở rộng |
| Command | Lệnh |
| SOP | Quy trình thao tác chuẩn |
| Template | Biểu mẫu |
| Diff | Phần thay đổi giữa các phiên bản |
| Rollback | Khôi phục phiên bản trước |
| Agent / AI Agent | Tác nhân AI, trừ khi đã khóa nhãn khác |

Đây là lựa chọn biên tập cho dự án, không khẳng định là bản dịch duy nhất. Giữ đúng tên riêng và cú pháp như Google Gemini, AGENTS.md, SKILL.md, `name:`, `description:`. Những khóa mã phải giữ nguyên là ngoại lệ kỹ thuật, không phải tất cả từ tiếng Anh đều là tên riêng.

## 8. Độ chính xác và hình minh họa

Ảnh giao diện tự dựng phải được mô tả là “giao diện minh họa”, không khẳng định là ảnh chụp phiên bản thật. Nếu cần hướng dẫn bấm nút đúng vị trí, dùng ảnh chụp thực tế được cung cấp hoặc nguồn đã kiểm chứng.

Không tái sử dụng các khẳng định kiểu “100% có dẫn nguồn”, “không ảo giác”, “tiết kiệm 70% token”, “miễn nhiễm mọi sai sót” từ ảnh cũ như dữ kiện. Với nhiệm vụ kiểm chứng, tìm nguồn; với nhiệm vụ biên tập, đề xuất cách diễn đạt thận trọng; với nhiệm vụ dịch nguyên văn, nêu vấn đề mà không âm thầm sửa.

Ảnh không chữ: không thêm `>_`, `{}`, `/`, số thứ tự hay dòng chữ giả. Khi yêu cầu vừa muốn ký hiệu cụ thể vừa cấm mọi ký tự, ưu tiên yêu cầu cấm tuyệt đối; dùng cửa sổ dòng lệnh trống, các khối hình hoặc biểu tượng đồ họa thay thế.

## 9. Ảnh và thành phần chỉnh sửa được

Ảnh có chữ tiện chèn nhanh nhưng không có lớp chữ chỉnh sửa riêng. Với nội dung thay đổi thường xuyên, công thức, số liệu hoặc đoạn mã cần chính xác, đề xuất ảnh nền/hình neo + chữ/sơ đồ riêng trong PowerPoint. Microsoft khuyến nghị không để chữ trong ảnh là cách duy nhất truyền tải thông tin quan trọng, đồng thời bổ sung mô tả thay thế phù hợp. [N4]

Không xuất một ảnh đặt trên slide rồi gọi đó là “mẫu slide chỉnh sửa hoàn toàn”. Không gọi PNG có phong cách vector là SVG hoặc vector thật.
