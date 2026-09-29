#!/usr/bin/env python3
"""Agent Skills 规范合规门禁

本仓库此前用自己的 `integrity_check.py` 验收（0 硬问题），但官方参考实现
`skills-ref validate` 对 49 个技能全部判失败 —— 根因是自定义 frontmatter 字段
不在规范白名单内，且 `categories: ['a','b']` 属于 flow-style 序列，官方 loader 拒绝。

本脚本把「规范合规」独立成一道门禁，与内容质量门禁（integrity_check.py）分开：
  - 规范层：改了会装不上/不被客户端识别 → 必须零容忍
  - 内容层：质量退化 → 可分阶段收敛

依赖官方参考实现：pip install skills-ref
未安装时退化为内置规则检查（覆盖规范中可静态判定的部分），并提示安装。

用法
----
  python scripts/check_spec_compliance.py            # 全量
  python scripts/check_spec_compliance.py --no-ref    # 跳过官方 validator，只跑内置规则
  python scripts/check_spec_compliance.py --strict    # 内置 warning 也算失败
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'

# 规范（https://agentskills.io/specification）允许的顶层字段
ALLOWED_TOP = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}
MAX_DESC = 1024
MAX_LINES = 500          # 规范建议：SKILL.md 控制在 500 行内
MAX_COMPAT = 500
NAME_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
FLOW_SEQ = re.compile(r'^\s*[A-Za-z0-9_-]+:\s*\[')   # flow-style 序列，官方 loader 拒绝

errors: list[tuple[str, str]] = []
warns: list[tuple[str, str]] = []


def check_skill(d: Path) -> None:
    name = d.name
    p = d / 'SKILL.md'
    doc = skillmeta.load(name)
    fm = doc['frontmatter']
    meta = doc['metadata']
    body = doc['body']
    raw = skillmeta.read_text(p)

    # 目录名 / name 一致与格式
    if fm.get('name') != name:
        errors.append((name, f"name={fm.get('name')!r} 与目录名 {name!r} 不一致"))
    if not NAME_RE.match(str(fm.get('name', ''))):
        errors.append((name, f"name={fm.get('name')!r} 不符合规范（仅小写字母/数字/连字符，无连续连字符）"))

    # 顶层字段白名单
    extra = sorted(set(fm) - ALLOWED_TOP)
    if extra:
        errors.append((name, f'顶层出现非规范字段 {extra}（规范只允许 {sorted(ALLOWED_TOP)}）'))

    # metadata 必须是 string -> string
    if not isinstance(meta, dict):
        errors.append((name, 'metadata 不是映射'))
    else:
        for k, v in meta.items():
            if not isinstance(v, str):
                errors.append((name, f'metadata.{k} 值为 {type(v).__name__}，规范要求 string'))

    # description
    desc = str(fm.get('description', ''))
    if not desc.strip():
        errors.append((name, 'description 为空'))
    elif len(desc) > MAX_DESC:
        errors.append((name, f'description {len(desc)} 字符，超过规范上限 {MAX_DESC}'))

    # compatibility
    compat = fm.get('compatibility')
    if compat and len(str(compat)) > MAX_COMPAT:
        errors.append((name, f'compatibility {len(str(compat))} 字符，超过上限 {MAX_COMPAT}'))

    # 行数与体积（规范建议）
    n = len(raw.splitlines())
    if n > MAX_LINES:
        warns.append((name, f'SKILL.md {n} 行，超过规范建议的 {MAX_LINES} 行，建议把细节下沉到 references/'))

    # YAML flow-style 序列（官方 loader 判非法）
    fm_text = re.match(r'^---\n(.*?)\n---\n', raw, re.S)
    if fm_text and FLOW_SEQ.search(fm_text.group(1)):
        errors.append((name, 'frontmatter 含 flow-style 序列（[a, b]），官方 loader 判为非法 YAML'))

    # 文件引用必须在 skill 根内、且不从 SKILL.md 深层嵌套
    for m in re.finditer(r'\]\(([^)]+)\)', body):
        target = m.group(1).split('#')[0]
        if not target or target.startswith(('http://', 'https://', 'mailto:')):
            continue
        if target.startswith('../'):
            errors.append((name, f'正文链接越出 skill 根目录：{target}（单装该技能后失效）'))
        elif not (d / target).exists():
            errors.append((name, f'正文链接指向不存在的文件：{target}'))
    for ref in re.findall(r'references/([\w.-]+/[\w.-]+\.md)', body):
        warns.append((name, f'references 嵌套两层：references/{ref}，规范建议保持一层深'))

    # 裸 *.md 引用：正文里提到某个 .md 时若前面没有路径限定（紧邻的字符不是 '/'），
    # 而该文件不在本技能下，agent 就找不到它。入口技能的路由表曾把 qa-mobile-testing
    # 的文件写成裸名，正是这个形态。
    for m in re.finditer(r'(?<![\w/.-])([a-z][\w.-]*\.md)', body):
        rel = m.group(1)
        if (d / rel).exists() or (d / 'references' / rel).exists():
            continue
        qualified = m.start() > 0 and body[m.start() - 1] == '/'
        if qualified:
            continue
        owner = [s for s in sorted(p.name for p in SKILLS_DIR.iterdir()
                                   if (p / 'references' / rel).exists())
                 if s != name]
        if owner:
            errors.append((name, f'正文裸引用 {rel}，该文件属于 {owner[0]}/references/，'
                                 f'应写成 {owner[0]}/references/{rel}'))
        else:
            warns.append((name, f'正文引用 {rel} 在本技能与任何兄弟技能下都不存在'))

    # BOM
    if p.read_bytes().startswith(b'\xef\xbb\xbf'):
        errors.append((name, 'SKILL.md 带 UTF-8 BOM'))


def run_official() -> tuple[int, str]:
    exe = shutil.which('skills-ref')
    if not exe:
        return -1, ''
    fail, msgs = 0, []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not (d / 'SKILL.md').exists():
            continue
        r = subprocess.run([exe, 'validate', str(d)], capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        if r.returncode != 0:
            fail += 1
            for line in r.stdout.splitlines():
                if line.strip().startswith('- '):
                    msgs.append(f'{d.name}: {line.strip()[2:]}')
    return fail, '\n'.join(msgs[:20])


def run_ratchet() -> tuple[int, list[str]]:
    """内容层棘轮：只对超出 layout_baseline.json 的新增违规失败。

    存量债（缺加载时机地图 / 缺 assets / ID 含中文）已记录在基线里，
    改造期间不会把门禁打红；但任何**新引入**的这类违规会立即失败。
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import layout_baseline
    base = layout_baseline.load().get('checks', {})
    cur = layout_baseline.scan()
    msgs, n = [], 0
    for k in layout_baseline.CHECKS:
        new = sorted(set(cur[k]) - set(base.get(k, [])))
        n += len(new)
        for skill in new:
            msgs.append(f'{skill}: {layout_baseline.LABELS[k]}（不在 layout_baseline.json 存量中）')
    return n, msgs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-ref', action='store_true', help='跳过官方 skills-ref validator')
    ap.add_argument('--strict', action='store_true', help='warning 也算失败')
    args = ap.parse_args()

    for d in sorted(SKILLS_DIR.iterdir()):
        if (d / 'SKILL.md').exists():
            check_skill(d)

    print('=== Agent Skills 规范合规 ===')
    print(f'  内置规则: {"❌" if errors else "✅"} {len(errors)} 错误 / {len(warns)} 警告')
    for n, m in errors[:15]:
        print(f'    ERROR {n}: {m}')
    for n, m in warns[:15]:
        print(f'    warn  {n}: {m}')

    ref_fail, ref_msg = (0, '') if args.no_ref else run_official()
    if args.no_ref:
        print('\n  官方 skills-ref validator: 已跳过 (--no-ref)')
    elif ref_fail < 0:
        print('\n  ⚠️  未安装官方参考实现，跳过 skills-ref validate')
        print('     安装：pip install skills-ref')
    else:
        status = '✅' if ref_fail == 0 else '❌'
        print(f'\n  官方 skills-ref validator: {status} {ref_fail} 个技能不合规')
        for line in ref_msg.splitlines():
            print(f'    {line}')

    ratchet_fail, ratchet_msg = run_ratchet()
    print(f'\n  内容层棘轮: {"❌" if ratchet_fail else "✅"} '
          f'{ratchet_fail} 项新增违规（超出 layout_baseline.json 存量）')
    for m in ratchet_msg[:10]:
        print(f'    {m}')

    hard = len(errors) + max(0, ref_fail) + ratchet_fail
    print('\n' + '=' * 50)
    print(f'规范合规: {"❌" if hard else "✅"} {hard} 硬问题, {len(warns)} 警告')
    print('=' * 50)
    return 1 if (hard or (args.strict and warns)) else 0


if __name__ == '__main__':
    sys.exit(main())
