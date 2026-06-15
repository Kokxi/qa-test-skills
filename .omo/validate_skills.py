#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate all 41 generated SKILL.md files for completeness and quality."""

import json, os, re, sys

SKILLS_DIR = r'E:\opentest\skills'
METADATA_PATH = r'E:\opentest\.omo\skills-recovery-metadata.json'

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

expected = {}
for cname, cdata in metadata['clusters'].items():
    for sname, sdata in cdata['skills'].items():
        expected[sname] = {'cluster': cname, 'data': sdata}

errors = []
warnings = []
stats = {'ok': 0, 'missing': 0, 'total': 0}

for sname in sorted(expected.keys()):
    d = os.path.join(SKILLS_DIR, sname)
    if not os.path.isdir(d):
        errors.append(f'MISSING_DIR {sname}')
        stats['missing'] += 1
        continue
    md = os.path.join(d, 'SKILL.md')
    if not os.path.isfile(md):
        errors.append(f'MISSING_SKILL_MD {sname}')
        stats['missing'] += 1
        continue

    stats['total'] += 1
    with open(md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Frontmatter boundaries
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        errors.append(f'NO_FRONTMATTER {sname}')
        continue

    fm_raw = fm_match.group(1)

    # Parse frontmatter fields
    fm_fields = {}
    for line in fm_raw.split('\n'):
        m = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip().strip('"')
            fm_fields[key] = val

    expected_name = expected[sname]['data']['name']
    if fm_fields.get('name') != expected_name:
        errors.append(f'NAME_MISMATCH {sname}: got "{fm_fields.get("name")}" expected "{expected_name}"')

    desc = fm_fields.get('description', '')
    if not desc:
        errors.append(f'EMPTY_DESCRIPTION {sname}')

    if 'when_to_use' not in fm_fields:
        errors.append(f'MISSING_WHEN_TO_USE {sname}')

    # Check metadata block
    if 'metadata:' not in fm_raw:
        errors.append(f'MISSING_METADATA {sname}')

    # Section completeness
    has_slop = '> **"' in content
    has_guide = '## 使用指南' in content
    has_must = '### \u2705 推荐做法' in content
    has_must_not = '### \u274c 避免做法' in content
    has_prompt = '## 模板 Prompt' in content
    has_checklist = '## 验收 Checklist' in content

    missing_sections = []
    if not has_slop: missing_sections.append('slop_quote')
    if not has_guide: missing_sections.append('使用指南')
    if not has_must: missing_sections.append('推荐做法')
    if not has_must_not: missing_sections.append('避免做法')
    if not has_prompt: missing_sections.append('模板Prompt')
    if not has_checklist: missing_sections.append('验收Checklist')

    if missing_sections:
        errors.append(f'MISSING_SECTIONS {sname}: {missing_sections}')

    # Check slop quote content from metadata
    sq = expected[sname]['data'].get('slotQuote', '')
    rb = expected[sname]['data'].get('rebuttal', '')
    if not sq.strip():
        warnings.append(f'EMPTY_SLOTQUOTE {sname}')
    if not rb.strip():
        warnings.append(f'EMPTY_REBUTTAL {sname}')

    # Check must/must-not have items
    must_match = re.search(r'### \u2705 推荐做法\n\n(.*?)(?=\n### \u274c)', content, re.DOTALL)
    if must_match:
        must_items = [l for l in must_match.group(1).strip().split('\n') if re.match(r'^\d+\.', l)]
        if len(must_items) < 2:
            warnings.append(f'FEW_MUST_ITEMS {sname}: {len(must_items)}')
    else:
        errors.append(f'MISSING_MUST_SECTION {sname}')

    must_not_match = re.search(r'### \u274c 避免做法\n\n(.*?)(?=\n## )', content, re.DOTALL)
    if must_not_match:
        must_not_items = [l for l in must_not_match.group(1).strip().split('\n') if re.match(r'^\d+\.', l)]
        if len(must_not_items) < 2:
            warnings.append(f'FEW_MUSTNOT_ITEMS {sname}: {len(must_not_items)}')
    else:
        errors.append(f'MISSING_MUSTNOT_SECTION {sname}')

    # Check garbled content
    if '\ufffd' in content:
        errors.append(f'GARBLED_CHARS {sname}')

    # Check prompt template has role/task/input sections
    if '## 角色' not in content:
        warnings.append(f'MISSING_PROMPT_ROLE {sname}')
    if '## 任务' not in content:
        warnings.append(f'MISSING_PROMPT_TASK {sname}')
    if '## 输入' not in content:
        warnings.append(f'MISSING_PROMPT_INPUT {sname}')

    stats['ok'] += 1

# Summary
print(f'=== VALIDATION SUMMARY ===')
print(f'Total expected skills: {len(expected)}')
print(f'Files checked: {stats["total"]}')
print(f'Errors: {len(errors)}')
print(f'Warnings: {len(warnings)}')
print()

if errors:
    print('--- ERRORS (must fix) ---')
    for e in errors:
        print(f'  {e}')
if warnings:
    print('')
    print('--- WARNINGS (should fix) ---')
    for w in warnings:
        print(f'  {w}')

print()
print(f'Verdict: {"PASS" if not errors else "FAIL ({}/{} errors)".format(len(errors), stats["total"])}')
sys.exit(1 if errors else 0)
