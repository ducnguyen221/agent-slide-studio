# ĐẶC TẢ THIẾT KẾ INFOGRAPHIC & PROMPT ENGINEERING TẠO ẢNH SLIDE
*(Infographic Component Specs & AI Visual Prompt System)*

> **Tài liệu tham chiếu 02** — Thuộc skill `presentation-infographic`.  
> Phân rã từ 5 slide mẫu thực chiến chuẩn Enterprise / Banking / Tech Training (KPIM standard).  
> Cung cấp thông số hình học, token màu sắc, giải phẫu thẻ (Card Anatomy) và bộ công thức prompt AI (Flux.1 / Midjourney v6 / DALL-E 3) để sinh ra slide và visual assets đẳng cấp cao.

---

## 1. Hệ thống Design Tokens (Màu sắc & Thông số Kỹ thuật)

Lấy cảm hứng trực tiếp từ các slide mẫu (Ngân hàng, AI Campaign, Chấm điểm khách hàng):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PALETTE MÀU CHUẨN DOANH NGHIỆP                    │
├───────────────────┬───────────────────┬──────────────────┬──────────────────┤
│ PRIMARY DEEP NAVY │ ACCENT ELECTRIC   │ HIGHLIGHT ORANGE │ SURFACE & BORDER │
│ #0A192F / #0F2744 │ #2563EB / #00B0F0 │ #F97316 / #EA580C│ #FFFFFF / #E2E8F0│
│ (Tiêu đề, Badge)  │ (Mũi tên, Active) │ (Warning, Bóngđèn│ (Nền Card, Viền) │
└───────────────────┴───────────────────┴──────────────────┴──────────────────┘
```

### 1.1. Bảng mã màu chi tiết
* **Primary Tech Ink (Xanh tím than đậm):** `#0A192F` hoặc `#0F2744` — Dùng cho Action Title, số thứ tự badge, viền chính.
* **Secondary Brand Blue (Xanh dương hiện đại):** `#1E40AF` hoặc `#2563EB` — Dùng cho tiêu đề card, icon chính, đường nối.
* **Accent Warning / Highlight (Cam rực rỡ):** `#F97316` hoặc `#EA580C` — Dùng cho hộp Lưu ý quan trọng, icon bóng đèn `💡`, icon đích ngắm `🎯`, tag chú ý.
* **Semantic Status (Phân loại 3 mức):**
  * *Mức Cao (High / Success):* Nền `#F0FDF4`, Viền `#86EFAC`, Chữ & Icon `#16A34A` (Xanh lá).
  * *Mức Trung bình (Medium / Warning):* Nền `#FFFBEB`, Viền `#FDE68A`, Chữ & Icon `#D97706` (Vàng hổ phách).
  * *Mức Thấp (Low / Alert):* Nền `#FEF2F2`, Viền `#FECACA`, Chữ & Icon `#DC2626` (Đỏ san hô).
* **Neutral Surface & Text:**
  * Nền slide: `#FFFFFF` (hoặc `#F8FAFC` xám siêu nhạt).
  * Nền thẻ (Card): `#FFFFFF` với bóng mờ `rgba(15, 39, 68, 0.06) 0px 8px 24px`.
  * Viền thẻ (Border): `1px solid #E2E8F0`.
  * Body Text: `#475569` (Slate gray, không dùng đen tuyệt đối để tránh mỏi mắt).

### 1.2. Kích thước & Lưới (Cho Canvas 16:9 - 1920x1080)
* **Safe Zone Lề ngoài:** Top $90\text{px}$, Bottom $70\text{px}$, Left $100\text{px}$, Right $100\text{px}$.
* **Khoảng cách giữa các Card (Gutter):** $20\text{px} - 32\text{px}$.
* **Bo góc (Border Radius):** 
  * Card lớn: $16\text{px}$.
  * Huy hiệu số (Badge): Tròn hoàn toàn ($50\%$) hoặc Bo góc $8\text{px}$.
  * Pill Tag (Chân card / Phân loại): $9999\text{px}$ (Pill bo tròn 2 đầu).

---

## 2. Giải phẫu Thành phần (Component Anatomy) từ 5 Slide Mẫu

### 2.1. Header & Brand Accent
* **Góc trên bên trái:** Dải vát chéo đa giác thương hiệu (2 mảng màu: Navy đậm xếp cạnh Cam rực).
* **Góc trên bên phải:** Họa tiết vi mạch công nghệ (Circuit line art mờ với các chấm tròn kết nối node).
* **Action Title:** Font Sans-serif in hoa, đậm, size $34 - 40\text{pt}$, màu `#0A192F`.
* **Subtitle:** Nằm ngay dưới tiêu đề, font nghiêng hoặc thường, size $16 - 18\text{pt}$, màu `#334155`, giải thích câu hỏi *"So what?"* (Giá trị mang lại là gì).

---

### 2.2. Card Quy trình Modular (Process Step Card)
Mỗi card trong quy trình $3 - 5$ bước (như Mẫu 1, 3, 4) được cấu tạo từ 5 lớp:

```text
┌─────────────────────────────────────────────────────────┐
│                     [ 01 ] ◄── Huy hiệu số nổi bật      │
│                                (Vòng tròn Navy đậm)     │
│             ┌─────────────────────────┐                 │
│             │                         │                 │
│             │     VISUAL ANCHOR       │                 │
│             │  (Icon 3D Clay / Biểu đồ│                 │
│             │   Vector phẳng 2-tone)  │                 │
│             │                         │                 │
│             └─────────────────────────┘                 │
│                                                         │
│   TIÊU ĐỀ BƯỚC (IN HOA, BOLD, 18-20pt)                  │
│   Mô tả định hướng 1 dòng                               │
│                                                         │
│   ✔ Ý triển khai 1 (Checkmark tròn xanh)                │
│   ✔ Ý triển khai 2                                      │
│   ✔ Ý triển khai 3                                      │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🎯 Output: Sản phẩm đầu ra cụ thể của bước này       │ │ ◄── Pill Tag chân thẻ
│ └─────────────────────────────────────────────────────┘ │       (Nền xanh nhạt)
└─────────────────────────────────────────────────────────┘
```

* **Visual Anchor theo từng dạng bước:**
  * *Bước chọn/đo lường:* Clipboard kiểm tra + cụm avatar người dùng.
  * *Bước chuẩn hóa:* Đồ thị đường cong $0 \rightarrow 1$ với điểm chốt màu cam.
  * *Bước cân đo/trọng số:* Cán cân công lý 2 đĩa cân (màu xanh navy kết hợp đĩa cam).
  * *Bước tính điểm/chỉ số:* Đồng hồ đo tốc độ (Gauge meter) có kim chỉ và 3 dải màu xanh-vàng-cam.
  * *Bước tạo Campaign AI:* Não bộ AI phát sáng + Loa phóng thanh + Biểu tượng phân khúc.
  * *Bước tạo Content AI:* Tài liệu văn bản + Khung chat đa kênh + Phong bì thư.
  * *Bước tạo Media AI:* Màn hình banner + Điện thoại di động hiển thị video.

---

### 2.3. Bố cục Sóng Uốn Lượn Bậc Thang (Staggered Wave Use-case Layout)
Học từ **Slide Mẫu 5 (Các Usecase Digital Marketing Ngân hàng)**:
* Thay vì xếp 5 card thẳng hàng gây buồn ngủ, các card được **đặt sole cao - thấp**:
  * Card 01: Vị trí Cao
  * Card 02: Vị trí Thấp
  * Card 03: Vị trí Cao
  * Card 04: Vị trí Thấp
  * Card 05: Vị trí Cao
* **Đường nối sóng (Curved Wave Rail):** Một đường line màu xanh dương mềm mại uốn lượn xuyên suốt từ Card 01 qua Card 05, kết nối các badge số với nhau.
* **Điểm nhấn 3D Claymorphism:** Mỗi card sở hữu 1 mô hình 3D đất sét mờ siêu thực (Isometric Clay 3D):
  1. *Thẻ 1 (Hóa đơn):* Điện thoại 3D + tờ hóa đơn cuộn + chồng tiền xu vàng.
  2. *Thẻ 2 (Tiết kiệm):* Laptop phát livestream + heo đất màu hồng pastel + loa phóng thanh xanh.
  3. *Thẻ 3 (Thẻ tín dụng):* Thẻ ngân hàng nổi chip vàng + tờ lịch hẹn thanh toán.
  4. *Thẻ 4 (Du học):* Quả địa cầu 3D + mũ cử nhân xanh + laptop mini.
  5. *Thẻ 5 (Đáo hạn):* Két sắt ngân hàng màu xanh navy + khiên bảo vệ kim loại + tiền vàng.

---

### 2.4. Khối Tiện ích Tầng Dưới (Lower Deck Utilities)
Slide chuyên nghiệp luôn tận dụng $25\%$ không gian phía dưới cho các khối bổ trợ đắt giá:

#### Kiểu 1: Khung Phân loại 3 Tầng & Hành động (Tiered Classification Box)
* Gồm 3 cột nhỏ: `70-100 Ưu tiên cao` (Xanh lá) | `40-69 Trung bình` (Vàng) | `0-39 Thấp` (Đỏ).
* Dưới mỗi thang điểm ghi rõ hành động thực thi tức thì (ví dụ: *Tiếp cận ngay cá nhân hóa* vs *Hạn chế tần suất*).

#### Kiểu 2: Thanh Công thức Toán học (Formula Bar)
* Bên trái: Ký hiệu Tổng Sigma $\sum$ hoặc $f(x)$ đặt trong vòng tròn Navy đậm.
* Giữa: Công thức toán học trực quan (ví dụ: $\text{Điểm} = \sum (\text{Chuẩn hóa}_i \times \text{Trọng số}_i) \times 100$).
* Phải: Biểu đồ mini + Quy tắc suy diễn (*"Giá trị càng cao mức độ ưu tiên càng lớn"*).

#### Kiểu 3: Hộp Lưu ý Quan trọng / Key Insight Callout
* Nền màu be/cam siêu nhạt (`#FFF7ED`), viền cam (`#F97316`, $1.5\text{px}$).
* Icon: Bóng đèn vàng/cam `💡` hoặc Khiên cảnh báo `🛡!`.
* Chứa $2 - 3$ gạch đầu dòng nhấn mạnh điều kiện cốt lõi (ví dụ: *AI hỗ trợ không thay thế kiểm duyệt; Luôn tuân thủ compliance*).

---

## 3. Bộ Công thức Prompt AI Tạo Ảnh Slide & Asset 3D

Khi dùng các mô hình AI tạo ảnh thế hệ mới (**Flux.1 Schnell/Dev**, **Midjourney v6.1**, **Ideogram v2**, hoặc **DALL-E 3**), hãy áp dụng các công thức prompt chuẩn xác sau.

---

### Formula 1: Tạo Toàn bộ Slide Infographic Hoàn chỉnh (Full 16:9 Slide)
> **Mục tiêu:** Sinh ra bức ảnh slide tổng thể đã chia card, có tiêu đề, icon và layout hoàn chỉnh.

```text
[Bối cảnh & Tỷ lệ]:
A professional enterprise corporate presentation slide, 16:9 aspect ratio, clean modern infographic layout for executive training.

[Tiêu đề & Header]:
At the top, a bold modern corporate header in dark navy "#0A192F" with an orange accent polygon slash on the top left corner, subtle tech circuit board line watermark in the background. Action title text area and italic subtitle.

[Bố cục chính - Main Body]:
In the center, a horizontal 4-step workflow pipeline with four rounded rectangle white cards, separated by clean dark navy directional arrows. Each card has a floating dark navy circular badge with numbers "1", "2", "3", "4" on top. 
Card 1 features a modern vector clipboard with checklist. 
Card 2 features an ascending cartesian line graph with orange trend line. 
Card 3 features a balanced dual-pan scale in navy and orange. 
Card 4 features a colorful circular gauge speedometer meter pointing to high score. 
Each card has clean bullet points and a pill-shaped output tag at the bottom.

[Tầng tiện ích dưới - Lower Deck]:
At the bottom, two modular utility boxes: on the left, a 3-tier classification container with green, amber, and red status tags; on the right, a warm peach callout box with a bright orange lightbulb icon.

[Phong cách & Render]:
Ultra-clean UI design, corporate fintech aesthetics, Figma design system style, high contrast, crisp vector elements, soft drop shadows, pure white and slate gray background, studio lighting, 8k resolution, vector graphic presentation deck --ar 16:9 --v 6.1 --style raw
```

---

### Formula 2: Tạo Visual Asset 3D Isometric / Claymorphism (Tách nền ghép slide)
> **Mục tiêu:** Tạo các vật thể 3D nổi bật để đặt vào trung tâm các Card hoặc Cover Slide (giống Slide Mẫu 2 & 5).

#### Asset A: Laptop Trung tâm Phân tích Dữ liệu (Dành cho Slide Cover / Tech Stack)
```text
3D isometric illustration of a giant sleek modern laptop standing open at a 45-degree angle, floating on a pure solid white background. On the laptop screen, a high-tech dark mode analytics dashboard is glowing with colorful charts, interactive funnel diagram, AI neural network brain graph, and pie charts. Around the laptop, miniature 3D professionals in modern business casual attire are analyzing data: one woman holding a tablet, one man pointing at a chart. Floating around are 3D marketing megaphone, gears, target with arrow, and colorful icon spheres. Claymorphism style, smooth matte finish, vibrant royal blue, electric cyan, and bright orange accents, soft ambient occlusion, clean studio lighting, isolated on white background, 8k render, octane render style --ar 1:1 --v 6.1
```

#### Asset B: Bộ 5 Vật phẩm Ngân hàng / Fintech 3D Đất sét (Dành cho 5 Usecase Cards)
```text
Set of 5 isolated 3D claymorphism icons on a solid clean white background, arranged neatly:
1. A modern smartphone displaying a digital payment receipt with floating gold coins.
2. A sleek laptop showing a live video stream with a pink piggy bank and a blue megaphone beside it.
3. A sleek blue credit card with gold chip next to a small desk calendar showing checked dates.
4. A stylized 3D earth globe wearing a blue graduation cap next to an open notebook.
5. A heavy steel bank safe vault door with a silver security shield and stacks of golden coins.
Smooth plasticine clay texture, matte finish, pastel blue, vibrant navy, and warm gold colors, soft studio rim lighting, minimal shadows, isolated on pure white, high-detail 3D rendering --ar 16:9 --v 6.1
```

---

### Formula 3: Tạo Sơ đồ Khái niệm Bento Grid Đa tầng (Concept Bento Deck)
```text
Modern presentation slide layout in Bento Grid style, 16:9 ratio. Clean white background with faint dot grid pattern. 
Top left: Large feature card containing an AI neural network icon with glowing orange nodes and 3 key bullet points. 
Top right: Two stacked smaller cards with clean line icons representing "Security Compliance" and "Speed Optimization". 
Bottom row: A wide horizontal workflow bar showing a 3-phase progression (Data Ingest -> Prompt Engineering -> Output Verification) with interconnected pills. 
Sleek typography, subtle borders, high legibility, corporate enterprise aesthetic, Linear app design style, Stripe design ethos, no blur, razor-sharp vector shapes --ar 16:9 --v 6.1
```

---

## 4. Bảng Kiểm Tra Chất Lượng Infographic Trước Khi Xuất Xưởng (QA Checklist)

Trước khi chuyển giao slide cho người dạy hoặc xuất file:

| Tiêu chí | Kiểm tra đạt chuẩn | Cách khắc phục nếu lỗi |
|---|---|---|
| **1. Khoảng cách an toàn (Safe Margin)** | Nội dung cách mép tối thiểu $80\text{px}$? | Thu nhỏ kích thước card, kéo lùi vào trong. |
| **2. Độ tương phản chữ (Contrast)** | Text nhỏ nhất vẫn đọc rõ từ cự ly $2\text{m}$? | Đổi màu text sang `#0F2744` hoặc `#334155`. Tăng size tối thiểu $14\text{pt}$. |
| **3. Điểm tựa thị giác (Visual Anchor)** | Mỗi card có đúng 1 hình/icon làm tâm điểm? | Bỏ các icon rải rác thừa; gom vào 1 vị trí cố định trên card. |
| **4. Đồng bộ phong cách (Icon Consistency)** | Toàn bộ icon cùng 1 phong cách (đều là Line hoặc đều là 3D)? | Thay thế các icon lạc quẻ; không trộn 2D vẽ tay với 3D bóng bẩy. |
| **5. Phân tầng thông điệp (Information Hierarchy)** | Tiêu đề $>$ Tên bước $>$ Bullet point $>$ Ghi chú? | Tuân thủ type scale: Tiêu đề ($36\text{pt}$), Tên bước ($20\text{pt}$), Bullet ($14\text{pt}$). |
| **6. Khối tiện ích (Utility Deck)** | Có đúc kết bằng công thức, cảnh báo hoặc takeaway? | Thêm 1 Callout Box màu cam hoặc 1 thanh tóm tắt ở đáy slide. |
