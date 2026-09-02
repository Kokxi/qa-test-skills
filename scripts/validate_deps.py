#!/usr/bin/env python3
"""验证 all 48 skill SKILL.md 的依赖引用完整性。
检查：
1. related_skills.all_skills 中引用的技能是否都存在
2. upstream/downstream 引用的技能是否都存在
3. 孤立技能（没有被其他任何技能引用的技能）
"""
import re, sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / 'skills'
ROOT_SKILL = BASE_DIR / 'skills' / 'qa-test-skills' / 'SKILL.md'  # 入口工作流（已从根目录平级迁移到 skills/ 下）

errors = []
warnings = []

def get_skill_dirs():
    return sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir())

def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    yaml = m.group(1)
    fields = {}
    current_key = None
    for line in yaml.split('\n'):
        # Top-level key
        kv = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if kv and not line.startswith(' ') and not line.startswith('\t'):
            current_key = kv.group(1)
            fields[current_key] = kv.group(2).strip()
        # Multi-line value continuation or nested
        elif current_key and line.startswith('  '):
            if isinstance(fields.get(current_key), str) and fields[current_key] != '':
                # Could be scalar continuation
                pass
    return fields

def parse_multiline_yaml_list(content, key):
    """Extract list values from a YAML list like:
    key:
      - item1
      - item2
    Supports keys at any indentation level.
    """
    m = re.search(r'^(\s*)' + re.escape(key) + r':\s*\n(.*?)(?=^\1\S|\Z)', content, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    items = re.findall(r'^\s+[-]\s+(.+)$', block, re.MULTILINE)
    return [i.strip().strip('"').strip("'") for i in items]

def parse_structure(content, key):
    """Extract structured data from YAML like:
    key:
      subkey:
        - name: xxx
    """
    m = re.search(r'^' + re.escape(key) + r':\s*\n(.*?)(?=^\w|\Z)', content, re.MULTILINE | re.DOTALL)
    if not m:
        return {}
    return m.group(1)

def extract_related_skills(content):
    """Extract all skill names from related_skills section."""
    skills = set()
    m = re.search(r'^related_skills:\s*\n(.*?)(?=^\w|\Z)', content, re.MULTILINE | re.DOTALL)
    if not m:
        return skills
    block = m.group(1)
    # all_skills list
    all_skills = re.findall(r'^\s+-\s+([\w-]+)', block, re.MULTILINE)
    skills.update(all_skills)
    # upstream/downstream lists
    for direction in ['upstream', 'downstream']:
        dm = re.search(r'^\s+' + direction + r':\s*\n(.*?)(?=^\s+\w|\Z)', block, re.MULTILINE | re.DOTALL)
        if dm:
            up = re.findall(r'^\s+-\s+([\w-]+)', dm.group(1), re.MULTILINE)
            skills.update(up)
    return skills

all_skills = get_skill_dirs()
all_skills_set = set(all_skills)
referenced_by = defaultdict(set)

sys.stdout.reconfigure(encoding='utf-8')

print(f"=== 依赖引用验证 ===\n总技能数: {len(all_skills)}\n")

root_content = ROOT_SKILL.read_text(encoding='utf-8')
root_refs = extract_related_skills(root_content)
for ref in root_refs:
    referenced_by[ref].add('SKILL.md (root)')
    if ref not in all_skills_set:
        errors.append(f"根SKILL.md 引用了不存在的技能: {ref}")

EXTERNAL_REF = {'qa-test-skills'}  # 根SKILL.md，非skills/下子技能

# 检查每个子技能的引用
for skill_name in all_skills:
    fpath = SKILLS_DIR / skill_name / 'SKILL.md'
    if not fpath.exists():
        errors.append(f"缺少 SKILL.md: {skill_name}")
        continue
    content = fpath.read_text(encoding='utf-8')
    refs = extract_related_skills(content)
    for ref in refs:
        if ref not in all_skills_set and ref != skill_name and ref not in EXTERNAL_REF:
            errors.append(f"{skill_name} 引用了不存在的技能: {ref}")
        referenced_by[ref].add(skill_name)

# 检查孤立技能
for skill in all_skills:
    if skill not in referenced_by:
        warnings.append(f"孤立技能（未被任何其他技能引用）: {skill}")

# 检查上游引用的技能是否有对应的下游声明
for skill_name in all_skills:
    fpath = SKILLS_DIR / skill_name / 'SKILL.md'
    with fpath.open('r', encoding='utf-8') as f:
        content = f.read()
    # Extract upstream
    m = re.search(r'upstream:\s*\n(.*?)(?=^\s+\w|\Z)', content, re.MULTILINE | re.DOTALL)
    if m:
        upstreams = re.findall(r'^\s+-\s+([\w-]+)', m.group(1), re.MULTILINE)
        for up in upstreams:
            if up in all_skills_set:
                # Check if this upstream has this skill in its downstream
                up_path = SKILLS_DIR / up / 'SKILL.md'
                with up_path.open('r', encoding='utf-8') as f:
                    up_content = f.read()
                dm = re.search(r'downstream:\s*\n(.*?)(?=^\s+\w|\Z)', up_content, re.MULTILINE | re.DOTALL)
                if dm:
                    downstreams = re.findall(r'^\s+-\s+([\w-]+)', dm.group(1), re.MULTILINE)
                    if skill_name not in downstreams:
                        warnings.append(f"依赖不对称: {skill_name} 声明 upstream={up}, 但 {up} 的 downstream 中未包含 {skill_name}")

# 输出结果
if errors:
    print("❌ 错误:")
    for e in errors:
        print(f"  - {e}")
else:
    print("✅ 没有引用错误")

if warnings:
    print(f"\n⚠️  警告 ({len(warnings)}):")
    for w in warnings:
        print(f"  - {w}")
else:
    print("✅ 没有警告")

print(f"\n引用统计:")
for skill in sorted(referenced_by.keys()):
    refs = sorted(referenced_by[skill])
    if len(refs) > 0:
        print(f"  {skill}: 被 {len(refs)} 个文件引用 — {', '.join(refs[:5])}{'...' if len(refs) > 5 else ''}")

# 找到未被根SKILL.md all_skills 列出的技能
root_listed = extract_related_skills(root_content)
not_listed = all_skills_set - root_listed
if not_listed:
    warnings.append(f"根SKILL.md的 all_skills 中未收录: {', '.join(sorted(not_listed))}")
    print(f"\n⚠️  根SKILL.md 未收录以下技能:")
    for s in sorted(not_listed):
        print(f"  - {s}")
