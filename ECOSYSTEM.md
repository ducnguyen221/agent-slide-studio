# ECOSYSTEM — Agent Slide Studio trong hệ thống ACD

## 🤝 ACD Ecosystem Integration
- **Role in ACD:** Studio thuộc Nhóm 2 (Production Studio) — xưởng slide và infographic 16:9 tiếng Việt với bố cục L01-L48, infographic I01-I12 và ảnh sinh bằng khả năng ảnh gốc của host. `agent-skill-studio` là xưởng nền cấp chuẩn `SKILL.md` portable, công cụ kiểm (`validate`/`audit`/`package`) và đóng gói skill; repo này tự giữ nghiệp vụ của mình, không nhờ xưởng nền viết thay. Repo chưa có plugin marketplace nên là khách hàng đóng gói (brief AUDIT + package) của xưởng nền.
- **Upstream Controllers:** `agent-executive-team` (deck hội đồng, pitch), `agent-sales-team` (sales pitch deck) và `agent-academy-team` (slide bài giảng) ở mức Cốt lõi; `agent-finance-legal-team`, `agent-hr-team` và repo marketing ở mức Thường xuyên. Nội dung đầu vào từ `agent-data-studio` (số liệu, biểu đồ), `agent-writing-studio` (chữ đã gọt) và `agent-design-studio` (brand token).
- **Downstream Consumers:** Các Team nhận deck và ảnh slide đã QA; `agent-video-studio` nhận khung hình slide làm cảnh dựng.
- **Recommended Bundles:** Bundle B (Sales Pitch Deck 16:9) và Bundle C (slide bài giảng sư phạm). Không thuộc Bundle E; chỉ là bên gửi brief cho `agent-skill-studio` khi cần đóng gói plugin.
- **Handoff Artifacts:** Đầu vào là `production-brief.md` do Team giao, kèm bản đồ deck và khóa chữ theo quy trình của repo. Đầu ra là ảnh slide cùng prompt, báo cáo QA toàn deck và biên nhận nghiệm thu; thiếu khả năng ảnh của host thì bàn giao prompt và khóa nội dung.
