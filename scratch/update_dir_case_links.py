import os, re, urllib.parse

dir_map = {
    'architecture/': 'Architecture/',
    'checkpoints/': 'Checkpoints/',
    'dataset/': 'Dataset/',
    'decisions/': 'Decisions/',
    'experiments/': 'Experiments/',
    'figures/': 'Figures/',
    'findings/': 'Findings/',
    'literature/': 'Literature/',
    'preprocessing/': 'Preprocessing/',
    'reports/': 'Reports/',
    'research/architecture/': 'research/Architecture/',
    'research/checkpoints/': 'research/Checkpoints/',
    'research/dataset/': 'research/Dataset/',
    'research/decisions/': 'research/Decisions/',
    'research/experiments/': 'research/Experiments/',
    'research/figures/': 'research/Figures/',
    'research/findings/': 'research/Findings/',
    'research/literature/': 'research/Literature/',
    'research/preprocessing/': 'research/Preprocessing/',
    'research/reports/': 'research/Reports/',
}

# Update all markdown files in research and root README
files_to_process = []
for root, dirs, files in os.walk('research'):
    if '.obsidian' in root: continue
    for f in files:
        if f.endswith('.md'):
            files_to_process.append(os.path.join(root, f))
files_to_process.append('README.md')

total_replacements = 0

for file_path in files_to_process:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Markdown links [label](url)
    def link_replacer(match):
        label = match.group(1)
        url = match.group(2)
        if url.startswith(('http:', 'https:', '#', 'mailto:')):
            return match.group(0)
        
        new_url = url
        # Check URL encoded or decoded
        for old_dir, new_dir in dir_map.items():
            # Check direct
            if new_url.startswith(old_dir):
                new_url = new_dir + new_url[len(old_dir):]
            elif ('/' + old_dir) in new_url:
                new_url = new_url.replace('/' + old_dir, '/' + new_dir)
            elif ('../' + old_dir) in new_url:
                new_url = new_url.replace('../' + old_dir, '../' + new_dir)
        return f"[{label}]({new_url})"

    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replacer, content)

    # 2. Img tags <img ... src="..." ...>
    def img_replacer(match):
        full_tag = match.group(0)
        src_match = re.search(r'src=[\"\x27]([^\"\x27]+)[\"\x27]', full_tag)
        if not src_match: return full_tag
        src = src_match.group(1)
        if src.startswith(('http:', 'https:')): return full_tag
        
        new_src = src
        for old_dir, new_dir in dir_map.items():
            if new_src.startswith(old_dir):
                new_src = new_dir + new_src[len(old_dir):]
            elif ('/' + old_dir) in new_src:
                new_src = new_src.replace('/' + old_dir, '/' + new_dir)
            elif ('../' + old_dir) in new_src:
                new_src = new_src.replace('../' + old_dir, '../' + new_dir)
        return full_tag.replace(src, new_src)

    content = re.sub(r'<img[^>]+>', img_replacer, content)

    # 3. Text mentions in code blocks or file trees
    # e.g., "├── architecture/" -> "├── Architecture/"
    tree_replacements = [
        ("├── architecture/", "├── Architecture/"),
        ("├── checkpoints/", "├── Checkpoints/"),
        ("├── dataset/", "├── Dataset/"),
        ("├── decisions/", "├── Decisions/"),
        ("├── experiments/", "├── Experiments/"),
        ("├── figures/", "├── Figures/"),
        ("├── findings/", "├── Findings/"),
        ("├── literature/", "├── Literature/"),
        ("├── preprocessing/", "├── Preprocessing/"),
        ("└── reports/", "└── Reports/"),
        ("├── reports/", "├── Reports/"),
        ("`architecture/`", "`Architecture/`"),
        ("`checkpoints/`", "`Checkpoints/`"),
        ("`dataset/`", "`Dataset/`"),
        ("`decisions/`", "`Decisions/`"),
        ("`experiments/`", "`Experiments/`"),
        ("`figures/`", "`Figures/`"),
        ("`findings/`", "`Findings/`"),
        ("`literature/`", "`Literature/`"),
        ("`preprocessing/`", "`Preprocessing/`"),
        ("`reports/`", "`Reports/`"),
        ("`research/architecture/`", "`research/Architecture/`"),
        ("`research/checkpoints/`", "`research/Checkpoints/`"),
        ("`research/dataset/`", "`research/Dataset/`"),
        ("`research/decisions/`", "`research/Decisions/`"),
        ("`research/experiments/`", "`research/Experiments/`"),
        ("`research/figures/`", "`research/Figures/`"),
        ("`research/findings/`", "`research/Findings/`"),
        ("`research/literature/`", "`research/Literature/`"),
        ("`research/preprocessing/`", "`research/Preprocessing/`"),
        ("`research/reports/`", "`research/Reports/`"),
    ]
    for old_s, new_s in tree_replacements:
        content = content.replace(old_s, new_s)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        total_replacements += 1
        print(f"Updated: {file_path}")

print(f"Total files updated: {total_replacements}")
