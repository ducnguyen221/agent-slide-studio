# Hệ phân loại nhiều chiều

## Hai lớp cần phân biệt

**Bố cục cấu trúc (L)** mô tả quan hệ kiến thức. **Mẫu infographic minh họa (I)** kết hợp cấu trúc với hình neo, icon, ví dụ chữ ngắn và cách nhấn màu. Cả hai đều có thể dùng trên slide PowerPoint. “Infographic” không phải đối lập với “quy trình”: một infographic có thể mang quan hệ quy trình, so sánh hoặc kiến trúc.

Để thuận tiện duyệt ảnh, mỗi mẫu có một **nhóm chính**. Thẻ nhiều chiều cho phép mẫu xuất hiện ở nhiều kết quả lọc mà không nhân bản tệp hoặc đổi mã.

## Chín nhóm chính, mười bảng xem trước

G01 mở đầu; G02 khái niệm; G03 quy trình; G04 so sánh; G05 kiến trúc;
G06 dữ liệu; G07 giải thích; G08 thực hành; G09 infographic minh họa.
G09 có hai nhánh: G09A quy trình/kiểm soát và G09B khung năng lực/kiến trúc.
Bảng G09A/B đều thuộc G09, không làm số nhóm chính tăng lên mười.

## Các chiều lọc độc lập

| Chiều | Câu hỏi quyết định | Ví dụ |
|---|---|---|
| home_group | Duyệt thư viện từ đâu? | G03, G09A |
| intent | Người xem cần làm gì? | Giải thích, so sánh, quyết định, thực hành |
| topology | Quan hệ thật là gì? | Vòng lặp, phân tầng, ma trận, trước–sau |
| representation | Mức triển khai thị giác? | Sơ đồ cấu trúc; infographic minh họa |
| density | Bao nhiêu chữ trên trang? | D0, D1, D2 |
| style | Cách thể hiện? | Trắng phẳng, trắng minh họa, navy |
| deck_phase | Vai trò trong bài? | Mở, giải thích, bằng chứng, ứng dụng, thực hành, kết |
| data_requirement | Có cần số thực? | Không; số thực hoặc ví dụ được gắn nhãn |
| output_modes | Cách đưa lên slide? | FULL, TITLE_RESERVED, EDITABLE_OVERLAY, NO_TEXT |

**D1 là mặc định:** 35–70 đơn vị cách trắng toàn slide. Đây là quy ước biên tập, không là từ ngôn ngữ học hoặc token của mô hình. Mỗi vùng một nhãn, một câu ngắn; tối đa một câu đúc kết. D2 (71–100) chỉ dùng có chủ đích. Không thu chữ để vừa số khối.

## Quy tắc chọn

1. Xác định mục tiêu và quan hệ, chọn 1–3 mã L.
2. Người dùng cần biểu tượng, hình minh họa và ví dụ? Tìm I theo base_layouts/intent; không chỉ đổi màu khung L.
3. Chọn mật độ và phong cách. Không dùng phong cách như một bố cục mới để tăng số lượng giả.
4. Khi ghép cả bài, dùng vai trò trang và mạch nội dung, không luân phiên mẫu ngẫu nhiên.

## Tính ổn định

Không đổi hoặc tái sử dụng mã đã phát hành. Biến thể sau này giữ mã nền, thêm variant_id có nghĩa. Ví dụ I01 là một vòng lặp minh họa, còn “trắng” hay “navy” là tham số. Không tạo mã mới chỉ vì đổi sắc xanh.

Thông tin máy đọc: [groups.json](groups.json), [facets.json](facets.json), [registry L](../archetypes/registry.json), [registry I](../infographics/registry.json).
