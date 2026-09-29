#!/usr/bin/env python3
"""单技能 metadata 校验器 —— 改完 SKILL.md 立刻自查，别等全量门禁。

专治 output-format / input-format 写成非法 JSON 这类手写高频错误。
（历史：structure 数组里同一个对象字面量内塞了两个 "key":"value" 对，少逗号。）

用法
----
  python scripts/check_meta.py qa-scenario-tree qa-risk-intuition
  python scripts/check_meta.py --all
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

# 这些 metadata 值是 JSON 字符串，必须能解析
JSON_KEYS = ['input-format', 'output-format', 'error-recovery-guidance',
             'depth-requirement', 'categories', 'references', 'related-skills']
# 这些值是纯文本，不要求 JSON
TEXT_KEYS = ['version', 'slug', 'display-name', 'when-to-use']


def check(skill: str) -> list[str]:
    errs: list[str] = []
    meta = skillmeta.load(skill)['metadata']

    for k in JSON_KEYS:
        v = meta.get(k)
        if v in (None, ''):
            continue
        try:
            parsed = json.loads(v)
        except ValueError as exc:
            pos = getattr(exc, 'pos', None)
            near = f'\n      …{v[max(0, pos - 70):pos + 40]}…' if pos is not None else ''
            errs.append(f'metadata.{k} 非法 JSON：{exc}{near}')
            continue
        # structure 里每个对象元素只能有一个键（历史高频错误）
        if k == 'output-format' and isinstance(parsed, dict):
            st = parsed.get('structure')
            if isinstance(st, list):
                for i, item in enumerate(st):
                    if isinstance(item, dict) and len(item) > 1:
                        errs.append(
                            f'metadata.output-format.structure[{i}] 有 {len(item)} 个键，'
                            f'必须拆成多个数组元素：{list(item)}')
            if not parsed.get('traceability'):
                errs.append('metadata.output-format 缺 traceability')

    for k in TEXT_KEYS:
        v = meta.get(k)
        if v is not None and not isinstance(v, str):
            errs.append(f'metadata.{k} 应为 string，实为 {type(v).__name__}')

    for k, v in meta.items():
        if not isinstance(v, str):
            errs.append(f'metadata.{k} 值类型为 {type(v).__name__}，规范要求 string')
    return errs


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    if not args or args[0] == '--all':
        targets = sorted(skillmeta.skill_names())
    else:
        targets = args

    bad = 0
    for s in targets:
        if s not in skillmeta.skill_names():
            print(f'❌ {s}: 不存在的技能')
            bad += 1
            continue
        errs = check(s)
        if errs:
            bad += 1
            print(f'❌ {s}')
            for e in errs:
                print(f'    {e}')
    if not bad:
        print(f'✅ {len(targets)} 个技能的 metadata 全部合法')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
