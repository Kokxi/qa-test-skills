#!/usr/bin/env python3
"""门禁双向自测：对 integrity_check.py 的 15 项检查逐项验证「该报的报、不该报的不报」。

为什么需要它
------------
门禁的价值全在正则准不准。太松 → 缺陷漏过（41 个技能的虚假 9 列声明就是这么活下来的）；
太严 → 噪音淹没真问题（检查项 13 初版误报 29 条、检查项 7 把「验收清单」判为缺清单）。
但只看「当前仓库是否通过」无法区分这两种情况——它同时也是「检查坏了」的表现。

所以每个检查都必须有两类用例：
  INJECT  注入一个已知违规 → 必须报（防漏）
  LEGAL   放一个形似但合规的内容 → 必须不报（防误报）

用法
----
  python scripts/gate_selftest.py            # 跑全部
  python scripts/gate_selftest.py --check 14  # 只跑某项
  python scripts/gate_selftest.py -v          # 打印每个用例的报错内容
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

# 复制到临时工作区的目录（.git 排除；examples 不参与任何检查）
COPY_DIRS = ['skills', 'scripts', 'evals', 'docs', 'plugin', '.claude-plugin', '.agents']
COPY_FILES_EXTRA = ['publish-all.bat']
COPY_FILES = ['publish-all.bat']

# 被注入的技能（挑覆盖面广的，且不参与其他检查的敏感判定）
T = 'qa-test-case-design'      # 产出 9 列用例表的真源
PLAIN = 'qa-bug-lifecycle'     # 不产用例表
SENSITIVE = 'qa-scenario-tree'  # 在 SENSITIVE 名单里，带安全警告


# ---------- 工具 ----------
def stage(ws: Path):
    """把仓库内容复制到临时工作区"""
    for d in COPY_DIRS:
        src, dst = ROOT / d, ws / d
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
    for f in COPY_FILES + COPY_FILES_EXTRA:
        if (ROOT / f).exists():
            dst = ws / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / f, dst)


def restore(ws: Path, files):
    """把被改过的文件从源仓库还原"""
    for rel in files:
        src, dst = ROOT / rel, ws / rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif dst.exists():
            dst.unlink()


def run_check(ws: Path):
    r = subprocess.run([sys.executable, 'scripts/integrity_check.py', '--json'],
                       cwd=str(ws), capture_output=True, text=True, encoding='utf-8')
    try:
        return {c['id']: c for c in json.loads(r.stdout)['checks']}, r
    except (ValueError, KeyError):
        raise AssertionError(f'integrity_check.py --json 无法解析：\n'
                             f'stdout={r.stdout[:400]}\nstderr={r.stderr[:400]}')


def fm_shape(ws: Path, rel: str) -> str:
    """dump 改动后文件的 frontmatter 键位与缩进，用于分辨「注入坏了」还是「检查坏了」"""
    p = ws / rel
    if not p.exists():
        return f'{rel} 不存在'
    head = p.read_text(encoding='utf-8').partition('\n---\n')[0]
    keys = [f'{len(l) - len(l.lstrip())}:{l.split(":")[0].strip()}'
            for l in head.splitlines() if re.match(r'^\s*[\w-]+:', l)]
    return f'{rel} frontmatter: {" ".join(keys)}'


def raw_meta(ws: Path, skill: str, key: str) -> str:
    """让 skillmeta 自己读一遍，打印它拿到的原始字符串——判断注入是否落地的最直接证据。

    同时打印 yaml 是否抛错：skillmeta.split_doc 在 yaml 失败时会静默回退到扁平正则，
    metadata 会变成 {}，症状是「所有 metadata 键都读不到」，很容易被误判成注入没生效。
    """
    code = (
        "import sys,re,json\n"
        "sys.path.insert(0,'scripts')\n"
        "import yaml\n"
        f"raw=open('skills/{skill}/SKILL.md',encoding='utf-8',newline='').read().replace('\\r\\n','\\n')\n"
        "m=re.match(r'^---\\n(.*?)\\n---\\n(.*)$',raw,re.S)\n"
        "print('split_doc 匹配:',bool(m))\n"
        "try:\n"
        "    fm=yaml.safe_load(m.group(1)) or {}\n"
        "    print('YAML OK, top keys:',list(fm.keys()))\n"
        "    print('直读 metadata keys:',list((fm.get('metadata') or {}).keys()))\n"
        "    print('直读 output-format 前 80:',repr((fm.get('metadata') or {}).get('output-format'))[:80])\n"
        "except Exception as e:\n"
        "    print('YAML 抛错:',type(e).__name__)\n"
        "    print(str(e)[:400])\n"
        "import skillmeta\n"
        "print('skillmeta SKILLS_DIR:',skillmeta.SKILLS_DIR)\n"
        f"d=skillmeta.load({skill!r})\n"
        "print('skillmeta frontmatter keys:',list(d['frontmatter'].keys()))\n"
        "print('skillmeta metadata keys:',list(d['metadata'].keys()))\n"
        f"v=d['metadata'].get({key!r})\n"
        "print('skillmeta 读到:',repr(v)[:200])\n"
    )
    r = subprocess.run([sys.executable, '-c', code], cwd=str(ws),
                       capture_output=True, text=True, encoding='utf-8')
    return (r.stdout or r.stderr).strip()[:700]


def read(ws: Path, rel: str) -> str:
    p = ws / rel
    if p.suffix.lower() == '.bat':
        # .bat 是 GBK（cmd.exe 按系统 ANSI 码页读）
        return p.read_bytes().decode('gbk').replace('\r\n', '\n')
    return p.read_text(encoding='utf-8')


def write(ws: Path, rel: str, text: str):
    """按目标文件的既有编码写回。

    .bat 必须是 GBK + CRLF（cmd.exe 按系统 ANSI 码页读 .bat，LF 行尾会让
    多行 ( ) 块解析错乱）。用 UTF-8 写会把文件改坏——注入用例必须无损。
    """
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() == '.bat':
        p.write_bytes(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('gbk'))
    else:
        p.write_text(text, encoding='utf-8', newline='\n')


def sub_frontmatter(text: str, key: str, old: str, new: str) -> str:
    """在 frontmatter 里替换一行（不动正文）"""
    head, sep, body = text.partition('\n---\n')
    assert old in head, f'锚点不在 frontmatter：{old!r}'
    return head.replace(old, new, 1) + sep + body


def mutate_json_meta(ws: Path, skill: str, key: str, fn, raw=None):
    """解码 metadata.<key> 的 JSON → 应用 fn → 重新编码写回。

    比字符串替换可靠：output-format 之类的值是转义后的 JSON，
    直接拼字符串会匹配不到（而且 YAML 引号嵌套极易出错）。
    """
    p = f'skills/{skill}/SKILL.md'
    text = read(ws, p)
    head, sep, body = text.partition('\n---\n')
    m = re.search(rf'^([ \t]*){re.escape(key)}:\s*"(.*)"[ \t]*$', head, re.M)
    assert m, f'{skill}: frontmatter 里找不到 {key}'
    indent, raw_val = m.group(1), m.group(2)
    # 缩进必须原样保留：metadata 下的键是缩进的，写成顶层就会被判成非规范字段
    val = json.loads(json.loads(f'"{raw_val}"'))
    if raw is not None:
        write(ws, p, head[:m.start()] + f'{indent}{key}: {raw}' + head[m.end():] + sep + body)
        return
    # 注意：fn 可以原地修改 val，也可以返回新对象。
    # 不能只用返回值——list.insert/dict.update 都返回 None，会把字段写成 "null"。
    out = fn(val)
    enc = json.dumps(val if out is None else out, ensure_ascii=False) \
        .replace('\\', '\\\\').replace('"', '\\"')
    write(ws, p, head[:m.start()] + f'{indent}{key}: "{enc}"' + head[m.end():] + sep + body)


# ---------- 注入用例：每个 (检查 id, 名称, 改哪些文件, 怎么改) ----------
def _inj_check_id(p):
    return re.search(r'name:\s*(\S+)', read(p.parent, 'SKILL.md')).group(1)


INJECT = []
LEGAL = []


def legal(cid, name, files, mutate, why):
    """登记一条「合规内容必须不报」的用例——验证的是误报方向。"""
    LEGAL.append((cid, name, files, mutate, why))


def inject(cid, name, files, mutate):
    INJECT.append((cid, name, files, mutate))


# 1 frontmatter
inject(1, '注入非法 JSON（output-format 少一个逗号）',
       [f'skills/{T}/SKILL.md'],
       lambda ws: mutate_json_meta(ws, T, 'output-format', None,
                                   raw='"{\\"structure\\":[,]}"'))

inject(1, '注入顶层非规范字段',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        read(ws, f'skills/{PLAIN}/SKILL.md')
                        .replace('\nlicense: MIT', '\nlicense: MIT\ncustom-top: oops', 1)))

# 2 name vs 目录名
inject(2, 'name 与目录名不一致',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        read(ws, f'skills/{PLAIN}/SKILL.md')
                        .replace(f'name: {PLAIN}', 'name: qa-wrong-name', 1)))

# 3 version
inject(3, '某个技能版本号与其他不一致',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        sub_frontmatter(read(ws, f'skills/{PLAIN}/SKILL.md'),
                                        'version', 'version: "1.', 'version: "9.9.')))

# 4 related-skills 悬空
def _dangling_rel(ws):
    def fn(v):
        k = next(iter(v))
        v[k].append('qa-does-not-exist')
    mutate_json_meta(ws, PLAIN, 'related-skills', fn)


inject(4, 'related-skills 指向不存在的技能',
       [f'skills/{PLAIN}/SKILL.md'], _dangling_rel)

# 5 references
inject(5, '正文引用不存在的 references 文件',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        read(ws, f'skills/{PLAIN}/SKILL.md')
                        .rstrip() + '\n\n见 [`references/nope.md`](references/nope.md)\n'))

inject(5, '正文存在越出技能根目录的链接',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        read(ws, f'skills/{PLAIN}/SKILL.md')
                        .rstrip() + '\n\n见 [全局规范](../../docs/standards.md)\n'))

# 6 ID 规范一致性
inject(6, 'traceability 声明了 standards.md 未定义的前缀',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: mutate_json_meta(ws, PLAIN, 'output-format',
                                   lambda v: v['traceability'].insert(0, 'XX-{模块缩写}-{序号}')))

# 7 检查清单（软）
def _drop_checklist(ws):
    p = f'skills/{PLAIN}/SKILL.md'
    t = read(ws, p)
    t2 = re.sub(r'^##\s*(?:\d+\.\s*)?(?:交付前)?(?:检查清单|自检清单|自检).*$',
                '', t, flags=re.M)
    write(ws, p, t2)


inject(7, '把技能的检查清单整段删掉', [f'skills/{PLAIN}/SKILL.md'], _drop_checklist)

# 8 BOM
inject(8, '给 SKILL.md 加 UTF-8 BOM',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: (ws / f'skills/{PLAIN}/SKILL.md').write_bytes(
           b'\xef\xbb\xbf' + (ws / f'skills/{PLAIN}/SKILL.md').read_bytes()))

# 9 evals 结构
def _dup_eval_id(ws):
    p = 'evals/evals.json'
    d = json.loads(read(ws, p))
    d['evals'].append(dict(d['evals'][0]))
    write(ws, p, json.dumps(d, ensure_ascii=False, indent=2))


inject(9, 'evals 出现重复 id', ['evals/evals.json'], _dup_eval_id)


def _drop_field(ws):
    p = 'evals/evals.json'
    d = json.loads(read(ws, p))
    d['evals'][0].pop('expected_output', None)
    write(ws, p, json.dumps(d, ensure_ascii=False, indent=2))


inject(9, 'eval 缺 expected_output 字段', ['evals/evals.json'], _drop_field)

# 10 安全审计
#     when-to-use 是 YAML 双引号标量，注入的引号必须转义，否则 YAML 解析失败、
#     症状会变成「检查项 1 报错」而不是「检查项 10 报错」
inject(10, 'when-to-use 出现过宽的裸泛化触发词',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                        sub_frontmatter(read(ws, f'skills/{PLAIN}/SKILL.md'),
                                        'when-to-use', '用户说',
                                        '用户说\\"设计\\"、用户说')))

inject(10, '敏感技能删掉安全警告',
       [f'skills/{SENSITIVE}/SKILL.md'],
       lambda ws: write(ws, f'skills/{SENSITIVE}/SKILL.md',
                        read(ws, f'skills/{SENSITIVE}/SKILL.md')
                        .replace('⚠️ 安全警告', '（已移除）')))

# 11 evals ID 前缀
def _wrong_sep(ws):
    p = 'evals/evals.json'
    t = read(ws, p)
    m = re.search(r'"(target|targets?)"\s*:\s*"TC_[-*]?"', t)
    if not m:
        # 没有现成的 TC_ 目标就自己插一个
        d = json.loads(t)
        d['evals'][0]['assertions'].append(
            {'type': 'content_match', 'name': '注入', 'target': 'TC_-', 'value': 'x'})
        write(ws, p, json.dumps(d, ensure_ascii=False, indent=2))
        return
    write(ws, p, t[:m.start()] + m.group(0).replace('TC_', 'TC-', 1) + t[m.end():])


inject(11, 'eval 断言 target 用 TC- 而规范要求 TC_', ['evals/evals.json'], _wrong_sep)

# 12 版本同步
inject(12, 'plugin manifest 版本号与技能基准不一致',
       ['plugin/package.json'],
       lambda ws: write(ws, 'plugin/package.json',
                        re.sub(r'"version": "\d+[\d.]*"', '"version": "1.0.0"',
                               read(ws, 'plugin/package.json'), count=1)))

# 12 的历史缺陷：发布脚本各自硬编码默认版本，只有 publish-all.bat 被检查，
#     push-clawhub.bat / push-skillhub.bat 漏检 -> 不带参数运行会发布降版本
inject(12, 'push-clawhub.bat 默认版本落后于技能基准',
       ['scripts/push-clawhub.bat'],
       lambda ws: write(ws, 'scripts/push-clawhub.bat',
                        re.sub(r'(set\s+"VER=)([\d.]+)(")', r'\g<1>1.0.0\g<3>',
                               read(ws, 'scripts/push-clawhub.bat'), count=1)))

inject(12, 'push-skillhub.bat 注释里的版本落后于技能基准',
       ['scripts/push-skillhub.bat'],
       lambda ws: write(ws, 'scripts/push-skillhub.bat',
                        re.sub(r'(default\s+version\s*=\s*)([\d.]+)', r'\g<1>1.0.0',
                               read(ws, 'scripts/push-skillhub.bat'), count=1)))

# .bat 编码/行尾：踩过的坑——文件是 UTF-8 时 cmd.exe 把中文注释按 GBK 解释，
# 报「'xxx' 不是内部或外部命令」；行尾是 LF 时多行 ( ) 块被拆成独立命令。
inject(12, 'push-clawhub.bat 被写成 UTF-8（cmd.exe 会解析错乱）',
       ['scripts/push-clawhub.bat'],
       lambda ws: (ws / 'scripts/push-clawhub.bat').write_bytes(
           read(ws, 'scripts/push-clawhub.bat').encode('utf-8')))

inject(12, 'publish-all.bat 行尾是纯 LF（多行块会解析错乱）',
       ['publish-all.bat'],
       lambda ws: (ws / 'publish-all.bat').write_bytes(
           (ws / 'publish-all.bat').read_bytes().replace(b'\r\n', b'\n')))

legal(12, '.bat 为 GBK + CRLF 时不应被误报',
      ['scripts/push-skillhub.bat'],
      lambda ws: None, '正确的 .bat 形态（GBK 编码 + CRLF 行尾）必须通过')

# 13 产出一致性
inject(13, '不产用例表的技能声明「固定 9 列用例表」',
       [f'skills/{PLAIN}/SKILL.md'],
       lambda ws: mutate_json_meta(ws, PLAIN, 'output-format',
                                   lambda v: v.update(
                                       {'structure': '固定 9 列用例表：' + str(v.get('structure', ''))})))

# 14 关联 ID 前缀
#     注入时把 REQ-/SC- 一律换成 TC_：覆盖仓库里实际在用的冒号句式
def _bad_trace(ws):
    def fn(v):
        v['traceability'] = [re.sub(r'(REQ-|SC-)', 'TC_', t) for t in v['traceability']]
    mutate_json_meta(ws, T, 'output-format', fn)


inject(14, '关联需求 ID 误用 TC_ 前缀', [f'skills/{T}/SKILL.md'], _bad_trace)

# 15 references 登记
inject(15, 'references/ 新增文件但没登记进 metadata.references',
       [f'skills/{PLAIN}/references/brand-new.md'],
       lambda ws: write(ws, f'skills/{PLAIN}/references/brand-new.md',
                        '# 新文件\n\n这个文件没有登记进 metadata.references。\n'))

# —— 误报控制：以下内容形似违规但合规，门禁必须放过 ——
legal(1, '完整的 9 列 output-format JSON 不应被判非法',
      [f'skills/{PLAIN}/SKILL.md'],
      lambda ws: None, 'JSON 合法，结构不变')

legal(6, 'standards.md 里的 {模块缩写} 占位符应被正确识别为已定义前缀',
      ['docs/standards.md'],
      lambda ws: write(ws, 'docs/standards.md',
                       read(ws, 'docs/standards.md')
                       + '\n\n格式：`NEWPFX-{模块缩写}-{序号}`\n'),
      '新前缀声明进 standards.md 后应被 check 6 认可，不应反过来报 traceability 缺前缀')

legal(7, '清单标题叫「验收清单」也算有清单',
      [f'skills/{PLAIN}/SKILL.md'],
      lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                       re.sub(r'^##\s*(?:\d+\.\s*)?(?:交付前)?(?:检查清单|自检清单|自检).*$',
                              '## 验收清单\n\n- [ ] 这一项是交付前必须过的', read(ws, f'skills/{PLAIN}/SKILL.md'),
                              count=1, flags=re.M)),
      '「验收清单」是本项目入口技能在用的合规写法，正则不能只认「检查/自检清单」')

legal(10, '长度 >3 的泛化词不算过宽触发词',
      [f'skills/{PLAIN}/SKILL.md'],
      lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                       sub_frontmatter(read(ws, f'skills/{PLAIN}/SKILL.md'),
                                       'when-to-use', '用户说',
                                       '用户说\\"缺陷根因\\"、用户说')),
      '`设计`/`报告` 才是过宽的裸泛化词，`缺陷根因` 是有区分度的具体说法')

legal(11, '普通词做 target 不该被当 ID 前缀',
      ['evals/evals.json'],
      lambda ws: _legal_target(ws),
      'IDLIKE 要求 target 形如 `TC_`/`REQ-` 整串，`9列`/`CSV` 这类不该被误判')

legal(13, '技能目录里有真实 9 列用例表时不应报「声明与实际不符」',
      [f'skills/{PLAIN}/SKILL.md'],
      lambda ws: write(ws, f'skills/{PLAIN}/SKILL.md',
                       read(ws, f'skills/{PLAIN}/SKILL.md').rstrip() + '\n\n'
                       '## 产出示例\n\n'
                       '| 用例编号 | 测试类型 | 功能模块 | 测试标题 | 用例级别 | '
                       '预置条件 | 测试步骤 | 预期结果 | 风险等级 |\n'
                       '|---|---|---|---|---|---|---|---|---|\n'
                       '| TC_X_Y_001 | 功能 | A/登录 | 正常登录 | P0 | 已注册 | 输入账号密码 | 登录成功 | 中 |\n'),
      '声明 + 真实表头同时存在，check 13 应判为合规')

legal(14, '正确的 REQ-/SC- 关联 ID 不该被误判',
      [f'skills/{T}/SKILL.md'],
      lambda ws: mutate_json_meta(ws, T, 'output-format',
                                  lambda v: v['traceability'].append('需求带唯一ID（REQ-XXXX）')),
      'TC_ 出现在同一条 traceability 里但用于用例编号，不该误伤')

# —— 发布链路：ClawHub 侧不能带 metadata.slug（SkillHub 独有字段）——
# 发布暂存逻辑在 scripts/stage_for_publish.py。两个平台的要求正好相反：
#   SkillHub 需要顶层 displayName（它的解析器不认嵌套键，键名还必须是 displayName）
#   ClawHub 不能有 metadata.slug
# 两边都要验证：暂存副本满足各自要求，且源文件保持规范形态不被改动。
def _stage_check(ws: Path) -> str:
    """跑两遍发布暂存，校验各平台的 frontmatter 要求都满足"""
    import yaml
    out = []
    for platform, check in (
        ('clawhub', lambda h: not re.search(r'^[ \t]+slug[ \t]*:', h, re.M)),
        ('skillhub', lambda h: bool(re.search(r'^displayName[ \t]*:[ \t]*\S', h, re.M))),
    ):
        r = subprocess.run(
            [sys.executable, 'scripts/stage_for_publish.py', '--all',
             '--platform', platform, '--out', f'.stage-selftest/{platform}'],
            cwd=str(ws), capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            out.append(f'{platform} 暂存失败：{r.stderr[:150]}')
            continue
        root = ws / '.stage-selftest' / platform
        dirs = [d for d in root.iterdir() if (d / 'SKILL.md').exists()]
        if len(dirs) != 49:
            out.append(f'{platform} 暂存了 {len(dirs)} 个技能，应为 49')
            continue
        bad = []
        for d in dirs:
            text = (d / 'SKILL.md').read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
            if not m:
                bad.append(f'{d.name}: frontmatter 结构坏了')
                continue
            if not check(m.group(1)):
                bad.append(f'{d.name}: 不满足 {platform} 的字段要求')
                continue
            try:
                fm = yaml.safe_load(text.split('\n---\n')[0]) or {}
            except Exception as exc:  # noqa: BLE001
                bad.append(f'{d.name}: YAML 解析失败 {exc}')
                continue
            if not isinstance(fm.get('metadata'), dict):
                bad.append(f'{d.name}: metadata 不是映射')
        if bad:
            out.append(f'{platform}: {bad[:4]}')
    shutil.rmtree(ws / '.stage-selftest', ignore_errors=True)
    return '；'.join(out)


LEGAL.append((
    0, '两个平台的发布暂存副本都满足各自 frontmatter 要求',
    [f'skills/{T}/SKILL.md', 'scripts/stage_for_publish.py'],
    _stage_check, 'SkillHub 要顶层 displayName、ClawHub 不要 metadata.slug；源文件保持规范形态'))


def _legal_target(ws):
    p = 'evals/evals.json'
    d = json.loads(read(ws, p))
    d['evals'][0]['assertions'].append(
        {'type': 'content_match', 'name': '合法目标', 'target': '9列', 'value': 'x'})
    write(ws, p, json.dumps(d, ensure_ascii=False, indent=2))


# ---------- 跑 ----------
def main():
    argv = sys.argv[1:]
    verbose = '-v' in argv
    keep = '--keep' in argv
    only = None
    if '--check' in argv:
        only = int(argv[argv.index('--check') + 1])

    ws = Path(tempfile.mkdtemp(prefix='gate-selftest-')) / 'repo'
    ws.mkdir(parents=True)
    stage(ws)
    if keep:
        print(f'（--keep：临时工作区保留在 {ws}）')
    results = []

    def record(cid, kind, name, ok, detail=''):
        results.append((cid, kind, name, ok, detail))

    try:
        # 基线：干净仓库硬问题必须为 0
        base, raw = run_check(ws)
        hard = json.loads(subprocess.run(
            [sys.executable, 'scripts/integrity_check.py', '--json'],
            cwd=str(ws), capture_output=True, text=True, encoding='utf-8'
        ).stdout)['hard']
        if hard != 0:
            record(0, 'BASE', '干净仓库硬问题为 0', False,
                   f'实际 {hard} 项：' + '; '.join(
                       f"#{c['id']}×{c['count']}" for c in base.values() if c['count']))
        else:
            record(0, 'BASE', '干净仓库硬问题为 0', True)

        # INJECT：该报的必须报
        for cid, name, files, mutate in INJECT:
            if only and cid != only:
                continue
            restore(ws, files)
            mutate(ws)
            res, _ = run_check(ws)
            got = res.get(cid, {}).get('count', 0)
            if got > 0:
                record(cid, 'INJECT', name, True)
            else:
                other = ' | '.join(f"#{c}:{res[c]['items'][:1]}"
                                   for c in res if res[c]['count'])
                shape = ' ； '.join(fm_shape(ws, f) for f in files if f.endswith('SKILL.md'))
                skill = next((f.split('/')[1] for f in files if f.endswith('SKILL.md')), None)
                probe = raw_meta(ws, skill, 'output-format') if skill else ''
                record(cid, 'INJECT', name, False,
                       f'注入后检查项 {cid} 仍为 0 项｜其他项 {other or "无"}\n'
                       f'         {shape}\n'
                       f'         skillmeta 读到的 metadata.output-format = {probe}')
            restore(ws, files)

        # LEGAL：不该报的不许报
        for cid, name, files, mutate, why in LEGAL:
            if only and cid != only:
                continue
            restore(ws, files)
            msg = mutate(ws)          # 返回非空字符串 = 该用例自己的失败原因
            res, _ = run_check(ws)
            got = res.get(cid, {}).get('count', 0) if cid else 0
            if got == 0 and not msg:
                record(cid, 'LEGAL', name, True)
            else:
                why_txt = f'｜{why}' if why else ''
                got_txt = f'合规内容被误报 {got} 项：{res[cid]["items"][:2]}' if got else ''
                record(cid, 'LEGAL', name, False,
                       f'{got_txt}｜{msg or ""}{why_txt}'.rstrip('｜'))
            restore(ws, files)
    finally:
        if not keep:
            shutil.rmtree(ws.parent, ignore_errors=True)

    # 报告
    print('=' * 92)
    print('门禁双向自测')
    print('=' * 92)
    print(f"{'':2} {'#':>2}  {'方向':<7} {'结果':<5} 用例")
    print('-' * 92)
    for cid, kind, name, ok, detail in results:
        mark = '✅' if ok else '❌'
        print(f'   {cid:>2}  {kind:<7} {mark:<4} {name}')
        if not ok and detail:
            print(f'        → {detail}')
    passed = sum(1 for r in results if r[3])
    failed = [r for r in results if not r[3]]

    by_dir = {}
    for r in results:
        by_dir.setdefault(r[1], [0, 0])
        by_dir[r[1]][0 if r[3] else 1] += 1
    print()
    for k in ('BASE', 'INJECT', 'LEGAL'):
        if k in by_dir:
            ok, bad = by_dir[k]
            label = {'BASE': '基线', 'INJECT': '注入(该报)', 'LEGAL': '合规(不该报)'}[k]
            print(f'  {label:<16} 通过 {ok} / 失败 {bad}')
    print(f'\n合计：{passed} 通过 / {len(failed)} 失败')
    if failed:
        print('\n失败项：')
        for cid, kind, name, _, detail in failed:
            print(f'  ❌ 检查项 {cid} [{kind}] {name}')
            if detail:
                print(f'       {detail}')
    print('=' * 92)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
