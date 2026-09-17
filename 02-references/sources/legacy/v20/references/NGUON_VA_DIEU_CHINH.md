# Nguồn, phần kế thừa và điều chỉnh

## Nguồn nội bộ được cung cấp

**[N1]** `01_tu_duy_kien_truc_slide.md` — Tư duy & kiến trúc slide giảng dạy đào tạo chuẩn hóa. Dùng các mục: khác biệt mục tiêu đào tạo; gom cụm; hình neo; tiêu đề hành động; 10 Archetypes; quy trình chuyển hóa văn bản. Bản gốc giữ nguyên trong thư mục này.

**[N2]** `02_thiet_ke_infographic_va_prompts.md` — Đặc tả thiết kế infographic & prompt engineering tạo ảnh slide. Dùng các mục: design tokens; lề; cấu trúc thẻ; sóng so le; khối tiện ích; prompt toàn slide và biểu tượng; kiểm định. Bản gốc giữ nguyên trong thư mục này.

**Chuỗi ảnh tham chiếu:** những ảnh được cung cấp và tạo trong cuộc trò chuyện, cùng các yêu cầu thiết kế AIA-102 được truy xuất: tiếng Việt, 16:9, lề, nền trắng, bảng so sánh, vòng lặp, phân tầng, phân cấp, hình nền không chữ. Không khẳng định đã rà soát toàn bộ kho hội thoại AIA-102 ngoài phần truy xuất được.

## Nguồn ngoài được đối chiếu riêng

**[N3] Microsoft Support — Change the size of your PowerPoint slides.** Căn cứ cho tùy chọn Widescreen 16:9 và kích thước 13,333 × 7,5 inch.
https://support.microsoft.com/en-us/powerpoint/change-the-size-of-your-powerpoint-slides

**[N4] Microsoft Support — Make your PowerPoint presentations accessible to people with disabilities.** Căn cứ cho phông không chân, cỡ chữ từ 18 pt, khoảng trắng và không dùng chữ trong ảnh làm kênh thông tin quan trọng duy nhất.
https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities

**[N5] W3C — Understanding SC 1.4.3: Contrast (Minimum), WCAG 2.2.** Căn cứ cho mức tương phản 4,5:1 với chữ thường và 3:1 với chữ lớn. Chỉ dùng làm chỉ tiêu tham chiếu về tương phản, không chứng nhận toàn bộ ảnh/slide đạt WCAG.
https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

Ngày đối chiếu các nguồn ngoài: 17/09/2026. Không dùng những nguồn này để xác nhận các tính năng của Google Antigravity, Gemini hay cách hoạt động chính thức của SKILL.md.

## Các điều chỉnh thiết kế đề xuất — không phải nguyên văn bản gốc

| Nội dung | Bản gốc | Quyết định trong bộ mới |
|---|---|---|
| Số nhóm | 3–4 cụm; quy trình 3–5 bước | Giữ là điểm xuất phát, không bỏ bước thật để đủ số |
| Lề đáy | Mục kích thước ghi 70 px; QA yêu cầu tối thiểu 80 px | Chốt 80 px để thống nhất; vẫn giữ trái/phải 100, trên 90 |
| Chữ thân bài | Ví dụ QA dùng 14 pt | Nâng mục tiêu chính lên 18–22 pt; ghi chú nhỏ không chứa ý thiết yếu |
| Tiêu đề | Mẫu thiên về in hoa, có ví dụ dài | Tiêu đề ngắn, tối đa hai dòng; không ép toàn bộ in hoa |
| Chân trang | Mô tả luôn tận dụng 25% phía dưới | Mặc định một khối gọn khoảng 10–15%; chỉ mở rộng khi nội dung cần; bỏ ở hình không chữ |
| Ngôn ngữ prompt | Nhiều mẫu tiếng Anh và tham số mô hình cũ | Prompt trung lập công cụ, danh sách chữ tiếng Việt được khóa |
| Số bố cục | 10 kiểu | Giữ 10 mã đầu; bổ sung 10 biến thể, có ghi nguồn từng kiểu |
| Phong cách | Vector hoặc 3D trong thẻ; cover navy | Tách rõ infographic sáng với hình mở chương/nền tối |
| Đầu ra | Toàn slide và hình neo riêng | Bổ sung chế độ chừa tiêu đề, quy tắc sửa vùng và bàn giao Word |
| Kiểm định | Chủ yếu thiết kế | Thêm độ chính xác nội dung, thuật ngữ, nguồn và khả năng đọc thực |

Các quy định về số từ, số slide lặp bố cục, điểm QA và tỷ lệ vùng trống là đề xuất vận hành của bộ mới, không được gắn nhãn chuẩn quốc tế hay kết quả nghiên cứu.

## Danh mục ảnh tham chiếu

Các ảnh chỉ dùng để nhận diện phong cách. Một số ảnh chứa chữ tiếng Anh, chữ dày, tuyên bố tuyệt đối hoặc chi tiết sản phẩm chưa được kiểm chứng; không được xem là bản nội dung mẫu đã đạt kiểm định.

- `01_quy_trinh.png`: tham chiếu thẻ quy trình, huy hiệu và màu chuyển tiếp; không sao chép các nhãn chưa Việt hóa.
- `02_so_sanh.png`: tham chiếu hai cột và mũi tên chuyển hóa; không dùng làm định nghĩa đầy đủ về AI.
- `03_vong_lap.png`: tham chiếu chu trình bốn bước, cam nhấn tại bước cập nhật; không sao chép lời hứa “miễn nhiễm sai sót”.
- `04_giai_phau_tai_lieu.png`: tham chiếu tài liệu bên trái và chú giải bên phải; không sao chép các khẳng định về schema hay loại bỏ ảo giác.
- `05_bon_nhom_nang_luc.png`: tham chiếu lưới 2 × 2, biểu tượng lớn và đường phân cách; không dùng làm nguồn xác thực tính năng.
- `06_nen_khong_chu.png`: tham chiếu navy–cyan, vật thể hai phía và vùng trống trung tâm.
