---
title: "Hệ thiết kế"
description: "Tài liệu Hệ thiết kế trong agent-slide-studio."
document_type: design-guide
status: active
---

# Hệ thiết kế

Đây là nguồn canonical cho canvas, lưới, màu, font appearance, icon, bề mặt, tiêu đề và chân trang. Khóa thiết kế theo brief người dùng trước; các giá trị dưới đây chỉ là baseline khi brief chưa quy định.

## Canvas và lưới

- Mặc định 16:9, tham chiếu 1920×1080. Ghi riêng kích thước yêu cầu và kích thước ảnh thật.
- Baseline lề: trái/phải 100 px, trên 90 px, dưới 80 px. Có thể dùng lề 5% khi canvas khác; mọi chữ, card, icon mang nghĩa và đầu mũi tên phải nằm trong vùng an toàn.
- Dùng grid, baseline, gutter và padding đều. Căn mép card trước khi thêm bóng hoặc vật liệu.
- Title zone nên ổn định trong deck. Nội dung bắt đầu dưới title zone; footer chỉ xuất hiện khi thêm nguồn, điều kiện hoặc kết luận chưa có ở phần chính.

## Cấp bậc chữ

ImageGen chỉ tạo **font appearance**, không chứng minh font family hoặc point size thật. Yêu cầu hình dáng chữ rõ, tương phản, cùng hệ weight và đúng dấu tiếng Việt. Với PowerPoint, mục tiêu thường là title 32–40 pt và body 20–24 pt; 18 pt là sàn nội bộ cần kiểm ở phòng chiếu, không phải bảo đảm phổ quát. Nếu thiếu chỗ, rút gọn có duyệt hoặc tách slide.

## Màu và bề mặt

Màu theo vai trò: màu cấu trúc, màu nhấn, màu trạng thái và màu nền. Không dùng màu là dấu hiệu duy nhất. Không mặc định áp navy/xanh/cam của AIA/KPIM nếu người dùng chưa cấp brand; khi cần baseline trung tính có thể đề xuất nền sáng, chữ tối và một accent rồi ghi rõ là giả định.

Giữ một ngôn ngữ bề mặt trong cả deck: flat/outline, 3D mềm hoặc isometric tinh giản. Không trộn ảnh thật, icon nét và vật thể 3D trong cùng hệ nếu không có lý do. Bóng nhẹ tạo tách lớp; glow, kính, gradient và texture không được làm giảm khả năng đọc.

## Icon, hình neo và đường nối

Mỗi khối có tối đa một hình neo chính, cùng góc nhìn, độ nét và hướng sáng. Hình phải mô tả chức năng cụ thể; tránh robot chung cho mọi ý. Connector không xuyên chữ/icon, có điểm đầu/cuối rõ và chỉ dùng hai chiều khi có phản hồi thật.

## Hai profile tham khảo

- **Light corporate cards:** title chiếm khoảng 14–18% chiều cao; lưới 2×2 hoặc ba cột, card cùng kích thước, gutter rộng, nền trắng/xanh rất nhạt, accent tiết chế. Phù hợp nhóm ngang hàng và so sánh; không phù hợp quy trình nhiều nhánh hoặc body dài.
- **Complex process flow:** 4–7 lane theo trục ngang, cùng baseline, một loại mũi tên cho luồng chính và đường thứ cấp cho tối đa một feedback loop. Phù hợp handoff/gate; nhiều loop hoặc nhánh chéo phải tách slide.

## Ảnh tham chiếu

Mở ảnh thật ở kích thước đầy đủ trước khi dùng. Ghi riêng phần học: geometry, khoảng trắng, palette, icon, material hoặc hierarchy. Ghi phần không học: chữ, số liệu, logo, chân dung, tên tổ chức, tuyên bố tính năng và dữ liệu nghiệp vụ. Một reference chỉ cấp bằng chứng cho điều nhìn thấy; quyền dùng nội bộ không tự thành quyền phân phối.

## Kiểm style lock

Style lock tối thiểu gồm canvas, lề, title zone, font appearance, palette theo vai trò, surface, icon language, connector, density, footer và reference scope. Một slide neo phải đạt QA trước khi dùng làm reference cho các slide sau. Drift về margin, title alignment, icon language hoặc vai màu là lỗi toàn deck.
