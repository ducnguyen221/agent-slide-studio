---
name: slide-craft
description: Use when routing slide-deck authoring requests between canonical deck planning, native-slide workflows, and the Codex slide infographic image workflow. Verify any renderer or CLI in the current checkout before claiming it is available.
---

# Định tuyến sản xuất slide

Dùng skill này khi người dùng yêu cầu tạo, chỉnh cấu trúc hoặc tối ưu một bộ slide và cần chọn đúng nhánh sản xuất. Trước hết chốt outline và nội dung canonical; sau đó chọn đầu ra theo khả năng đã được kiểm chứng trong checkout hiện tại.

## Chọn nhánh

- **Ảnh infographic cho slide:** dùng [slide-infographic](../slide-infographic/SKILL.md): nội dung canonical → prompt → ảnh raster → QA trên ảnh thật. Nhánh này mặc định `TEXT_SAFE`, hỗ trợ `DIRECT_TEXT` best-effort và `NO_TEXT`.
- **PowerPoint native có thể chỉnh sửa:** chỉ dùng renderer hoặc quy trình đã tồn tại và đã được kiểm chứng trong checkout hiện tại. Ảnh raster không trở thành shape/text native chỉ vì được chèn vào PPTX.
- **HTML reconstruction:** đang thuộc Phase 2 planned, không phải năng lực hiện hành của gói tài liệu này.

## Cổng làm việc

1. **Outline:** tách nội dung thành slide có mục tiêu rõ, kiểm soát tải nhận thức và xin chốt các quyết định còn mơ hồ.
2. **Canonical:** khóa chữ, số, đơn vị, thứ tự và quan hệ trước khi chọn hình thức thể hiện.
3. **Đầu ra:** chuyển sang nhánh phù hợp ở trên và áp tiêu chí QA riêng của artifact thực tế.

Không tự suy ra tên lệnh, profile thiết kế hay khả năng editable từ tài liệu cũ. Không hứa đúng canvas, chính tả hoặc thành công ngay lần đầu chỉ dựa trên prompt; phải kiểm artifact đầu ra thật.
