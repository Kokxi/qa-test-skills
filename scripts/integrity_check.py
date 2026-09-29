#!/usr/bin/env python3
"""完整性一致性检查（10 项）

字段读取统一走 scripts/skillmeta.py，适配 Agent Skills 规范形态：
规范只允许 name/description/license/compatibility/metadata/allowed-tools 六个顶层字段，
本仓库的自定义字段全部收在 metadata 下（复杂值为 JSON 字符串）。
"""
import sys, re, json, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / 'skills'
ENTRY = 'qa-test-skills'  # 入口工作流
REQUIRED_META = ['version', 'when-to-use', 'related-skills', 'input-format',
                 'output-format', 'categories', 'depth-requirement',
                 'error-recovery-guidance']
# 入口是编排器，categories/depth-requirement/error-recovery-guidance 为叶子技能专属
ENTRY_EXEMPT = {'categories', 'depth-requirement', 'error-recovery-guidance'}

names = [d.name for d in skillmeta.skill_dirs()]
name_set = set(names)
issues = {}

def add(cat, *msgs):
    issues.setdefault(cat, []).extend(msgs)

# 1. 非规范顶层字段 + 必填 metadata + traceability
f1 = []
for n in names:
    extra = skillmeta.non_spec_fields(n)
    if extra:
        f1.append(f"{n}: 顶层残留非规范字段 {extra}")
    meta = skillmeta.load(n)['metadata']
    for key in REQUIRED_META:
        if key in ENTRY_EXEMPT and n == ENTRY:
            continue
        if not meta.get(key):
            f1.append(f"{n}: 缺 metadata.{key}")
    if n != ENTRY and not skillmeta.traceability(n):
        f1.append(f"{n}: output-format 缺 traceability")
add('frontmatter', *f1)

# 1b. metadata 里 JSON 编码的值必须真的能解析
#     （structured() 解析失败会静默返回默认值，坏数据会无声消失 —— 必须显式拦住）
import json as _json
f1b = []
JSON_META = ['categories', 'references', 'related-skills', 'input-format',
             'output-format', 'error-recovery-guidance', 'depth-requirement']
for n in names:
    meta = skillmeta.load(n)['metadata']
    for k in JSON_META:
        v = meta.get(k)
        if v in (None, ''):
            continue
        try:
            parsed = _json.loads(v)
        except ValueError as exc:
            pos = getattr(exc, 'pos', None)
            near = f' …{v[max(0, pos - 60):pos + 30]}…' if pos is not None else ''
            f1b.append(f'{n}: metadata.{k} 不是合法 JSON（{exc}）{near}')
            continue
        if k == 'output-format' and not (isinstance(parsed, dict) and parsed.get('traceability')):
            f1b.append(f'{n}: metadata.output-format 解析后缺 traceability')
add('frontmatter', *f1b)

# 2. name vs 目录名
f2 = [f"{n}: name={skillmeta.load(n)['name']} != 目录名 {n}"
      for n in names if skillmeta.load(n)['name'] != n]
add('name', *f2)

# 3. version 一致性（以入口为基准，不硬编码具体版本号）
expected = skillmeta.version(ENTRY)
f3 = []
if not expected:
    f3.append('入口 SKILL.md 缺 metadata.version')
for n in names:
    v = skillmeta.version(n)
    if v and expected and v != expected:
        f3.append(f"{n}: {v} (期望 {expected})")
    if not v:
        f3.append(f"{n}: 缺 metadata.version")
add('version', *f3)

# 4. related-skills 悬空
f4 = []
for n in names:
    for ref in skillmeta.referenced_skills(n):
        if ref not in name_set:
            f4.append(f"{n}: 引用不存在的 {ref}")
add('related', *f4)

dep = subprocess.run([sys.executable, 'scripts/validate_deps.py'],
                     capture_output=True, text=True, encoding='utf-8', cwd=str(ROOT))
