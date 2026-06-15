import os, re, json

skills_dir = r'E:\opentest\skills'
issues = []
files_checked = 0
file_details = []

for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f == 'SKILL.md':
            files_checked += 1
            path = os.path.join(root, f)
            name = os.path.basename(root)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()

            detail = {"name": name, "len": len(content), "issues": []}

            if not content.startswith('---'):
                detail["issues"].append("Missing YAML frontmatter")
            else:
                parts = content.split('---', 2)
                if len(parts) < 3:
                    detail["issues"].append("Incomplete YAML frontmatter")
                else:
                    fm = parts[1]
                    if not re.search(r'description:\s*\S', fm):
                        detail["issues"].append("Missing/invalid description")
                    if not re.search(r'^skill:\s*\S', fm, re.MULTILINE):
                        detail["issues"].append("Missing skill name")

            if 'Red Flags' not in content:
                detail["issues"].append("No Red Flags section")

            rows_found = len(re.findall(r'^\|\s*\*\*"', content, re.MULTILINE))
            if rows_found == 0:
                detail["issues"].append("No Red Flags rows")
            else:
                detail["red_flag_rows"] = rows_found

            detail["line_count"] = len(content.split('\n'))
            file_details.append(detail)
            if detail["issues"]:
                issues.append(detail)

print(f"Files checked: {files_checked}")
if issues:
    print(f"\nIssues found in {len(issues)} files:")
    for d in issues:
        print(f"  [{d['name']}] {', '.join(d['issues'])}")
else:
    print("No structural issues found!")

print(f"\nFiles with Red Flags rows:")
for d in file_details:
    rf = d.get('red_flag_rows', 'N/A')
    print(f"  {d['name']}: {rf} rows, {d['line_count']} lines")

# Duplicate title analysis
with open(r'E:\opentest\redflags_mapping_v2.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

from collections import Counter
all_titles = Counter()
title_skills = {}
for entry in mapping:
    skill = entry["skill"]
    for row in entry["rows"]:
        t = row["new_title"]
        all_titles[t] += 1
        if t not in title_skills:
            title_skills[t] = []
        title_skills[t].append(skill)

dupes = {t: c for t, c in all_titles.items() if c > 1}
print(f"\nDuplicate titles: {len(dupes)}")
for t, c in sorted(dupes.items(), key=lambda x: -x[1]):
    print(f"  x{c} '{t}' -> {title_skills[t]}")

# Length stats
lengths = [len(t) for t in all_titles]
print(f"\nLength stats:")
print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.1f}")
short = {t: len(t) for t in all_titles if len(t) < 8}
long = {t: len(t) for t in all_titles if len(t) > 22}
if short:
    print(f"  Very short (<8 chars, {len(short)}):")
    for t, l in sorted(short.items(), key=lambda x: x[1]):
        print(f"    [{l}] {t}")
if long:
    print(f"  Long (>22 chars, {len(long)}):")
    for t, l in sorted(long.items(), key=lambda x: -x[1]):
        print(f"    [{l}] {t}")

# Ending punctuation analysis
no_punct_count = 0
no_punct_list = []
for t in all_titles:
    has_end = t[-1] in ('。','？','！','?','!','.')
    if not has_end:
        no_punct_count += 1
        no_punct_list.append(t)
print(f"\nTitles without ending punctuation: {no_punct_count}/{len(all_titles)}")
if no_punct_list:
    print(f"  Examples: {no_punct_list[:5]}")
