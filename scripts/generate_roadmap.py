import os
import yaml
import re
from collections import defaultdict
from pathlib import Path
import mkdocs_gen_files

# Cấu hình
POSTS_DIR = "docs/blog/posts"
ROADMAP_FILE = "roadmap.md"
CATEGORIES = [
    "LLM", "Prompt Engineering", "RAG", "Agent", "MLOps", 
    "Computer Vision", "NLP", "Kỹ năng AI", "AI Cơ bản", "Case Study"
]
LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_ICONS = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
LEVEL_NAMES = {"beginner": "Cơ bản", "intermediate": "Trung bình", "advanced": "Nâng cao"}

def extract_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm khối YAML frontmatter giữa 2 dòng ---
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None

def generate_roadmap():
    posts = []
    
    # Đọc tất cả các bài viết
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md') or filename.startswith('.'):
            continue
            
        filepath = os.path.join(POSTS_DIR, filename)
        frontmatter = extract_frontmatter(filepath)
        
        if frontmatter and frontmatter.get('status') != 'draft':
            # Lấy title từ h1 nếu không có trong frontmatter
            title = frontmatter.get('title')
            if not title:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
            if not title:
                title = filename.replace('.md', '')

            posts.append({
                'filename': filename,
                'title': title,
                'date': frontmatter.get('date'),
                'categories': frontmatter.get('categories', []),
                'level': frontmatter.get('level', 'beginner'),
                'url': f"blog/posts/{filename}"
            })
            
    # Sắp xếp bài viết theo thời gian giảm dần
    posts.sort(key=lambda x: str(x['date']), reverse=True)
    
    # Thống kê
    total_posts = len(posts)
    level_counts = {level: 0 for level in LEVELS}
    
    # Ma trận kiến thức: category -> level -> list of posts
    matrix = {cat: {lvl: [] for lvl in LEVELS} for cat in CATEGORIES}
    
    # Gom bài viết theo thời gian (YYYY-MM)
    timeline = defaultdict(list)
    
    for post in posts:
        level = post['level']
        if level in level_counts:
            level_counts[level] += 1
            
        for cat in post['categories']:
            if cat in matrix and level in LEVELS:
                matrix[cat][level].append(post)
                
        # Format date for timeline
        date_str = str(post['date'])
        if len(date_str) >= 7:
            month_year = date_str[:7] # YYYY-MM
            timeline[month_year].append(post)

    # Ghi file roadmap
    with mkdocs_gen_files.open(ROADMAP_FILE, "w") as f:
        f.write("# 🗺️ Learning Roadmap\n\n")
        f.write("Hành trình học tập và ma trận kiến thức AI được tự động tổng hợp từ các bài viết.\n\n")
        
        f.write("## 📊 Tổng quan\n")
        f.write(f"- **Tổng số bài viết**: {total_posts}\n")
        
        level_stats = []
        for lvl in LEVELS:
            icon = LEVEL_ICONS[lvl]
            name = LEVEL_NAMES[lvl].capitalize()
            count = level_counts[lvl]
            level_stats.append(f"{icon} {name}: {count}")
        f.write("- " + " | ".join(level_stats) + "\n\n")
        
        f.write("## 🧮 Ma trận kiến thức\n\n")
        f.write("| Chủ đề | Cơ bản 🟢 | Trung bình 🟡 | Nâng cao 🔴 |\n")
        f.write("|---|---|---|---|\n")
        
        for cat in CATEGORIES:
            row = [cat]
            has_any_post = False
            for lvl in LEVELS:
                posts_in_cell = matrix[cat][lvl]
                if posts_in_cell:
                    has_any_post = True
                    count = len(posts_in_cell)
                    row.append(f"✅ ({count})")
                else:
                    row.append("❌")
            
            # Chỉ in row nếu có ít nhất 1 bài viết trong category đó, hoặc có thể in hết
            # Ở đây ta in hết để thấy được bức tranh tổng thể còn thiếu gì
            f.write("| " + " | ".join(row) + " |\n")
            
        f.write("\n## 📅 Timeline bài viết\n\n")
        
        for month_year in sorted(timeline.keys(), reverse=True):
            f.write(f"### {month_year}\n")
            for post in timeline[month_year]:
                cats = ", ".join(post['categories'])
                icon = LEVEL_ICONS.get(post['level'], "🟢")
                f.write(f"- {icon} [{post['title']}]({post['url']}) - *{cats}*\n")
            f.write("\n")

generate_roadmap()