dep_ok = '✅ 没有引用错误' in dep.stdout

# 5. references/ 引用悬空 + 越出 skill 根目录的链接
f5 = []
for n in names:
    for rel in skillmeta.references(n):
        if not (SKILLS_DIR / n / rel).exists():
            f5.append(f"{n}: {rel} 不存在")
    body = skillmeta.load(n)['body']
    for m in re.finditer(r'\]\((\.\./)+', body):        # 越出 skill 根目录
        f5.append(f"{n}: 正文存在越根链接 {m.group(0)}(...)")
    # 路径感知的 references 引用校验：
    #   references/x.md            -> 本技能 references/
    #   <兄弟技能>/references/x.md  -> 那个兄弟技能的 references/
    for m in re.finditer(r'([\w-]+/references|references)/([\w.-]+\.md)', body):
        prefix, fname = m.group(1), m.group(2)
        if prefix == 'references':
            base = SKILLS_DIR / n
        else:
            owner = prefix.split('/')[0]
            if owner == n:
                base = SKILLS_DIR / n
            elif (SKILLS_DIR / owner / 'references').is_dir():
                base = SKILLS_DIR / owner
            else:
                continue                                # 非技能目录，跳过
        if not (base / 'references' / fname).exists():
            f5.append(f"{n}: 正文引用 {prefix}/{fname} 不存在")
add('references', *f5)

# 6. ID 规范一致性（standards.md 中 TC_ 用下划线、REQ-/SC- 等用连字符，两种都要认）
std = (ROOT / 'docs' / 'standards.md').read_text(encoding='utf-8').replace('\r\n', '\n')
declared = set(re.findall(r'([A-Z]+)[-_]\{模块缩写\}', std))
used = set()
for n in names:
    for tr in skillmeta.traceability(n):
        for m in re.finditer(r'([A-Z]+)[-_]\{', tr):
            used.add(m.group(1))
f6 = [f"用例声明了 standards.md 未定义的 ID 前缀: {sorted(used - declared)}"] if used - declared else []

# 7. 检查清单存在性
#    清单可以放在 SKILL.md 正文（每轮都要逐项过的短清单），
#    也可以放在 references/ 下（内容较长、按需加载）——两种都算合规。
#    assets/ 里的产出模板不算清单。
#    标题形态：检查清单 / 自检清单 / 自检 / 交付前自检 / 验收清单
#    （验收清单是入口技能 qa-test-skills 在用的写法，见 gate_selftest 的 LEGAL 用例）
CLEAN = r'检查清单|自检清单|自检|验收清单|交付清单'
f7 = []
for n in names:
    d = SKILLS_DIR / n
    body = skillmeta.load(n)['body']
    pat = rf'^##\s*(?:\d+\.\s*)?(?:交付前)?(?:{CLEAN})'
    in_body = re.search(pat, body, re.M)
    in_refs = any(re.search(pat, r.read_text(encoding='utf-8'), re.M)
                  for r in (d / 'references').glob('*.md')) if (d / 'references').is_dir() else False
    if not (in_body or in_refs):
        f7.append(n)

# 8. UTF-8 BOM
f8 = []
for n in names:
    if (SKILLS_DIR / n / 'SKILL.md').read_bytes().startswith(b'\xef\xbb\xbf'):
        f8.append(n)
for p in list(SKILLS_DIR.glob('*/SKILL.md')) + list((ROOT / 'scripts').glob('*.py')) \
        + list((ROOT / 'evals').glob('*.json')):
    if p.read_bytes().startswith(b'\xef\xbb\xbf'):
        f8.append(str(p.relative_to(ROOT)))

# 9. evals.json 结构
f9 = []
data = json.loads((ROOT / 'evals' / 'evals.json').read_text(encoding='utf-8'))
ids = set()
for e in data['evals']:
    eid = e.get('id')
    if eid in ids:
        f9.append(f"eval id {eid} 重复")
    ids.add(eid)
    for fld in ['prompt', 'expected_output', 'assertions']:
        if fld not in e:
            f9.append(f"eval#{eid}: 缺 {fld}")
    for a in e.get('assertions', []):
        if 'type' not in a or 'name' not in a:
            f9.append(f"eval#{eid}: assertion 缺 type/name")

