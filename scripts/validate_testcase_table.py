#!/usr/bin/env python3
"""测试用例表校验器（9 列标准格式）

技能集里多个技能（qa-test-case-design / qa-api-testing / qa-boundary-deep-dive …）
都要输出同一套 9 列用例表，靠散文约束必然会漏。本脚本把确定性的规则固化成可执行校验，
让技能在交付前自检，而不是靠人眼扫。

用法
----
  python scripts/validate_testcase_table.py test-output/测试用例.md
  python scripts/validate_testcase_table.py <文件> --no-quota   # 跳过 P0-P3 占比（小规模集）
  python scripts/validate_testcase_table.py <文件> --json

校验项
------
 1. 存在 9 列表头，且列名与标准一致
 2. 每行列数一致（Markdown 竖线不被单元格内容里的竖线打断）
 3. 用例编号唯一，且符合 TC_{模块缩写}_{功能缩写}_{序号}
 4. 用例级别取值合法（P0/P1/P2/P3）
 5. 风险等级取值合法（高/中/低）
 6. P0≤20% / P1≤40% / P2≤30% / P3≤10%（--no-quota 可跳过）
 7. 覆盖率表述必须标注口径，禁止「全覆盖 / 100%」绝对化措辞
 8. 覆盖率声明必须指明依据（如「基于现有需求文档」）
 9. 若表内出现未覆盖声明，必须同时给出原因

退出码：0 全部通过 / 1 有 ERROR / 2 用法或读取错误
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

COLUMNS = ['用例编号', '测试类型', '功能模块', '测试标题', '用例级别',
           '预置条件', '测试步骤', '预期结果', '风险等级']
LEVELS = {'P0': 0.20, 'P1': 0.40, 'P2': 0.30, 'P3': 0.10}
RISKS = {'高', '中', '低'}
ID_RE = re.compile(r'^TC_[A-Z0-9]+_[A-Z0-9]+_\d{3,}$')
# 覆盖率禁词：绝对化表述
BANNED_COVERAGE = ['全覆盖', '100%覆盖', '100% 覆盖', '完全覆盖', '全部覆盖',
                   '毫无遗漏', '零缺陷', '零遗漏']
# 口径标记：出现任一即认为已标注依据
BASIS_MARKERS = ['基于', '口径', '依据', '以现有', '现有需求', '现有接口']


SEPARATOR_RE = re.compile(r'^:?-{2,}:?$')


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip('|').split('|')]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(SEPARATOR_RE.match(c) for c in cells)


def is_header(cells: list[str]) -> bool:
    return cells == COLUMNS or (cells and cells[0] == COLUMNS[0] and len(cells) == 9)


def find_tables(lines: list[str]) -> list[tuple[int, list[tuple[int, list[str]]]]]:
    """扫描全部 9 列用例表，返回 [(表头行号, [(行号, 单元格), ...])]。

    分隔行（|---|---|）在任意位置都跳过；遇到新的表头或非表格行则结束当前表。
    """
    tables: list[tuple[int, list[tuple[int, list[str]]]]] = []
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith('|'):
            i += 1
            continue
        cells = split_row(lines[i])
        if not is_header(cells):
            i += 1
            continue
        header_at = i
        rows: list[tuple[int, list[str]]] = []
        j = i + 1
        while j < len(lines) and lines[j].lstrip().startswith('|'):
            c = split_row(lines[j])
            if is_separator(c):
                j += 1
                continue
            if is_header(c):        # 下一张表，交给外层循环处理
                break
            rows.append((j + 1, c))
            j += 1
        if rows:
            tables.append((header_at, rows))
        i = j
    return tables


def validate(path: Path, check_quota: bool) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warns: list[str] = []
    stats: dict = {}
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()

    tables = find_tables(lines)
    if not tables:
        return [f'{path.name}: 未找到 9 列标准用例表（表头需为 {" | ".join(COLUMNS)}）'], warns, stats
    rows: list[tuple[int, list[str]]] = [r for _, rs in tables for r in rs]

    seen: dict[str, int] = {}
    level_count: dict[str, int] = {}
    for lineno, c in rows:
        if len(c) != 9:
            errors.append(f'第 {lineno} 行: {len(c)} 列，应为 9 列 — {lines[lineno - 1][:70]}')
            continue
        cid = c[0]
        if cid in seen:
            errors.append(f'第 {lineno} 行: 用例编号重复 {cid}（首次出现在第 {seen[cid]} 行）')
        else:
            seen[cid] = lineno
        if not ID_RE.match(cid):
            warns.append(f'第 {lineno} 行: 用例编号 {cid} 不符合 TC_{{模块}}_{{功能}}_{{序号}} 格式')
        lv = c[4]
        if lv not in LEVELS:
            errors.append(f'第 {lineno} 行: 用例级别 "{lv}" 非法，应为 P0/P1/P2/P3')
        else:
            level_count[lv] = level_count.get(lv, 0) + 1
        if c[8] not in RISKS:
            errors.append(f'第 {lineno} 行: 风险等级 "{c[8]}" 非法，应为 高/中/低')
        if not c[5]:
            errors.append(f'第 {lineno} 行: 预置条件为空')
        if not c[7]:
            errors.append(f'第 {lineno} 行: 预期结果为空')

    total = len(rows)
    stats['total'] = total
    stats['levels'] = level_count
    stats['tables'] = len(tables)

    if check_quota:
        for lv, cap in LEVELS.items():
            n = level_count.get(lv, 0)
            if n / total > cap + 1e-9:
                errors.append(
                    f'{lv} 占比 {n / total:.0%} 超过上限 {cap:.0%}'
                    f'（{n}/{total}）— 小规模用例集可用 --no-quota 并在报告中说明口径')
        stats['quota_ok'] = True

    # 覆盖率措辞与口径
    body = '\n'.join(lines)
    for word in BANNED_COVERAGE:
        if word in body:
            errors.append(f'覆盖率表述含绝对化措辞「{word}」— '
                          f'应改为「基于现有需求文档的覆盖率 X%」这类带口径的表述')
    if '覆盖率' in body:
        if not any(m in body for m in BASIS_MARKERS):
            errors.append('出现「覆盖率」但未标注统计口径（如「基于现有需求文档」）')
    if '未覆盖' in body and not re.search(r'未覆盖[^\n]{0,40}(原因|因为|由于|暂无|无)', body):
        errors.append('声明了「未覆盖」但未给出原因')
    stats['has_coverage_statement'] = '覆盖率' in body
    return errors, warns, stats


def main() -> int:
    ap = argparse.ArgumentParser(description='校验 9 列标准格式测试用例表')
    ap.add_argument('files', nargs='+', help='待校验的 Markdown / CSV 文件')
    ap.add_argument('--no-quota', action='store_true', help='跳过 P0-P3 占比校验（小规模集）')
    ap.add_argument('--json', action='store_true', help='以 JSON 输出')
    args = ap.parse_args()

    results, total_err = [], 0
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f'❌ {f}: 文件不存在')
            total_err += 1
            continue
        errors, warns, stats = validate(p, check_quota=not args.no_quota)
        total_err += len(errors)
        results.append({'file': str(f), 'errors': errors, 'warnings': warns, 'stats': stats})

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 1 if total_err else 0

    for r in results:
        head = '❌' if r['errors'] else '✅'
        st = r['stats']
        print(f"{head} {r['file']}  用例 {st.get('total', 0)} 条"
              f"{'  级别分布 ' + json.dumps(st.get('levels', {}), ensure_ascii=False) if st.get('levels') else ''}")
        for e in r['errors']:
            print(f'   ERROR   {e}')
        for w in r['warnings']:
            print(f'   warning {w}')
    print(f"\n{'=' * 46}\n合计: {total_err} 个 ERROR")
    return 1 if total_err else 0


if __name__ == '__main__':
    sys.exit(main())
