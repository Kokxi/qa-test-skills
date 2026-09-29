#!/usr/bin/env python3
"""SKILL.md 元数据读取helper（Agent Skills 规范形态）。

背景
----
规范（https://agentskills.io/specification）只允许 SKILL.md frontmatter 出现
name / description / license / compatibility / metadata / allowed-tools。
本仓库原先的自定义字段（version / when_to_use / related_skills / references /
input_format / output_format / categories / error_recovery_guidance /
depth_requirement_quantification / slug / displayName）已于 scripts/migrate_frontmatter.py
下沉到 metadata，复杂值以紧凑 JSON 字符串存放（规范要求 metadata 为 string->string）。

本模块是所有校验/发布脚本读取这些字段的唯一入口，避免各脚本各写一套正则。
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'
ENTRY_SKILL = 'qa-test-skills'
LICENSE = 'MIT'

# 自定义字段 -> metadata 键（与 migrate_frontmatter.py 的 FIELD_MAP 保持一致）
METADATA_KEYS = {
    'version': 'version',
    'slug': 'slug',
    'displayName': 'display-name',
    'when_to_use': 'when-to-use',
    'related_skills': 'related-skills',
    'references': 'references',
    'input_format': 'input-format',
    'output_format': 'output-format',
    'error_recovery_guidance': 'error-recovery-guidance',
    'categories': 'categories',
    'depth_requirement_quantification': 'depth-requirement',
}

SPEC_TOP_FIELDS = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.iterdir() if (p / 'SKILL.md').exists())


def skill_names() -> set[str]:
    return {d.name for d in skill_dirs()}


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', newline='').replace('\r\n', '\n')


def split_doc(path: Path) -> tuple[dict, str]:
    """返回 (frontmatter dict, 正文)。无 frontmatter 时返回 ({}, 全文)。"""
    raw = read_text(path)
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m:
        return {}, raw
    if yaml is not None:
        try:
            return (yaml.safe_load(m.group(1)) or {}), m.group(2)
        except Exception:  # noqa: BLE001 - 退回正则，尽力解析
            pass
    return _fallback_frontmatter(m.group(1)), m.group(2)


def _fallback_frontmatter(text: str) -> dict:
    fm: dict = {}
    for ln in text.split('\n'):
        m = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', ln)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


@lru_cache(maxsize=None)
def load(skill: str) -> dict:
    d = SKILLS_DIR / skill
    if not (d / 'SKILL.md').exists():
        raise FileNotFoundError(skill)
    fm, body = split_doc(d / 'SKILL.md')
    meta = fm.get('metadata') or {}
    if not isinstance(meta, dict):
        meta = {}
    return {'name': fm.get('name', skill), 'description': fm.get('description', ''),
            'frontmatter': fm, 'metadata': meta, 'body': body}


def raw(skill: str, field: str, default=None):
    """取自定义字段，兼容已迁移（metadata）与未迁移（顶层）两种形态。"""
    d = load(skill)
    key = METADATA_KEYS.get(field, field)
    if key in d['metadata']:
        return d['metadata'][key]
    if field in d['frontmatter']:
        return d['frontmatter'][field]
    return default


def structured(skill: str, field: str, default=None):
    """取自定义字段并把 JSON 字符串还原成结构化值。"""
    v = raw(skill, field)
    if v is None or v == '':
        return default
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default


def version(skill: str) -> str | None:
    v = raw(skill, 'version')
    return str(v).strip() if v is not None else None


def related_skills(skill: str) -> dict:
    return structured(skill, 'related_skills', {}) or {}


def referenced_skills(skill: str) -> set[str]:
    """related_skills 里出现的全部技能名（all_skills / upstream / downstream）。"""
    rel = related_skills(skill)
    out: set[str] = set()
    for value in rel.values():
        if isinstance(value, list):
            out.update(str(x) for x in value)
        elif isinstance(value, str):
            out.add(value)
    return out


def references(skill: str) -> list[str]:
    v = structured(skill, 'references', []) or []
    return [str(x) for x in v]


def when_to_use(skill: str) -> str:
    return str(raw(skill, 'when_to_use', '') or '')


def categories(skill: str) -> list[str]:
    v = structured(skill, 'categories', []) or []
    return [str(x) for x in v]


def output_format(skill: str) -> dict:
    return structured(skill, 'output_format', {}) or {}


def traceability(skill: str) -> list[str]:
    of = output_format(skill)
    tr = of.get('traceability') if isinstance(of, dict) else None
    return [str(x) for x in tr] if isinstance(tr, list) else []


def non_spec_fields(skill: str) -> list[str]:
    """仍留在顶层的非规范字段（迁移应已清空，此处供门禁检测）。"""
    return sorted(set(load(skill)['frontmatter']) - SPEC_TOP_FIELDS)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    for name in sys.argv[1:]:
        d = load(name)
        print(f'{name}  version={version(name)}  refs={references(name)}')
        print(f'  related -> {json.dumps(related_skills(name), ensure_ascii=False)}')
        print(f'  non-spec top fields: {non_spec_fields(name) or "none"}')