# 10. 安全审计残留：过宽的裸泛化触发词
GENERIC = {'测试', '分析', '评估', '评审', '管理', '设计', '策略', '报告', '复盘'}
f10 = []
for n in names:
    for kw in re.findall(r'"([^"]+)"', skillmeta.when_to_use(n)):
        if len(kw) <= 3 and kw in GENERIC:
            f10.append(f"{n}: {kw}")
SENSITIVE = ['qa-boundary-deep-dive', 'qa-bug-lifecycle', 'qa-bug-reporting',
             'qa-bug-root-cause-analysis', 'qa-combination-strategy', 'qa-critical-thinking',
             'qa-exploratory-testing', 'qa-input-validation', 'qa-question-framework',
             'qa-req-deconstruction', 'qa-scenario-tree', 'qa-stakeholder-communication',
             'qa-test-automation-arch']
missing_warn = [n for n in SENSITIVE
                if '⚠️ 安全警告' not in (SKILLS_DIR / n / 'SKILL.md').read_text(encoding='utf-8')]

# 11. evals 断言的 ID 前缀必须与 docs/standards.md 一致
#     （历史缺陷：断言写 TC- 而技能规定 TC_，合规输出恒判负分）
f11 = []
std_prefix = {}
for m in re.finditer(r'([A-Z]{2,6})([-_])\{', std):
    std_prefix.setdefault(m.group(1), m.group(2))
IDLIKE = re.compile(r'^([A-Z]{2,6})([-_])[-*]?$')
for e in data['evals']:
    for a in e.get('assertions', []):
        for key in ('target', 'targets'):
            v = a.get(key)
            if not isinstance(v, (str, list)):
                continue
            for t in ([v] if isinstance(v, str) else v):
                m = IDLIKE.match(str(t))
                if not m:
                    continue
                pfx, sep = m.group(1), m.group(2)
                want = std_prefix.get(pfx)
                if want is None:
                    f11.append(f"eval#{e.get('id')} 「{a.get('name')}」target={t!r} 不在 standards.md")
                elif want != sep:
                    f11.append(f"eval#{e.get('id')} 「{a.get('name')}」target={t!r} 应为 {pfx}{want}")

# 12. 版本号同步：manifest / 发布脚本必须与入口 SKILL.md 的 metadata.version 一致
#     （历史缺陷：技能 1.7.9、manifest 1.7.7、publish-all.bat 默认 1.7.0 → 发布即降版本）
f12 = []
SYNC_JSONS = ['plugin/package.json', 'plugin/openclaw.plugin.json',
              '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
              '.agents/plugins/marketplace.json']
