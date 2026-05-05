# AI Wiki

Đây là repository lưu trữ kiến thức về Trí tuệ Nhân tạo (AI) của tôi, được tổ chức dưới dạng wiki và blog.

Dự án sử dụng **MkDocs Material** để xây dựng thành website tĩnh.

## 🌟 Tính năng

- **Blog Timeline**: Các bài viết tự động sắp xếp theo thứ tự thời gian.
- **Auto-generated Roadmap**: Tự động tạo ma trận kiến thức và lộ trình học tập dựa trên bài viết (Category x Level).
- **Phân loại**: Hỗ trợ Categories và Tags.
- **Search**: Hỗ trợ tìm kiếm tiếng Việt.
- **Giao diện**: Dark/Light mode, code highlight, hỗ trợ sơ đồ Mermaid.
- **Deploy**: Tự động deploy lên GitHub Pages qua GitHub Actions.

## 🚀 Cài đặt môi trường local

Yêu cầu: Python 3.10+

1. Clone repository:
   ```bash
   git clone https://github.com/tranvanhoan/MyWiki.git
   cd MyWiki
   ```

2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Chạy server local:
   ```bash
   mkdocs serve
   ```
   Truy cập `http://localhost:8000` để xem website.

## 📝 Quy trình viết bài mới

1. Copy file template `templates/post_template.md`.
2. Đổi tên theo định dạng `YYYY-MM-DD-ten-bai-viet.md` (không bắt buộc nhưng khuyên dùng).
3. Đặt file vào thư mục `docs/blog/posts/`.
4. Điền đầy đủ thông tin vào Frontmatter (đặc biệt là `date`, `categories`, `level`).
5. Commit và Push lên nhánh `main`. GitHub Actions sẽ tự động build và deploy.

## 🛠️ Công nghệ sử dụng

- [MkDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- Plugins: `blog`, `tags`, `search`, `mkdocs-gen-files`, `mkdocs-literate-nav`
