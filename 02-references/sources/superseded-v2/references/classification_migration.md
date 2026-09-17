# Di chuyển danh mục v2.0 → v2.1

- Trước: archetypes/INDEX.md liệt kê 36 bố cục theo mã; ba contact sheet chia mỗi trang 12 mã.
- Nay: archetypes/INDEX.md trỏ tới CATALOG.md chia theo ý đồ. registry.json giữ nguyên dữ liệu cũ và bổ sung thẻ.
- L01–L36, tên tệp và ảnh cũ không đổi. Người dùng không phải đổi yêu cầu đã lưu.
- L37–L48 là đề xuất cấu trúc mới. I01–I12 là lớp infographic minh họa, có base_layouts tham chiếu L.
- G01–G08 là nhóm chức năng; G09 là nhóm cách thể hiện riêng để dễ tìm theo ảnh mẫu. Vì hai logic khác nhau, intent/topology là chiều lọc độc lập.
- Không thêm frontmatter vào CATALOG hoặc các reference; metadata của thư viện ở JSON, không giả thành schema của Codex/Claude.

Mục tiêu: người dùng có thể nói “G09A, vòng lặp, D1” hoặc “I01”, AI vẫn tìm đúng mẫu.
