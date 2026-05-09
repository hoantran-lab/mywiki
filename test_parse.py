import os, re, yaml
POSTS_DIR = "docs/blog/posts"
for filename in os.listdir(POSTS_DIR):
    if not filename.endswith('.md') or filename.startswith('.'): continue
    with open(os.path.join(POSTS_DIR, filename), 'r') as f: content = f.read()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    print(filename, bool(match))
