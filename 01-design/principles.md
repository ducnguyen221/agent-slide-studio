---
title: "Nguyên tắc thiết kế slide"
description: "Tài liệu Nguyên tắc thiết kế slide trong agent-slide-studio."
document_type: design-guide
status: active
---

# Nguyên tắc thiết kế slide

Đọc file này một lần trước khi lập deck. Đây là nguồn canonical cho tư duy slide, mạch bài, mật độ và nhịp toàn bài; quy tắc hình thức nằm ở [design-system.md](design-system.md).

## Slide phục vụ một kết quả

Mỗi slide có một vai trò trong mạch bài, một thông điệp có thể nói thành câu và một quan hệ thị giác chính. Tiêu đề nên nêu kết luận hoặc hành động, không chỉ gọi tên chủ đề. Tách chữ hiển thị khỏi ghi chú giảng viên và nguồn; slide đào tạo phải hỗ trợ người học theo dõi, ghi nhớ và tra cứu nhưng không biến thành trang tài liệu đặc chữ.

Không ép nội dung vào số card có sẵn. Giữ đúng số bước, nhánh, tầng, tiêu chí và ngoại lệ của nghiệp vụ. Khi một trang cần hai luồng chính hoặc chữ phải thu nhỏ mới vừa, tách trang theo nhịp tổng quan → giải thích → ví dụ → thực hành.

## Tổ chức nhận thức

- Dùng chữ và hình để bổ sung cho nhau. Hình neo, icon, card và đường nối phải giải thích ý nghĩa; chúng không chỉ trang trí.
- Gom các ý cùng chức năng thành cụm có ranh giới rõ. Ba đến năm cụm là điểm bắt đầu biên tập, không phải giới hạn khoa học.
- Thiết kế một đường đọc có chủ đích. Cấp bậc thường đi từ kicker/chủ đề → action title → hình neo hoặc khối chính → chi tiết → kết luận cần thiết.
- Dùng mũi tên chỉ khi có hướng, chuyển giao hoặc nhân quả. Vòng lặp phải có cạnh quay về; so sánh phải dùng cùng tiêu chí; ma trận phải có hai trục có nghĩa.
- Mỗi trang chỉ có một lớp trọng tâm. Công thức, cảnh báo hoặc takeaway chỉ thêm khi chúng hoàn tất thông điệp, không tạo một slide thứ hai ở chân trang.

## Mật độ và bản chữ

`D0` không có chữ; `D1` là mặc định gọn; `D2` chỉ dùng khi người xem cần đọc sâu. Các ngưỡng 35–70 và 71–100 đơn vị cách trắng là quy ước biên tập của gói, không phải luật nhận thức hay token. Ưu tiên nhãn ngắn, một câu có ích cho mỗi khối và khoảng trắng đủ phân nhóm. Không bỏ ý, đổi số hoặc thu chữ để đạt ngân sách.

Mọi chữ hiển thị phải có ID ổn định và nguồn. Giữ nguyên tên riêng, cú pháp, số, dấu thập phân và đơn vị đã khóa. Phân biệt rõ nội dung từ nguồn, bổ sung có dẫn chứng, ví dụ giả định và đề xuất. Không tự thêm tỷ lệ hiệu quả, cam kết tuyệt đối hoặc tính năng chưa được xác minh.

## Nhịp toàn bài

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

## Cổng quyết định

Trước khi sang workflow tạo ảnh, deck phải có đủ slide ID, vai trò, thông điệp, nguồn, exact visible text, topology, mã L/I, density, reference và trạng thái. Chọn mã bằng [INDEX](../02-references/INDEX.md), rồi mở đặc tả và ảnh thật tương ứng; không quyết định từ thumbnail hoặc tên mẫu.
