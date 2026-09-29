#!/usr/bin/env python3
"""frontmatter 规范迁移：把非规范字段收进 metadata（Agent Skills spec）。

背景
----
Agent Skills 规范（https://agentskills.io/specification）只允许 SKILL.md frontmatter
出现 6 个字段：name / description / license / compatibility / metadata / allowed-tools。
其中 metadata 是「string -> string」映射。本仓库此前把 11 个自定义字段放在顶层，
导致官方参考实现 skills-ref validate 对全部 49 个技能判失败。

本脚本把这些字段降级进 metadata（复杂值用紧凑 JSON 字符串），
并把 when_to_use 的触发词并入 description —— 规范规定 description 是唯一触发依据，
非规范字段多数客户端读不到，这一步同时修掉触发面缺失的实质缺陷。

用法
----
  python scripts/migrate_frontmatter.py            # 迁移
  python scripts/migrate_frontmatter.py --check     # 只体检不写盘，CI 用
  python scripts/migrate_frontmatter.py --force     # 已迁移的也重算 description
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit('需要 pyyaml：pip install pyyaml')

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'
TRIGGERS = ROOT / 'scripts' / 'i18n_triggers.json'
LICENSE = 'MIT'

# 规范允许的顶层字段（skills-ref 校验白名单）
SPEC_TOP = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}

# 顶层自定义字段 -> metadata 键名。None 表示原样保留键名。
FIELD_MAP = {
    'slug': 'slug',
    'displayName': 'display-name',
    'version': 'version',
    'disable-model-invocation': 'disable-model-invocation',
    'when_to_use': 'when-to-use',
    'related_skills': 'related-skills',
    'references': 'references',
    'input_format': 'input-format',
    'output_format': 'output-format',
    'error_recovery_guidance': 'error-recovery-guidance',
    'categories': 'categories',
    'depth_requirement_quantification': 'depth-requirement',
}

# 每个技能都有的营销句，从 description 里剔除（信息在正文顶部与 README 已有）
MARKETING = re.compile(
    r'\s*本技能属于\s*QA\s*Test\s*Skills\s*技能集[^\n]*?npx skills add\s+\S+', re.S
)
# description 尾部的安装提示
INSTALL_HINT = re.compile(r'\s*完整工作流体验需安装全套[^\n]*?(?=。|$)', re.S)

MAX_DESC = 1024  # 规范硬上限


def read_skill(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding='utf-8', newline='').replace('\r\n', '\n')
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m:
        raise ValueError(f'{path}: 无 frontmatter')
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def load_triggers() -> dict:
    return json.loads(TRIGGERS.read_text(encoding='utf-8'))['triggers']


def scalar(value) -> str:
    """metadata 的值必须是字符串：标量用 JSON 编码，复杂值用紧凑 JSON。"""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def yaml_str(text: str) -> str:
    """把任意字符串安全地表达成 YAML 单行标量（带引号，永不触发 flow-style 解析）。"""
    return json.dumps(text, ensure_ascii=False)


def extract_zh_triggers(when_to_use: str) -> str:
    """从 when_to_use 抽中文触发词：优先取引号内的词，再补尾部条件短语。"""
    when_to_use = ' '.join(str(when_to_use).split())
    quoted = re.findall(r'"([^"]{1,20})"', when_to_use)
    seen, terms = set(), []
    for q in quoted:
        if q not in seen:
            seen.add(q)
            terms.append(q)
    tail = re.sub(r'"[^"]{1,20}"', '', when_to_use)
    tail = re.split(r'[、,]', tail)[-1].strip(' ，。')
    tail = re.sub(r'^用户说', '', tail).strip(' ，。')
    if tail and len(tail) <= 40 and tail not in seen:
        terms.append(tail)
    return '、'.join(terms)


def build_description(zh_desc: str, when_to_use: str, en_triggers: str) -> str:
    """保留原有中文描述（去营销），追加中英双语触发场景，压到规范 1024 字符以内。"""
    zh = ' '.join(str(zh_desc).split())
    zh = INSTALL_HINT.sub('', MARKETING.sub('', zh)).strip()
    zh_terms = extract_zh_triggers(when_to_use)
    en = ' '.join(str(en_triggers or '').split())

    tail_bits = []
    if zh_terms:
        tail_bits.append(f'触发场景：{zh_terms}。')
    if en:
        tail_bits.append(f'Use when the user asks about: {en}.')
    tail = ' '.join(tail_bits)

    if not tail:
        return zh[:MAX_DESC]

    budget = MAX_DESC - len(tail) - 1
    if budget < len(zh):  # 超限时压缩主描述，保留触发词（触发价值更高）
        zh = zh[:budget].rstrip('，,、 ') + '。'
    return f'{zh} {tail}'.strip()


def fold(text: str, indent: str = '  ') -> str:
    """折叠块标量 >- ：多行拼接为一行，规避不同 YAML loader 的换行解析差异。"""
    assert '\n' not in text
    return indent + text


def migrate(path: Path, triggers: dict, force: bool) -> tuple[str, bool, list[str]]:
    fm, body = read_skill(path)
    name = fm.get('name') or path.parent.name
    notes: list[str] = []

    already = 'metadata' in fm and not (set(fm) - SPEC_TOP)
    if already and not force:
        return 'skip', False, notes

    metadata: dict[str, str] = {}
    for key, target in FIELD_MAP.items():
        if key in fm and fm[key] not in (None, [], {}):
            metadata[target] = scalar(fm[key])

    desc = build_description(
        fm.get('description', ''),
        fm.get('when_to_use', ''),
        triggers.get(name, ''),
    )
    if len(desc) > MAX_DESC:
        notes.append(f'description {len(desc)} 字符超限，已截断到 {MAX_DESC}')
        desc = desc[:MAX_DESC]
    if not triggers.get(name):
        notes.append('scripts/i18n_triggers.json 缺英文触发词，description 未含英文侧')

    # 组装：规范字段按 spec 顺序，非规范内容全部下沉 metadata
    out = ['---', f'name: {name}']
    out.append('description: >-')
    out.append(fold(desc))
    out.append(f'license: {LICENSE}')
    if fm.get('allowed-tools'):
        out.append(f"allowed-tools: {fm['allowed-tools']}")
    if metadata:
        out.append('metadata:')
        for k, v in metadata.items():
            out.append(f'  {k}: {yaml_str(v)}')
    out.append('---')

    new_raw = '\n'.join(out) + '\n' + body
    if not force and new_raw == path.read_text(encoding='utf-8', newline='').replace('\r\n', '\n'):
        return 'unchanged', False, notes

    # 统一 LF + 无 BOM
    io.open(path, 'w', encoding='utf-8', newline='\n').write(new_raw)
    return ('migrated' if already else 'new'), True, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='只体检不写盘')
    ap.add_argument('--force', action='store_true', help='已迁移的也重算')
    args = ap.parse_args()

    triggers = load_triggers()
    skills = sorted(p for p in SKILLS_DIR.iterdir() if (p / 'SKILL.md').exists())
    tally = {'migrated': 0, 'new': 0, 'skip': 0, 'unchanged': 0}
    changed, problems = [], []

    for d in skills:
        try:
            state, did_write, notes = migrate(d / 'SKILL.md', triggers, args.force)
        except Exception as exc:  # noqa: BLE001 - 迁移要尽量跑完
            problems.append(f'{d.name}: {exc}')
            continue
        tally[state] += 1
        if did_write:
            changed.append(d.name)
        for n in notes:
            problems.append(f'{d.name}: {n}')

    verb = '待迁移' if args.check else '已迁移'
    print(f'=== frontmatter 规范迁移（{verb}）===')
    print(f'  技能总数: {len(skills)}')
    print(f"  新迁移 {tally['new']} / 重算 {tally['migrated']} / "
          f"未变 {tally['unchanged']} / 已是规范形态 {tally['skip']}")
    if changed:
        print(f'  涉及文件 ({len(changed)}): {", ".join(changed[:6])}'
              f'{"..." if len(changed) > 6 else ""}')
    if problems:
        print(f'\n⚠️  {len(problems)} 项需关注:')
        for p in problems:
            print(f'  - {p}')

    if args.check and changed:
        print('\n❌ 存在未迁移的 SKILL.md，运行 python scripts/migrate_frontmatter.py')
        return 1
    if problems:
        return 1
    print('\n✅ 全部 frontmatter 符合 Agent Skills 规范')
    return 0


if __name__ == '__main__':
    sys.exit(main())
