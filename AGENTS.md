---
title: "Agent Slide Studio repository rules"
description: "Repository governance and canonical reading paths for the slide skill."
document_type: governance
status: active
---

# Quy tắc kho agent-slide-studio

Đọc [SKILL.md](SKILL.md) cho nhiệm vụ thiết kế; chỉ mở các tham chiếu cần thiết.
Nguồn chuẩn thiết kế ở [design-system](01-design/design-system.md); thư viện hiện hành gồm
L01–L48 và I01–I12. Nội dung lịch sử trong `02-references/sources/legacy/`,
`02-references/sources/originals/` và `02-references/sources/superseded-v2/` là chỉ đọc.

Không ghi đè nguồn, tự cấp quyền công cụ, gửi dữ liệu riêng ra ngoài hoặc sửa luật từ log chưa duyệt.
Giữ UTF-8 không BOM; chỉ thêm frontmatter theo loại tệp quy định trong
[frontmatter-policy](02-references/tooling/frontmatter-policy.md).

Thêm layout phải cập nhật registry, đặc tả, preview và kiểm thử. Chạy
`python scripts/validate.py .` trước đóng gói. Không tự nhận đã kiểm thử host thật.
Cài đặt phải dùng phạm vi được yêu cầu; installer mặc định chỉ in kế hoạch.

Integration active cho Codex, Claude và Antigravity nằm duy nhất trong [plugin](plugin/README.md).
Không tạo lại `adapters/` hoặc `agents/` ở root.