SYNC_BATS = ['publish-all.bat', 'scripts/push-clawhub.bat', 'scripts/push-skillhub.bat']
if expected:
    for rel in SYNC_JSONS:
        p = ROOT / rel
        if not p.exists():
            f12.append(f'{rel}: 文件不存在')
            continue
        found = set(re.findall(r'"version"\s*:\s*"([0-9][^"]*)"',
                               p.read_text(encoding='utf-8')))
        bad = {v for v in found if v != expected}
        if bad:
            f12.append(f'{rel}: {sorted(bad)} 与基准 {expected} 不一致')
    for rel in SYNC_BATS:
        p = ROOT / rel
        if not p.exists():
            f12.append(f'{rel}: 文件不存在')
            continue
        # .bat 必须是 GBK 编码 + CRLF 行尾，否则 cmd.exe 解析会错乱。
        # 历史踩坑：文件是 UTF-8 时中文注释被当 GBK 解释，症状是
        # 报「'xxx' 不是内部或外部命令」；行尾是 LF 时多行 ( ) 块会被拆成独立命令。
        raw = p.read_bytes()
        try:
            raw.decode('gbk')
        except UnicodeDecodeError as exc:
            f12.append(f'{rel}: 不是 GBK 编码（cmd.exe 按系统 ANSI 码页读 .bat），{exc}')
            continue
        crlf, lf = raw.count(b'\r\n'), raw.count(b'\n') - raw.count(b'\r\n')
        if crlf == 0:
            f12.append(f'{rel}: 行尾是纯 LF，cmd.exe 解析多行 ( ) 块会错乱，需 CRLF')
        elif lf > 0:
            f12.append(f'{rel}: 行尾 CRLF/LF 混用（CRLF={crlf} LF={lf}）')
        bat = raw.decode('gbk')
        # 既看真正生效的 set "VER=..."，也看 REM 注释里的说明
        # （注释写着旧版本号，下一个人照着改就又埋一次降版本的雷）
        for m in re.finditer(r'set\s+"VER=([0-9][\d.]*)"', bat):
            if m.group(1) != expected:
                f12.append(f'{rel}: 默认版本 {m.group(1)} 与基准 {expected} 不一致（发布会降版本）')
        for m in re.finditer(r'(?:default\s+version\s*=\s*|\(default:\s*)([0-9][\d.]*)', bat, re.I):
            if m.group(1) != expected:
                f12.append(f'{rel}: 注释里的版本 {m.group(1)} 与基准 {expected} 不一致')

# 13. output-format 声明的产出物必须真的产出
#     （历史缺陷：46 个技能声明「固定 9 列用例表」，其中 41 个根本不产用例表 ——
#      复制粘贴样板导致缺陷报告/复盘/看板/发布方案被声明成用例表）
#     判定用「真实 9 列表头」而非「有没有表格」：技能可能产出别的表格。
#     注意：只判「无真实用例表却声明」，不判「正文未内嵌样例」——
#     output_format 是给 agent 的产出契约，声明格式而不贴样例是合法的。
COLS9 = ['用例编号', '测试类型', '功能模块', '测试标题', '用例级别',
         '预置条件', '测试步骤', '预期结果', '风险等级']


def _has_real_case_table(n: str) -> bool:
    d = SKILLS_DIR / n
    texts = [skillmeta.load(n)['body']]
    for sub in ('references', 'assets'):
        p = d / sub
        if p.is_dir():
            texts += [f.read_text(encoding='utf-8') for f in p.rglob('*.md')]
    for t in texts:
        for line in t.splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) == 9 and sum(1 for c in COLS9 if c in cells) >= 7:
                return True
    return False


f13 = []
for n in names:
    of = skillmeta.output_format(n)
    st = str(of.get('structure', '')) if isinstance(of, dict) else ''
    if '固定 9 列' in st and not _has_real_case_table(n):
        f13.append(f'{n}: 声明「固定 9 列用例表」但技能目录下无真实 9 列用例表（复制粘贴污染）')

# 14. traceability 的关联 ID 前缀必须正确
#     （历史缺陷：格式 owner qa-test-case-design 把「关联需求ID」「关联场景ID」写成 TC_ 前缀，
#      其余 7 个技能照抄，共 9-10 处）
f14 = []
# 覆盖多种句式与多种引导符：
#   关联需求ID（TC_…）  关联需求ID(TC_…)  关联需求ID：TC_…  关联需求ID: TC_…
# 只认括号形式会漏掉冒号形式——仓库里两种都在用（见 gate_selftest 的 INJECT 用例）。
BAD_TRACE = re.compile(r'(需求|场景)[^，。）)]{0,10}(ID|id)[^，。）)]{0,4}(?:[（(]|[:：])[^，。）)]{0,4}TC_')
for n in names:
    for tr in skillmeta.traceability(n):
        if BAD_TRACE.search(tr):
            f14.append(f'{n}: 关联 ID 误用 TC_ 前缀 → {tr.strip()[:60]}')

