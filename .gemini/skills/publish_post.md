# Skill: Publish bài viết lên GitHub & Deploy Website

## Mô tả
Skill này thực hiện quy trình publish bài viết đã được user review xong lên GitHub, 
kích hoạt GitHub Actions tự động build, và cập nhật toàn bộ website bao gồm:
- Bài viết mới
- Trang chủ (index.md) — tự động cập nhật 15 bài mới nhất
- Roadmap — tự động cập nhật ma trận kiến thức

## Khi nào kích hoạt
- Khi user yêu cầu "publish", "push", "deploy", "đăng bài", "xuất bản", "push lên github", 
  hoặc xác nhận đã review xong bài viết và muốn đưa lên website.
- **Chỉ kích hoạt SAU KHI user đã review bài viết** bằng mắt.

## Điều kiện tiên quyết
- Đã có bài viết mới trong `docs/blog/posts/` (đã tạo bởi skill `write_blog_post`).
- User đã xác nhận OK hoặc đã chỉnh sửa xong.
- Repo đã được init Git và có remote `origin` trỏ đến GitHub.

## Kiến trúc auto-generate

Các trang sau được **tự động generate tại build time** bởi `mkdocs-gen-files` plugin:

| Trang | Script | Mô tả |
|-------|--------|--------|
| `index.md` | `scripts/generate_index.py` | Giới thiệu + 15 bài viết mới nhất |
| `roadmap.md` | `scripts/generate_roadmap.py` | Ma trận kiến thức + timeline |

→ **KHÔNG cần cập nhật index.md hay roadmap.md thủ công.** Chỉ cần push bài viết mới, GitHub Actions sẽ chạy `mkdocs build` và tất cả tự cập nhật.

## Quy trình thực hiện

### Bước 1: Kiểm tra trạng thái
1. Chạy `git status` trong thư mục `MyWiki` để xem các file thay đổi.
2. Xác nhận có file `.md` mới trong `docs/blog/posts/`.
3. Nếu không có file mới, thông báo user và dừng lại.

```bash
# Kiểm tra trạng thái
git status --short
```

### Bước 2: Kiểm tra nhanh bài viết (Pre-flight check)
Trước khi push, kiểm tra nhanh bài viết mới:

1. **Đọc file bài viết** mới trong `docs/blog/posts/`.
2. Kiểm tra frontmatter:
   - [ ] `date` đúng format `YYYY-MM-DD`
   - [ ] `categories` nằm trong danh sách cho phép: 
     `LLM`, `Prompt Engineering`, `RAG`, `Agent`, `MLOps`, `Computer Vision`, `NLP`, `Kỹ năng AI`, `AI Cơ bản`, `Case Study`
   - [ ] `level` là `beginner`, `intermediate`, hoặc `advanced`
   - [ ] `status` là `published`
   - [ ] Có `authors: [tranvanhoan]`
   - [ ] Có `description`
3. Kiểm tra nội dung:
   - [ ] Có phần `## Tham khảo` hoặc tương đương
   - [ ] Không có placeholder text (`TODO`, `XXX`, `lorem ipsum`, `[Điền vào]`)
4. Nếu phát hiện lỗi, thông báo user và **dừng lại**, không push.

### Bước 3: Stage và Commit
1. Stage tất cả file thay đổi:

```bash
git add docs/blog/posts/        # Bài viết mới
git add docs/assets/             # Hình ảnh mới (nếu có)
git add docs/index.md            # Trang chủ (nếu có thay đổi)
git add scripts/                 # Scripts generate (nếu có thay đổi)
git add mkdocs.yml               # Config (nếu có thay đổi)
git add .gemini/                 # Skills (nếu có thay đổi)
```

2. Tạo commit message theo format chuẩn:

```bash
git commit -m "📝 Bài mới: <Tiêu đề bài viết>

- Category: <category>
- Level: <level>
- Tags: <tag1, tag2, tag3>"
```

**Quy tắc commit message:**
- Emoji prefix: `📝` cho bài mới, `✏️` cho chỉnh sửa bài cũ
- Dòng đầu: tóm tắt ngắn gọn
- Body: metadata chính của bài

### Bước 4: Push lên GitHub
```bash
git push origin main
```

