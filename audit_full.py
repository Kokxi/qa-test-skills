"""Comprehensive quality audit for ClawHub/SkillHub publishing readiness"""
import os, json, re
from collections import Counter

skills_dir = r'E:\opentest\skills'
mapping_path = r'E:\opentest\redflags_mapping_v2.json'

# 1. Check old titles that didn't change (already in first-person style)
with open(mapping_path, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

unchanged = []
for entry in mapping:
    skill = entry["skill"]
    for row in entry["rows"]:
        if row["title"] == row["new_title"]:
            unchanged.append((skill, row["title"]))

print("=== UNCHANGED TITLES (already in first-person style) ===")
print(f"Total unchanged: {len(unchanged)}")
if unchanged:
    for s, t in sorted(unchanged, key=lambda x: x[0]):
        print(f"  [{s}] \"{t}\"")

# 2. Check for old titles that might still be in files (missed replacements)
print("\n=== CHECK FILES FOR LEFT-OVER OLD TITLES ===")
old_titles = set()
for entry in mapping:
    for row in entry["rows"]:
        old_titles.add(row["title"])

issues = []
for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f == 'SKILL.md':
            path = os.path.join(root, f)
            name = os.path.basename(root)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            for ot in sorted(old_titles, key=len, reverse=True):
                if ot in content:
                    issues.append(f"  [{name}] Old title still present: \"{ot}\"")
if issues:
    print("\n".join(issues))
else:
    print("  No leftover old titles found - all clean!")

# 3. Check title tone consistency
print("\n=== TITLE TONE ANALYSIS ===")
titles = []
for entry in mapping:
    for row in entry["rows"]:
        titles.append((entry["skill"], row["new_title"]))

# Count patterns
pattern_counts = Counter()
for skill, t in titles:
    # First 2 chars for pattern analysis
    prefix = t[:2]
    pattern_counts[prefix] += 1

print("Top opening patterns:")
for p, c in pattern_counts.most_common(15):
    examples = [t for s, t in titles if t[:2] == p][:2]
    print(f"  '{p}' x{c}: {examples}")

# Check for "..." usage
ellipsis = [t for s, t in titles if '...' in t or '……' in t]
if ellipsis:
    print(f"\nTitles with ellipsis ({len(ellipsis)}):")
    for t in ellipsis:
        print(f"  \"{t}\"")

# Check for specific "bad" patterns
bad_patterns = []
for skill, t in titles:
    # Titles that are questions (ending with ?)
    if t.endswith('？') or t.endswith('?'):
        bad_patterns.append((skill, t, 'question'))
    # Titles using "不" negation
    if t.startswith('不'):
        bad_patterns.append((skill, t, 'starts-with-不'))

print(f"\nTitles ending with question mark ({len([x for x in bad_patterns if x[2]=='question'])}):")
for s, t, typ in bad_patterns:
    if typ == 'question':
        print(f"  [{s}] \"{t}\"")

print(f"\nTitles starting with '不' ({len([x for x in bad_patterns if x[2]=='starts-with-不'])}):")
for s, t, typ in bad_patterns:
    if typ == 'starts-with-不':
        print(f"  [{s}] \"{t}\"")

# 4. File structure audit
print("\n=== FILE STRUCTURE AUDIT ===")
structure_issues = []
for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f == 'SKILL.md':
            path = os.path.join(root, f)
            name = os.path.basename(root)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            # Required sections
            sections = {
                'YAML frontmatter': '---' in content[:5],
                'description field': 'description:' in content[:200],
                'Overview (## 概述)': '## 概述' in content,
                'Problems solved (## 解决的问题)': '## 解决的问题' in content,
                'Core framework (## 核心框架)': '## 核心框架' in content,
                'Red Flags (## 常见翻车点)': '## 常见翻车点' in content,
            }
            
            for section, present in sections.items():
                if not present:
                    structure_issues.append(f"  [{name}] Missing: {section}")

if structure_issues:
    print("Issues found:")
    print("\n".join(structure_issues))
else:
    print("  All files have required sections!")

# 5. Line count distribution
print("\n=== FILE SIZES ===")
line_counts = []
for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f == 'SKILL.md':
            path = os.path.join(root, f)
            name = os.path.basename(root)
            with open(path, 'r', encoding='utf-8') as fh:
                lines = fh.readlines()
            line_counts.append((name, len(lines)))

line_counts.sort(key=lambda x: x[1])
print("Smallest files:")
for name, count in line_counts[:5]:
    print(f"  {name}: {count} lines")
print("Largest files:")
for name, count in line_counts[-5:]:
    print(f"  {name}: {count} lines")

# 6. Red Flags rows per file
print("\n=== RED FLAGS ROWS PER FILE ===")
rows_per_file = Counter()
for entry in mapping:
    rows_per_file[entry["skill"]] = len(entry["rows"])
for name, count in rows_per_file.most_common():
    print(f"  {name}: {count} rows")

# Check qa-task-router (should be no Red Flags)
has_qataskrouter = any(e["skill"] == "qa-task-router" for e in mapping)
print(f"  qa-task-router in mapping: {has_qataskrouter}")

# 7. First-person consistency check
print("\n=== FIRST-PERSON CHECK ===")
non_first_person = []
for skill, t in titles:
    first_person_indicators = ['我', '我们', '咱', 'AI', '让我']
    has_fp = any(ind in t for ind in first_person_indicators)
    if not has_fp:
        non_first_person.append((skill, t))

if non_first_person:
    print(f"Titles without first-person pronoun ({len(non_first_person)}):")
    for s, t in non_first_person:
        print(f"  [{s}] \"{t}\"")
else:
    print("  All titles have first-person reference")

# 8. Check README completeness for publishing
print("\n=== PUBLISHING READINESS ===")
readme_path = r'E:\opentest\README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme = f.read()
    checklist_items = [
        ('Has install guide', '安装' in readme),
        ('Has usage guide', '使用' in readme),
        ('Has skill list', '技能清单' in readme),
        ('Has file structure', '文件结构' in readme),
        ('Has FAQ', '常见问题' in readme),
    ]
    print("README.md readiness:")
    for item, ok in checklist_items:
        print(f"  {'[x]' if ok else '[ ]'} {item}")
else:
    print("  README.md NOT FOUND!")
