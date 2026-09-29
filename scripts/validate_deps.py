#!/usr/bin/env python3
"""验证全部 skill SKILL.md 的依赖引用完整性。
检查：
1. 入口工作流 related_skills.all_skills 中引用的技能是否都存在
2. upstream/downstream 引用的技能是否都存在
3. 孤立技能（没有被其他任何技能引用的技能）
4. 依赖不对称（A 声明 upstream=B，但 B 的 downstream 不含 A）

注意：相关字段位于 metadata.related-skills（Agent Skills 规范形态，JSON 字符串），
统一经 scripts/skillmeta.py 读取，兼容旧的顶层字段形态。
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / 'skills'
ENTRY_SKILL = 'qa-test-skills'  # 入口工作流

errors = []
warnings = []

all_skills = [d.name for d in skillmeta.skill_dirs()]
all_skills_set = set(all_skills)
referenced_by = defaultdict(set)

sys.stdout.reconfigure(encoding='utf-8')

print(f"=== 依赖引用验证 ===\n总技能数: {len(all_skills)}\n")

# 入口工作流的 all_skills 清单
root_refs = skillmeta.referenced_skills(ENTRY_SKILL)
for ref in root_refs:
    referenced_by[ref].add('SKILL.md (entry)')
    if ref not in all_skills_set:
        errors.append(f"入口 SKILL.md 引用了不存在的技能: {ref}")

EXTERNAL_REF = {ENTRY_SKILL}  # 入口工作流本身，不作为子技能

# 检查每个子技能的引用
for skill_name in all_skills:
    if not (SKILLS_DIR / skill_name / 'SKILL.md').exists():
        errors.append(f"缺少 SKILL.md: {skill_name}")
        continue
    for ref in skillmeta.referenced_skills(skill_name):
        if ref not in all_skills_set and ref != skill_name and ref not in EXTERNAL_REF:
            errors.append(f"{skill_name} 引用了不存在的技能: {ref}")
        referenced_by[ref].add(skill_name)

# 检查孤立技能
for skill in all_skills:
    if skill not in referenced_by:
        warnings.append(f"孤立技能（未被任何其他技能引用）: {skill}")

# 检查上游引用的技能是否有对应的下游声明
for skill_name in all_skills:
    for up in (skillmeta.related_skills(skill_name).get('upstream') or []):
        if up not in all_skills_set:
            continue
        downstreams = skillmeta.related_skills(up).get('downstream') or []
        if downstreams and skill_name not in downstreams:
            warnings.append(
                f"依赖不对称: {skill_name} 声明 upstream={up}, "
                f"但 {up} 的 downstream 中未包含 {skill_name}")

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

print("\n引用统计:")
for skill in sorted(referenced_by.keys()):
    refs = sorted(referenced_by[skill])
    print(f"  {skill}: 被 {len(refs)} 个文件引用 — {', '.join(refs[:5])}{'...' if len(refs) > 5 else ''}")

# 入口工作流的 all_skills 是否覆盖全部子技能（入口自身不计入）
root_listed = skillmeta.referenced_skills(ENTRY_SKILL)
not_listed = all_skills_set - root_listed - {ENTRY_SKILL}
if not_listed:
    print(f"\n⚠️  入口 SKILL.md 的 all_skills 中未收录: {', '.join(sorted(not_listed))}")

sys.exit(1 if errors else 0)
