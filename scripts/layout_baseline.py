#!/usr/bin/env python3
"""生成/更新内容层基线（棘轮）。

背景
----
第 0 批给内容层拆分加了 3 项检查（加载时机地图 / assets / ID 不含中文），
但存量 47 个技能全部不合规 —— 门禁若直接判红，改造过程就没法用 CI 卡住。

本文件记录"当前已知存量"。检查只对**超出基线的新增违规**失败；
每完成一批改造，从基线里移除对应技能，基线单调收缩。

用法
----
  python scripts/layout_baseline.py --generate     # 按当前状态重建基线（会丢人工调优，慎用）
  python scripts/layout_baseline.py --prune 已修    # 把当前已无违规的技能移出基线
  python scripts/layout_baseline.py --show          # 查看基线与现状差异
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

BASELINE = Path(__file__).resolve().parent / 'layout_baseline.json'

CHECKS = ('no-load-map', 'no-assets', 'id-has-cjk', 'no-checklist')
LABELS = {
    'no-load-map': '缺加载时机地图',
    'no-assets': '缺 assets 产出模板',
    'id-has-cjk': '用例编号含中文',
    'no-checklist': '缺检查清单',
}
# 不参与内容层改造的技能（入口编排器 / 已完成样板）
EXEMPT = {'qa-test-skills'}
DONE = {'qa-api-testing', 'qa-agent-testing'}

CJK_ID = re.compile(r'\b[A-Z]{2,6}-[一-鿿]+-?\d*')
LOADMAP = re.compile(r'^##\s*(?:\d+\.\s*)?(?:加载时机|什么时候读|文件加载时机)', re.M)
CHECKLIST = re.compile(r'^##\s*(?:\d+\.\s*)?(?:交付前)?(?:检查清单|自检清单|自检)', re.M)


def scan() -> dict[str, list[str]]:
    """扫描全量技能，返回 {检查项: [违规技能名]}。"""
    out: dict[str, list[str]] = {k: [] for k in CHECKS}
    for d in skillmeta.skill_dirs():
        n = d.name
        if n in EXEMPT or n in DONE:
            continue
        body = skillmeta.load(n)['body']
        refs = list((d / 'references').glob('*.md')) if (d / 'references').is_dir() else []
        assets = list((d / 'assets').glob('*')) if (d / 'assets').is_dir() else []

        if not LOADMAP.search(body):
            out['no-load-map'].append(n)
        if not assets:
            out['no-assets'].append(n)
        if CJK_ID.search(body) or any(CJK_ID.search(r.read_text(encoding='utf-8')) for r in refs):
            out['id-has-cjk'].append(n)
        has_ck = CHECKLIST.search(body) or any(CHECKLIST.search(r.read_text(encoding='utf-8')) for r in refs)
        if not has_ck:
            out['no-checklist'].append(n)
    return {k: sorted(v) for k, v in out.items()}


def load() -> dict:
    if not BASELINE.exists():
        return {'_comment': '内容层存量基线（棘轮）。检查只对超出本文件的新增违规失败。',
                'checks': {k: [] for k in CHECKS}}
    return json.loads(BASELINE.read_text(encoding='utf-8'))


def save(data: dict) -> None:
    BASELINE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                        encoding='utf-8', newline='\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--generate', action='store_true', help='按当前状态重建基线')
    ap.add_argument('--prune', action='store_true', help='移除当前已无违规的技能')
    ap.add_argument('--show', action='store_true', help='显示基线与现状差异')
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding='utf-8')
    cur = scan()
    base = load().get('checks', {})

    if args.generate:
        save({'_comment': '内容层存量基线（棘轮）。检查只对超出本文件的新增违规失败；'
                          '每完成一批改造用 --prune 收缩。',
              'checks': cur})
        total = sum(len(v) for v in cur.values())
        print(f'基线已重建：{total} 项存量')
        for k in CHECKS:
            print(f'  {LABELS[k]:<18} {len(cur[k])} 个')
        return 0

    if args.prune:
        pruned = 0
        for k in CHECKS:
            before = set(base.get(k, []))
            after = sorted(before & set(cur[k]))
            removed = before - set(after)
            base[k] = after
            pruned += len(removed)
            for n in sorted(removed):
                print(f'  已修复并移出基线 [{LABELS[k]}] {n}')
        data = load()
        data['checks'] = {k: sorted(base.get(k, [])) for k in CHECKS}
        save(data)
        print(f'\n基线收缩 {pruned} 项，剩余 {sum(len(v) for v in data["checks"].values())} 项')
        return 0

    # --show（默认）
    new_total = fixed_total = 0
    print('=' * 62)
    print('内容层棘轮：基线 vs 现状')
    print('=' * 62)
    for k in CHECKS:
        b, c = set(base.get(k, [])), set(cur[k])
        new, fixed = sorted(c - b), sorted(b - c)
        new_total += len(new)
        fixed_total += len(fixed)
        mark = '✅' if not new else '❌'
        print(f'  {mark} {LABELS[k]:<18} 存量 {len(b):>2} → 现状 {len(c):>2}'
              f'（新 {len(new)} / 已修 {len(fixed)}）')
        for n in new:
            print(f'       新增违规: {n}')
        for n in fixed:
            print(f'       已修复:   {n}')
    print()
    print(f'合计：新增违规 {new_total}（应恒为 0）/ 已修复 {fixed_total}（基线应随之收缩）')
    print('=' * 62)
    return 1 if new_total else 0


if __name__ == '__main__':
    sys.exit(main())
