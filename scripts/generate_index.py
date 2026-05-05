import os
import yaml
import re
import mkdocs_gen_files

# Cấu hình
POSTS_DIR = "docs/blog/posts"
INDEX_FILE = "index.md"
MAX_RECENT_POSTS = 15

LEVEL_ICONS = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
LEVEL_NAMES = {"beginner": "Cơ bản", "intermediate": "Trung bình", "advanced": "Nâng cao"}


def extract_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


def extract_title(filepath, frontmatter):
    """Lấy title từ frontmatter hoặc heading H1 đầu tiên."""
    title = frontmatter.get('title') if frontmatter else None
    if not title:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
    if not title:
        title = os.path.basename(filepath).replace('.md', '')
    return title


def generate_index():
    posts = []

    if not os.path.isdir(POSTS_DIR):
        return

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md') or filename.startswith('.'):
            continue

        filepath = os.path.join(POSTS_DIR, filename)
        frontmatter = extract_frontmatter(filepath)

        if frontmatter and frontmatter.get('status') != 'draft':
            title = extract_title(filepath, frontmatter)
            posts.append({
                'filename': filename,
                'title': title,
                'date': frontmatter.get('date'),
                'categories': frontmatter.get('categories', []),
                'level': frontmatter.get('level', 'beginner'),
                'description': frontmatter.get('description', ''),
                'url': f"blog/posts/{filename}"
            })

    # Sắp xếp theo ngày giảm dần
    posts.sort(key=lambda x: str(x['date']), reverse=True)

    # Lấy N bài mới nhất
    recent_posts = posts[:MAX_RECENT_POSTS]

    # Ghi file index.md
    with mkdocs_gen_files.open(INDEX_FILE, "w") as f:
        # --- Phần giới thiệu ---
        f.write("# AI Wiki - My Knowledge Base\n\n")
        f.write(
            "Chào mừng đến với **AI Wiki**! Đây là không gian tôi tạo ra để "
            "lưu trữ, hệ thống hóa và chia sẻ những kiến thức về "
            "**Trí Tuệ Nhân Tạo (AI)** mà tôi đã và đang học hỏi.\n\n"
        )
        f.write(
            "Dự án này vừa là **Second Brain** cho bản thân, vừa là "
            "kho tài liệu tham khảo mở cho cộng đồng.\n\n"
        )

        # --- Quick links ---
        f.write("## 🚀 Khám phá\n\n")
        f.write("- **[📝 Blog & Bài viết](blog/index.md)**: Tất cả bài viết theo dòng thời gian.\n")
        f.write("- **[🗺️ Learning Roadmap](roadmap.md)**: Ma trận kiến thức theo chủ đề và cấp độ.\n")
        f.write("- **[🏷️ Chủ đề (Tags)](tags.md)**: Khám phá bài viết theo từ khóa.\n\n")

        # --- Bài viết mới nhất ---
        f.write("---\n\n")
        f.write(f"## 📰 Bài viết mới nhất\n\n")

        if recent_posts:
            for post in recent_posts:
                date_str = str(post['date']) if post['date'] else "N/A"
                cats = ", ".join(post['categories'])
                level_icon = LEVEL_ICONS.get(post['level'], "🟢")
                level_name = LEVEL_NAMES.get(post['level'], post['level'])
                desc = post['description']

                f.write(f"### {level_icon} [{post['title']}]({post['url']})\n\n")
                f.write(f"📅 {date_str} · 🏷️ {cats} · {level_icon} {level_name}\n\n")
                if desc:
                    f.write(f"> {desc}\n\n")
        else:
            f.write("*Chưa có bài viết nào. Hãy quay lại sau!*\n\n")

        # --- Footer ---
        f.write("---\n\n")
        f.write(
            "Hãy thoải mái duyệt qua và hy vọng bạn tìm thấy "
            "những thông tin hữu ích! 🚀\n"
        )


generate_index()
