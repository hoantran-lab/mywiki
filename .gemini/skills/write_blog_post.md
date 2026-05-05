# Skill: Viết bài mới cho AI Wiki

## Mô tả
Skill này tự động hóa quy trình viết bài cho AI Wiki (MkDocs Material blog).
Khi được kích hoạt, chỉ cần nhập **chủ đề** — skill sẽ tự research, viết, kiểm chứng và đặt bài vào đúng vị trí.

## Khi nào kích hoạt
- Khi user yêu cầu "viết bài", "tạo bài", "write post", "new post", hoặc đề cập đến việc tạo nội dung mới cho wiki/blog.
- User sẽ cung cấp **chủ đề** (topic) cho bài viết.

## Quy trình thực hiện

### Bước 1: Phân tích chủ đề & lên dàn ý
1. Nhận chủ đề từ user.
2. Xác định:
   - **Category** phù hợp (chỉ được chọn từ danh sách cho phép trong `mkdocs.yml`):
     `LLM`, `Prompt Engineering`, `RAG`, `Agent`, `MLOps`, `Computer Vision`, `NLP`, `Kỹ năng AI`, `AI Cơ bản`, `Case Study`
   - **Level**: `beginner`, `intermediate`, hoặc `advanced`
   - **Tags**: 3-5 tags liên quan
3. Lên dàn ý (outline) cho bài viết bao gồm các phần chính.

### Bước 2: Tìm kiếm thông tin từ nguồn tin cậy
1. **Sử dụng `search_web` tool** để tìm kiếm thông tin từ nhiều nguồn:
   - Tìm kiếm bằng tiếng Anh (kết quả chất lượng hơn) VÀ tiếng Việt nếu cần.
   - Ưu tiên nguồn tin cậy: arXiv, Google AI Blog, OpenAI Blog, Hugging Face, Wikipedia, các trang academic.
   - Tìm kiếm ít nhất **3-5 nguồn khác nhau** cho mỗi bài viết.
2. **Sử dụng `read_url_content` tool** để đọc chi tiết nội dung các nguồn tìm được.
3. Ghi chú lại URL và thông tin chính từ mỗi nguồn để dùng cho phần Tham khảo.

### Bước 3: Viết bài
1. **Đọc template** từ `templates/post_template.md` để nắm format chuẩn.
2. **Đọc bài viết mẫu** từ `docs/blog/posts/` (file mới nhất) để nắm phong cách viết.
3. Viết bài theo cấu trúc sau:

```markdown
---
date: YYYY-MM-DD          # Ngày hiện tại
categories:
  - <Category>            # Chọn từ danh sách cho phép
tags:
  - tag1
  - tag2
  - tag3
level: <level>            # beginner | intermediate | advanced
status: published
description: "Mô tả ngắn 1-2 câu"
authors:
  - tranvanhoan
---

# Tiêu đề bài viết

## Mở đầu
(Nêu vấn đề, thu hút người đọc)

**Nội dung chính:**
- Điểm 1
- Điểm 2
- ...

---

## 1. Phần nội dung 1
(Kiến thức chính, ví dụ thực tế)

## 2. Phần nội dung 2
(Tiếp tục...)

## N. Phần cuối
(...)

---

## Kết luận
(Tóm tắt, ý nghĩa, bài học rút ra)

## Tham khảo
- [Tên nguồn](URL) — mô tả ngắn
- ...
```

#### Quy tắc viết bài:
- **Ngôn ngữ**: Tiếng Việt, tone chuyên nghiệp nhưng dễ hiểu, hấp dẫn.
- **Độ dài**: 800–2000 từ (tùy mức độ phức tạp của chủ đề).
- **Thuật ngữ kỹ thuật**: Giữ nguyên tiếng Anh các thuật ngữ phổ biến (Transformer, Token, Fine-tuning, Embedding...), kèm giải thích tiếng Việt khi cần.
- **Ví dụ thực tế**: Mỗi phần chính phải có ít nhất 1 ví dụ cụ thể minh hoạ.
- **Hình minh hoạ**: Sử dụng sơ đồ Mermaid khi cần minh hoạ flow/architecture. Code blocks khi minh hoạ code.
- **Admonitions**: Sử dụng MkDocs admonitions (`!!! tip`, `!!! warning`, `!!! info`, `!!! example`) để highlight thông tin quan trọng.

