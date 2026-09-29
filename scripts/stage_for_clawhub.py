#!/usr/bin/env python3
"""ClawHub 发布暂存：复制技能目录并剥掉 metadata.slug。

为什么需要
----------
`metadata.slug` 是 SkillHub 独有的字段（SkillHub 用它做技能唯一标识）。
ClawHub 用目录名识别技能，不需要这个字段。但本仓库只维护一份代码
（dev-zh 分支带 slug），所以发 ClawHub 时必须先剥掉，否则 ClawHub 侧
会收到一个它不认识的元数据键。

为什么不写在 .bat 里
-------------------
批处理做 YAML 文本处理极易出错（缩进、转义、只改 frontmatter 不动正文），
而这类错误在发布后才暴露。放在 Python 里可以：
  1. 只在 frontmatter 区间内操作，正文里的同名字段不受影响
  2. 只删 `metadata:` 下缩进的那一行，不动其他键的缩进
  3. 被 gate_selftest.py 覆盖（有 INJECT/LEGAL 用例）

用法
----
  python scripts/stage_for_clawhub.py <技能名> [--out <目录>] [--keep]
  python scripts/stage_for_clawhub.py --all [--out <目录>]     # 49 个全量

输出：把暂存目录绝对路径打到 stdout，批处理用 FOR /F 捕获。
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / 'skills'
DEFAULT_OUT = ROOT / '.publish-staging' / 'clawhub'

# metadata.slug 在 frontmatter 里形如：  slug: "qa-api-testing"
# 整行连换行一起吃掉——只把行内容替换成空串会在 metadata: 和下一个键之间留下空行
SLUG_LINE = re.compile(r'^[ \t]+slug[ \t]*:.*\r?\n?', re.M)


def strip_slug(text: str) -> tuple[str, bool]:
    """从 frontmatter 里删掉 slug 行。返回 (新文本, 是否删到了)。

    只在前两个 --- 之间操作。删掉 metadata 下的一行不会破坏
    「metadata 是 string->string 映射」这个约束——少一个键而已。
    """
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    if not m:
        return text, False
    head, body = m.group(1), m.group(2)
    # 只删缩进的那一行：顶层 slug 才是要删的；正文里的 slug 不受影响
    new_head, n = SLUG_LINE.subn('', head)
    if n == 0:
        return text, False
    new_head = re.sub(r'\n{3,}', '\n\n', new_head).rstrip('\n')
    return f'---\n{new_head}\n---\n{body}', True


def stage(name: str, out_root: Path, keep: bool = False) -> Path:
    src = SKILLS / name
    if not (src / 'SKILL.md').exists():
        raise SystemExit(f'❌ 找不到技能目录：{src}')

    dst = out_root / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    skill_md = dst / 'SKILL.md'
    text = skill_md.read_text(encoding='utf-8', newline='')
    new_text, removed = strip_slug(text)
    if removed:
        skill_md.write_text(new_text, encoding='utf-8', newline='')
    elif '--quiet' not in sys.argv:
        print(f'  note: {name} 本来就没有 metadata.slug（可能已剥离过）',
              file=sys.stderr)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('skill', nargs='?', help='技能名；省略时需配合 --all')
    ap.add_argument('--all', action='store_true', help='暂存全部技能')
    ap.add_argument('--out', default=str(DEFAULT_OUT), help='暂存根目录')
    ap.add_argument('--keep', action='store_true', help='保留暂存目录（默认也保留）')
    ap.add_argument('--list', action='store_true', help='只打印技能名，不暂存')
    a = ap.parse_args()

    if a.list:
        for d in sorted(SKILLS.iterdir()):
            if (d / 'SKILL.md').exists():
                print(d.name)
        return 0

    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)

    if a.all or not a.skill:
        names = [d.name for d in sorted(SKILLS.iterdir()) if (d / 'SKILL.md').exists()]
    else:
        names = [a.skill]

    for n in names:
        dst = stage(n, out_root)
        # 自检：暂存副本里不该再有 slug
        txt = (dst / 'SKILL.md').read_text(encoding='utf-8')
        head = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
        if head and SLUG_LINE.search(head.group(1)):
            print(f'❌ {n}: 暂存副本仍含 slug', file=sys.stderr)
            return 1
        if a.skill and not a.all:
            print(dst)          # 单个模式：stdout 只输出路径，供批处理捕获
    return 0


if __name__ == '__main__':
    sys.exit(main())