# 15. metadata.references 必须登记全部 references/ 与 assets/ 文件
f15 = []
for n in names:
    d = SKILLS_DIR / n
    real = set()
    for sub in ('references', 'assets'):
        p = d / sub
        if p.is_dir():
            real |= {f'{sub}/{f.name}' for f in p.rglob('*') if f.is_file()}
    if not real:
        continue
    missing = real - set(skillmeta.references(n))
    if missing:
        f15.append(f'{n}: metadata.references 漏登记 {sorted(missing)}')

# ---- 15 项检查结果登记表（报告与 --json 共用同一份数据，避免两处逻辑漂移）----
# severity: hard = 阻断门禁；soft = 仅提示
RESULTS = [
    (1,  'frontmatter 规范形态 + 必填 metadata', 'hard', issues.get('frontmatter', [])),
    (2,  'name vs 目录名',                        'hard', issues.get('name', [])),
    (3,  'version 一致性',                        'hard', issues.get('version', [])),
    (4,  'related-skills 悬空 + 依赖对称',         'hard', issues.get('related', [])
                                                          + ([] if dep_ok else ['依赖不对称'])),
    (5,  'references/ 悬空 + 越根链接',            'hard', issues.get('references', [])),
    (6,  'ID 规范一致性',                         'hard', f6),
    (7,  '检查清单存在性（正文或 references 均可）', 'soft', f7),
    (8,  'UTF-8 BOM',                             'hard', f8),
    (9,  'evals.json 结构',                       'hard', f9),
    (10, '安全审计残留',                          'hard', f10 + [f'{n}: 缺安全警告'
                                                           for n in missing_warn]),
    (11, 'evals ID 前缀与 standards.md 一致',      'hard', f11),
    (12, '版本号同步（manifest / 发布脚本）',       'hard', f12),
    (13, 'output-format 声明与实际产出一致',        'hard', f13),
    (14, '关联 ID 前缀正确性',                     'hard', f14),
    (15, 'metadata.references 登记完整性',         'hard', f15),
]

if '--json' in sys.argv:
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps({
        'checks': [{'id': i, 'title': t, 'severity': s,
                    'count': len(v), 'items': list(v)[:20]}
                   for i, t, s, v in RESULTS],
        'hard': sum(len(v) for i, t, s, v in RESULTS if s == 'hard'),
        'soft': sum(len(v) for i, t, s, v in RESULTS if s == 'soft'),
    }, ensure_ascii=False, indent=2))
    sys.exit(1 if any(s == 'hard' and v for i, t, s, v in RESULTS) else 0)

# ---- 人类可读报告 ----
sys.stdout.reconfigure(encoding='utf-8')
for num, title, sev, items in RESULTS:
    mark = '✅' if not items else ('❌' if sev == 'hard' else '⚠️')
    unit = '项' if sev == 'hard' else '缺检查清单'
    print(f"\n=== {num}. {title} ===")
    print(f"  {mark} {len(items)} {unit}")
    for i in items[:6]:
        print(f"    {i}")

if expected:
    print(f"\n  （版本基准 {expected}｜standards 定义 {len(declared)} 个 ID 前缀"
          f"｜{len(data['evals'])} 个 eval｜{len(names)} 个技能）")

hard = sum(len(v) for i, t, s, v in RESULTS if s == 'hard')
soft = sum(len(v) for i, t, s, v in RESULTS if s == 'soft')
print("\n" + "=" * 50)
print(f"汇总: ❌{hard} 项硬问题 + ⚠️{soft} 项软问题")
bad = {f"{i} {t[:12]}": len(v) for i, t, s, v in RESULTS if v and s == 'hard'}
if bad:
    print("  失分项: " + ", ".join(f"{k}×{n}" for k, n in bad.items()))
print("=" * 50)
sys.exit(1 if hard else 0)
