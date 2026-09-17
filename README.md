---
title: "agent-slide-studio"
description: "Tài liệu agent-slide-studio trong agent-slide-studio."
document_type: repository-overview
status: active
---

# agent-slide-studio

Knowledge package để lập cấu trúc deck, chọn bố cục và tạo ảnh slide 16:9 bằng ImageGen native của host. `SKILL.md` ở gốc là entrypoint hiện hành duy nhất.

## Dùng bộ hiện hành

1. Bắt đầu tại [SKILL.md](SKILL.md) và đi đúng đường đọc bắt buộc.
2. Map toàn bộ deck trước khi sinh ảnh; mỗi slide phải có ID, nguồn, exact visible text, topology và mã L/I.
3. Chọn bố cục trong [reference index](02-references/INDEX.md), rồi mở đặc tả, preview và ảnh mẫu thật được dẫn tới.
4. Khóa brand, font appearance, style và nội dung. Nếu còn thiếu, hỏi người dùng một lượt gọn trừ khi họ đã cho phép tự chọn.
5. Dùng prompt bảy phần và integration trong [plugin](plugin/README.md): [Codex](plugin/codex.md), [Claude](plugin/claude.md) hoặc [Antigravity](plugin/antigravity.md).
6. Mở ảnh thật ở kích thước đầy đủ, sửa lỗi bằng ImageGen edit/regenerate và QA lại toàn ảnh trước khi bàn giao.

Image generation chỉ dùng capability native mà host hiện tại thực sự cung cấp. Thiếu capability thì trả `CAPABILITY_UNAVAILABLE` và bàn giao prompt/content lock; không chuyển sang Python, HTML, SVG, browser screenshot hoặc renderer khác.

## Cấu trúc hiện hành

```text
SKILL.md                    entrypoint/router duy nhất
01-design/                  nguyên tắc và hệ thiết kế
02-references/INDEX.md      chỉ mục L01-L48, I01-I12, preview và ảnh mẫu
03-workflow/                bốn bước từ đọc nguồn đến QA/handoff
04-templates/               deck plan, slide prompt, review/handoff
plugin/                     tích hợp Codex, Claude và Antigravity
scripts/                    công cụ hỗ trợ tùy chọn
```

Nội dung lịch sử dưới `02-references/sources/` chỉ để đối chiếu, không thuộc đường đọc active.

## `v1/` là snapshot bất biến

`v1/` giữ bản cũ để truy nguyên. Không sửa, di chuyển, cài hoặc dùng `v1/` như entrypoint. Root hiện tại luôn thắng khi nội dung lịch sử khác với workflow hiện hành.

## Python chỉ là công cụ hỗ trợ

Không cần Python để đọc skill hoặc tạo ảnh qua host. Các script chỉ phục vụ kiểm link/hash/package, validate, cài đặt tùy chọn và bảo trì gallery khi được gọi rõ. Chúng không phải backend tạo slide và không được dùng làm fallback renderer. Xem [scripts/README.md](scripts/README.md) và [INSTALL.md](INSTALL.md) khi cần các thao tác hỗ trợ này.

## Giới hạn trung thực

Ảnh ImageGen là raster. Nó không chứng minh font family, point size hoặc editability thật. Một slide chỉ được đánh dấu đạt khi ảnh đúng revision đã được mở đầy đủ và đối chiếu với content lock, topology, safe margins và style lock.