- Nếu push thất bại do conflict, thông báo user và hướng dẫn giải quyết.
- Nếu push thất bại do authentication, hướng dẫn user cấu hình credentials.

### Bước 5: Xác nhận GitHub Actions đã trigger
1. Thông báo user rằng push đã thành công.
2. Giải thích rằng GitHub Actions workflow `deploy.yml` sẽ tự động:
   - Checkout code mới
   - Cài Python dependencies
   - Chạy `mkdocs build` — bao gồm:
     - ✅ Generate `index.md` (15 bài mới nhất) qua `generate_index.py`
     - ✅ Generate `roadmap.md` (ma trận kiến thức) qua `generate_roadmap.py`
   - Deploy lên GitHub Pages
3. Cung cấp link để user theo dõi:
   - **GitHub Actions**: `https://github.com/hoantran-lab/mywiki/actions`
   - **Website**: `https://hoantran-lab.github.io/mywiki/`

### Bước 6: Tóm tắt kết quả
Hiển thị tóm tắt sau khi hoàn tất:

```
✅ PUBLISH THÀNH CÔNG

📄 Bài viết: <Tiêu đề>
📁 File: docs/blog/posts/<filename>.md
🏷️ Category: <category> | Level: <level>
🔖 Tags: <tags>

🔄 GitHub Actions đang build...
   → Theo dõi: https://github.com/hoantran-lab/mywiki/actions

🌐 Website sẽ tự cập nhật sau 2-3 phút:
   → https://hoantran-lab.github.io/mywiki/

🏠 Trang chủ sẽ tự cập nhật (15 bài mới nhất)
📊 Roadmap sẽ tự cập nhật (ma trận kiến thức)
```

## Xử lý nhiều bài viết cùng lúc
Nếu có nhiều bài viết mới cần publish:
1. Stage tất cả bài viết cùng lúc.
2. Tạo 1 commit duy nhất với message liệt kê tất cả bài mới.
3. Push 1 lần.

```bash
git add docs/blog/posts/
git commit -m "📝 Thêm N bài viết mới

- Bài 1: <tiêu đề>
- Bài 2: <tiêu đề>
- ..."
git push origin main
```

## Xử lý chỉnh sửa bài đã publish
Nếu user muốn chỉnh sửa bài đã publish trước đó:
1. Sửa file trong `docs/blog/posts/`.
2. Commit với prefix `✏️`:
   ```bash
   git commit -m "✏️ Cập nhật: <Tiêu đề bài viết>"
   ```
3. Push và deploy như bình thường.

## Lưu ý quan trọng
- **KHÔNG bao giờ force push** (`git push --force`). Luôn dùng push bình thường.
- **KHÔNG push nếu chưa có xác nhận** từ user rằng đã review bài viết.
- **Kiểm tra kỹ trước khi push** — một khi đã push lên main, website sẽ tự động cập nhật.
- Nếu user muốn thử local trước, hướng dẫn chạy `mkdocs serve` trong thư mục MyWiki.
- **index.md và roadmap.md được auto-generate** — không cần sửa thủ công. Nếu muốn thay đổi layout, sửa scripts trong `scripts/`.

## Troubleshooting

### Lỗi Git authentication
```
Hướng dẫn user:
1. Kiểm tra SSH key: ssh -T git@github.com
2. Hoặc dùng HTTPS + Personal Access Token
3. Hoặc dùng GitHub CLI: gh auth login
```

### Lỗi GitHub Actions build
```
1. Kiểm tra Actions log: https://github.com/hoantran-lab/mywiki/actions
2. Lỗi phổ biến:
   - Category không nằm trong danh sách cho phép → sửa frontmatter
   - Thiếu dependency → kiểm tra requirements.txt
   - Syntax error trong Mermaid → kiểm tra lại sơ đồ
   - generate_index.py hoặc generate_roadmap.py lỗi → kiểm tra script
```

### Muốn preview local trước khi push
```bash
cd /Users/tranvanhoan/Documents/Projects/Learning/MyWiki
source .venv/bin/activate  # Nếu dùng virtualenv
mkdocs serve
# Mở http://localhost:8000 để preview
```
