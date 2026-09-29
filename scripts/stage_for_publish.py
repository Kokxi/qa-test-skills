#!/usr/bin/env python3
"""发布暂存：按目标平台调整技能副本的 frontmatter，再交给各平台 CLI 推送。

为什么需要
----------
仓库里的 SKILL.md 是**规范形态**：顶层只允许
name / description / license / compatibility / metadata / allowed-tools，
自定义字段全部收在 metadata 下（规范要求 metadata 为 string->string）。

但两个平台的 CLI 各有各的前置要求，都与规范形态不兼容：

| 平台   | 要求                                        | 与规范形态的冲突                          |
|--------|---------------------------------------------|-------------------------------------------|
| SkillHub | 顶层读得到 `slug` / `version` / `displayName` | 键名是 `display-name`（连字符），CLI 认不出  |
| ClawHub  | 不认 `metadata.slug`                          | slug 是 SkillHub 独有字段                  |

处理方式
--------
在**暂存副本**上做调整，源文件保持规范形态不变：

- `--platform skillhub`  补一个顶层 `displayName`（值取自 metadata.display-name）
- `--platform clawhub`   删掉 `metadata.slug`

两份产物都不入库（`.publish-staging/` 已在 .gitignore）。
选暂存而不是维护双分支，是因为两个分支会随每次改动漂移。

用法
----
  python scripts/stage_for_publish.py <技能名> --platform clawhub
  python scripts/stage_for_publish.py --all --platform skillhub
  python scripts/stage_for_publish.py --list

单个模式下 stdout 只打印暂存目录的绝对路径，批处理用 FOR /F 捕获。
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / 'skills'
DEFAULT_OUT = ROOT / '.publish-staging'

FM = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.S)


def _split(text: str) -> tuple[str, str] | None:
    m = FM.match(text)
    return (m.group(1), m.group(2)) if m else None


def _meta_get(head: str, key: str) -> str | None:
    """读 metadata 下的一个标量值（只看缩进行，避免误取顶层同名键）"""
    m = re.search(rf'^[ \t]+{re.escape(key)}[ \t]*:[ \t]*(.*?)[ \t]*$', head, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        v = v[1:-1]
    return v.replace('\\"', '"')


def _meta_drop(head: str, key: str) -> tuple[str, bool]:
    """删掉 metadata 下的一个键（整行含换行，避免留下空行）"""
    pat = re.compile(rf'^[ \t]+{re.escape(key)}[ \t]*:.*\r?\n?', re.M)
    new, n = pat.subn('', head)
    return new, n > 0


def for_skillhub(text: str) -> tuple[str, str | None]:
    """SkillHub：补顶层 displayName。返回 (新文本, 错误信息)"""
    parts = _split(text)
    if not parts:
        return text, 'frontmatter 结构无法解析'
    head, body = parts
    if re.search(r'^displayName[ \t]*:', head, re.M):
        return text, None                       # 已有顶层 displayName，不动
    dn = _meta_get(head, 'display-name')
    if not dn:
        return text, 'metadata 里有 display-name，但取不到值'
    head = f'displayName: "{dn}"\n' + head
    return f'---\n{head}\n---\n{body}', None


def for_clawhub(text: str) -> tuple[str, str | None]:
    """ClawHub：删掉 metadata.slug。返回 (新文本, 错误信息)"""
    parts = _split(text)
    if not parts:
        return text, 'frontmatter 结构无法解析'
    head, body = parts
    new_head, dropped = _meta_drop(head, 'slug')
    if not dropped:
        return text, None                       # 本来就没有 slug（可能已剥离过）
    new_head = re.sub(r'\n{3,}', '\n\n', new_head).rstrip('\n')
    return f'---\n{new_head}\n---\n{body}', None


PLATFORMS = {'skillhub': for_skillhub, 'clawhub': for_clawhub}


def stage(name: str, platform: str, out_root: Path) -> tuple[Path, str | None]:
    src = SKILLS / name
    if not (src / 'SKILL.md').exists():
        raise SystemExit(f'❌ 找不到技能目录：{src}')

    dst = out_root / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    skill_md = dst / 'SKILL.md'
    text = skill_md.read_text(encoding='utf-8', newline='')
    new_text, err = PLATFORMS[platform](text)
    if err:
        return dst, err
    if new_text != text:
        skill_md.write_text(new_text, encoding='utf-8', newline='')
    return dst, None


def verify(dst: Path, platform: str) -> str | None:
    """暂存副本必须满足目标平台的字段要求"""
    text = (dst / 'SKILL.md').read_text(encoding='utf-8')
    parts = _split(text)
    if not parts:
        return 'frontmatter 结构坏了'
    head = parts[0]
    if platform == 'skillhub':
        # SkillHub CLI 的 frontmatter 解析器不认缩进，键名必须正好是 displayName
        if not re.search(r'^displayName[ \t]*:[ \t]*\S', head, re.M):
            return '缺顶层 displayName'
    else:
        if re.search(r'^[ \t]+slug[ \t]*:', head, re.M):
            return '仍含 metadata.slug'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('skill', nargs='?', help='技能名；省略时需配合 --all')
    ap.add_argument('--all', action='store_true', help='暂存全部技能')
    ap.add_argument('--platform', choices=sorted(PLATFORMS), default='clawhub',
                    help='目标平台（决定怎么改 frontmatter）')
    ap.add_argument('--out', default=None, help='暂存根目录')
    ap.add_argument('--list', action='store_true', help='只打印技能名')
    a = ap.parse_args()

    if a.list:
        for d in sorted(SKILLS.iterdir()):
            if (d / 'SKILL.md').exists():
                print(d.name)
        return 0

    out_root = Path(a.out) if a.out else DEFAULT_OUT / a.platform
    out_root.mkdir(parents=True, exist_ok=True)

    if a.all or not a.skill:
        names = [d.name for d in sorted(SKILLS.iterdir()) if (d / 'SKILL.md').exists()]
    else:
        names = [a.skill]

    problems = 0
    single = bool(a.skill) and not a.all
    for n in names:
        dst, err = stage(n, a.platform, out_root)
        if err:
            print(f'❌ {n}: {err}', file=sys.stderr)
            problems += 1
            continue
        verr = verify(dst, a.platform)
        if verr:
            print(f'❌ {n}: 暂存副本校验失败 —— {verr}', file=sys.stderr)
            problems += 1
            continue
        if single:
            print(dst)          # 单个模式：stdout 只输出路径，供批处理捕获
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
