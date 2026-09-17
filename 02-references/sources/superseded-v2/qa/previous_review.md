> Bản nguồn kế thừa v20. Khi có khác biệt, dùng SKILL.md và tài liệu hiện hành; xem references/migration.md.

# Kiểm định, chỉnh sửa và bàn giao

## 1. Trước khi tạo ảnh

- [ ] Đã xác định mục tiêu, người xem, thông điệp chính và nguồn nội dung.
- [ ] Đã chọn đúng A hoàn chỉnh / B chừa tiêu đề / C không chữ.
- [ ] Bố cục biểu đạt đúng quan hệ, không chỉ dùng để chứa văn bản.
- [ ] Nội dung được chia cụm mà không làm mất bước hoặc thay nghĩa.
- [ ] Danh sách chữ hiển thị đã rõ; tên riêng và ngoại lệ kỹ thuật đã khóa.
- [ ] Đã ghi lại chữ hoặc số liệu cần kiểm chứng; không tự thêm cam kết tuyệt đối.
- [ ] Đã xác định ảnh tham chiếu nào dùng cho màu, biểu tượng hay bố cục.
- [ ] Vùng trống, lề và khối kết luận không xung đột.

## 2. Sau khi tạo ảnh: kiểm tra bằng kết quả thực

- [ ] Tỷ lệ ảnh thực là 16:9 hoặc đã xử lý để đặt đúng trên slide mà không méo.
- [ ] Không có lỗi dấu tiếng Việt, chữ cụt, từ sai hoặc ký tự rác.
- [ ] Không còn tiếng Anh ngoài danh sách ngoại lệ.
- [ ] Tiêu đề và các khối đúng nội dung đã duyệt; không thiếu/thừa ý.
- [ ] Huy hiệu, nhánh, số bước, hướng mũi tên và chú giải khớp nhau.
- [ ] Chữ, biểu tượng, bóng và đầu mũi tên nằm trong vùng an toàn.
- [ ] Vùng chừa tiêu đề thực sự trống nếu dùng chế độ B.
- [ ] Chế độ C không có chữ, số hoặc ký hiệu bị cấm.
- [ ] Chữ chính đọc được ở kích thước trình chiếu mục tiêu; không chỉ khi phóng to.
- [ ] Hình và chữ có tương phản phù hợp; không khẳng định đạt WCAG nếu chưa đo.
- [ ] Không có chi tiết thương hiệu, logo hoặc giao diện được bịa thành tài sản thật.
- [ ] Nội dung không chỉ dựa vào màu để phân biệt ý nghĩa.

Xem toàn ảnh để kiểm tra bố cục, sau đó xem từng vùng ở độ phân giải gốc để kiểm tra chữ. Có thể xem thêm bản thu nhỏ 1280 × 720 để phát hiện mật độ quá cao; đây không thay thế thử trên thiết bị trình chiếu thực tế.

Nếu không có khả năng xem hoặc đo kết quả, báo “chưa kiểm tra” cho tiêu chí đó. Không tự đánh dấu tất cả đạt chỉ vì prompt đã yêu cầu.

## 3. Điều kiện chặn bàn giao

Sai nội dung trọng yếu; số liệu không có nguồn; thiếu bước; mũi tên làm đảo nghĩa; sai tên riêng/tên tệp; tiếng Anh còn sót ngoài ngoại lệ; chữ chính không đọc được; tiêu đề bị cắt; vùng cần trống có chữ; chỉnh sửa lan ra vùng đã khóa.

Một lỗi chặn phải được sửa, hoặc phải được nêu rõ là chưa giải quyết; điểm thẩm mỹ cao không bù cho lỗi sai nghĩa.

## 4. Bảng điểm nội bộ đề xuất

| Hạng mục | Điểm tối đa |
|---|---|
| Chính xác nội dung và tiếng Việt | 25 |
| Thông điệp và tổ chức kiến thức | 20 |
| Khả năng đọc và khoảng thở | 25 |
| Quan hệ, đường đọc và bố cục | 15 |
| Nhận diện và biểu tượng đồng bộ | 10 |
| Đúng kiểu đầu ra và bàn giao | 5 |

Mốc đề xuất: từ 90/100 và không có lỗi chặn. Đây là công cụ tự rà soát, không phải thang đo được chứng nhận; không cho điểm những phần chưa thực sự kiểm tra.

## 5. Thứ tự sửa lỗi

Sửa nghĩa và thiếu ý → sửa tiếng Việt/tên tệp → sửa quan hệ đường nối → sửa lề và cỡ chữ → sửa màu/tương phản → tinh chỉnh trang trí. Không sửa màu đẹp hơn trước khi sửa nội dung sai.

Tạo phiên bản v01, v02… và ghi thay đổi. “Giữ nguyên” phải được hiểu theo vùng khóa; không xem toàn ảnh là vùng sáng tạo tự do. Với sửa một dòng chữ, ưu tiên ghép/sửa vùng thay vì sinh lại cả trang khi có công cụ thích hợp.

## 6. Gói bàn giao theo nhu cầu

**Bàn giao ảnh:** tệp ảnh cuối, kích thước thực nếu đã đo, nội dung chữ đã duyệt và ghi chú giới hạn nếu còn. Không gửi prompt dài thay cho ảnh khi người dùng yêu cầu ảnh.

**Bàn giao prompt:** đặc tả đủ độc lập để đưa sang công cụ khác: mục tiêu, khung, lề, bố cục, màu, danh sách chữ, biểu tượng và điều cấm. Không phụ thuộc câu “giống ảnh trên” nếu ảnh không đi cùng.

**Bàn giao Word:** kịch bản slide và phiếu thiết kế có mã trang, mục tiêu, chữ, bố cục, hình neo, nguồn, ghi chú giảng viên và trạng thái duyệt. Word là tài liệu biên tập, không phải tập tin thực thi tác vụ.

**Bàn giao PowerPoint chỉnh sửa được:** chỉ xác nhận khi thực sự đã tạo các lớp chữ/hình có thể chỉnh sửa. Nếu chỉ chèn ảnh vào .pptx, phải gọi đúng là “slide chứa ảnh”.

## 7. Khi chèn vào PowerPoint

Chọn tỷ lệ 16:9 phù hợp với bản thiết kế. Microsoft cung cấp tùy chọn Widescreen; kích thước toàn bộ bài trình chiếu cần được xác định trước khi bố trí nội dung. [N3]

Với chế độ A/B đã thiết kế nguyên khung, đặt ảnh phủ đúng khung slide và giữ tỷ lệ. Với chế độ B, thêm tiêu đề dạng chữ PowerPoint vào vùng đã để trắng; không cắt mất vùng trống rồi thu ảnh thêm một lần.

Tách riêng chữ quan trọng, bảng số liệu, mã và công thức khi cần cập nhật hoặc sao chép. Bổ sung mô tả thay thế và bản nội dung văn bản phù hợp để thông tin không chỉ tồn tại trong ảnh. [N4]

Không suy từ “1920 × 1080” rằng chữ đủ lớn; kích thước cuối và khoảng cách người xem mới là điều cần kiểm tra. Cũng không suy từ “PNG chất lượng cao” rằng sơ đồ đã thành vector.