### Bước 4: Kiểm chứng nội dung (QUAN TRỌNG)
Trước khi lưu bài, **bắt buộc** kiểm tra:

#### 4.1 Kiểm tra sự thật (Fact-check)
- [ ] Mọi con số, thống kê, ngày tháng đều có nguồn dẫn chứng.
- [ ] Tên công ty, sản phẩm, công nghệ được viết đúng.
- [ ] Không có thông tin bịa đặt hoặc suy đoán không có cơ sở.
- [ ] Phân biệt rõ "sự thật đã được chứng minh" vs "ý kiến/dự đoán".

#### 4.2 Kiểm tra đạo đức & trung lập
- [ ] Không phân biệt chủng tộc, giới tính, tôn giáo, quốc tịch.
- [ ] Không tâng bốc hoặc hạ thấp bất kỳ cá nhân/tổ chức nào một cách thiếu cơ sở.
- [ ] Trình bày cân bằng ưu điểm VÀ hạn chế của công nghệ.
- [ ] Không quảng cáo ẩn cho bất kỳ sản phẩm/dịch vụ nào.

#### 4.3 Kiểm tra kỹ thuật
- [ ] Code examples (nếu có) chạy đúng logic, không có lỗi syntax rõ ràng.
- [ ] Giải thích kỹ thuật chính xác, không oversimplify đến mức sai.
- [ ] Sơ đồ Mermaid render đúng syntax.

#### 4.4 Kiểm tra format
- [ ] Frontmatter đầy đủ và đúng format (date, categories, tags, level, status, description, authors).
- [ ] Category nằm trong danh sách cho phép.
- [ ] Có phần Tham khảo với ít nhất 2 nguồn tin cậy.
- [ ] Tên file đúng format: `YYYY-MM-DD-ten-bai-viet.md` (dùng ngày hiện tại).

### Bước 5: Lưu bài viết
1. Tạo tên file theo format: `YYYY-MM-DD-ten-bai-viet.md`
   - Dùng ngày hiện tại.
   - Tên bài viết viết thường, dùng dấu gạch ngang, không dấu tiếng Việt.
   - Ví dụ: `2026-05-05-transformer-architecture.md`
2. Lưu file vào: `docs/blog/posts/YYYY-MM-DD-ten-bai-viet.md`
3. Thông báo cho user:
   - Đường dẫn file đã tạo.
   - Tóm tắt nội dung bài.
   - Danh sách nguồn tham khảo đã sử dụng.
   - Nhắc user đọc và kiểm tra bài viết trước khi publish.

### Bước 6: Chờ user review
- Thông báo: **"Bài viết đã được tạo. Vui lòng đọc và kiểm tra trước khi publish."**
- Nếu user yêu cầu sửa, thực hiện chỉnh sửa theo feedback.
- **KHÔNG tự động push lên GitHub** — việc này thuộc skill `publish_post`.

## Ví dụ sử dụng

**User**: Viết bài về Transformer Architecture
**Skill sẽ**:
1. Xác định: Category=LLM, Level=intermediate, Tags=[transformer, attention, deep-learning]
2. Search web: "Transformer architecture explained", "Attention Is All You Need paper", "Transformer 2024 advances"
3. Đọc 3-5 nguồn chi tiết
4. Viết bài ~1500 từ theo template chuẩn
5. Fact-check toàn bộ nội dung
6. Lưu: `docs/blog/posts/2026-05-05-transformer-architecture.md`
7. Thông báo user kiểm tra

## Lưu ý quan trọng
- **LUÔN search web** để đảm bảo thông tin cập nhật. KHÔNG viết bài chỉ dựa trên training data.
- **LUÔN có phần Tham khảo** với URL thật, có thể verify.
- **KHÔNG bao giờ bịa URL** tham khảo. Nếu không tìm được URL cụ thể, ghi tên nguồn mà không kèm URL.
- Ưu tiên **chất lượng hơn số lượng** — mỗi bài phải thực sự có giá trị.
