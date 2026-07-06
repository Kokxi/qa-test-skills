#!/usr/bin/env python3
"""完整性一致性检查"""
import pathlib, re, json, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
skills = sorted((ROOT/'skills').glob('qa-*'))
issues = []

# 1. frontmatter 12 字段 + traceability
required = ['name','version','description','when_to_use','allowed-tools',
           'related_skills','input_format','output_format','categories',
           'depth_requirement_quantification','error_recovery_guidance']
fm_issues = []
for d in skills:
    f = d/'SKILL.md'
    fm = re.match(r'^---\n(.*?)\n---\n', f.read_text(encoding='utf-8').replace('\r\n','\n'), re.S)
    if not fm: fm_issues.append(f"{d.name}: 无 frontmatter"); continue
    fm = fm.group(1)
    for fld in required:
        if not re.search(r'^'+re.escape(fld)+r':', fm, re.M):
            fm_issues.append(f"{d.name}: 缺 {fld}")
    if not re.search(r'^\s*traceability:', fm, re.M):
        fm_issues.append(f"{d.name}: 缺 traceability")

# 2. name vs 目录名
name_issues = []
for d in skills:
    fm = re.match(r'^---\n(.*?)\n---\n', (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
    nm = re.search(r'^name:\s*([^"\'\n]+)', fm, re.M)
    if nm and nm.group(1).strip() != d.name:
        name_issues.append((d.name, nm.group(1).strip()))

# 3. version 全 1.6.0
ver_issues = []
for d in skills:
    fm = re.match(r'^---\n(.*?)\n---\n', (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
    vm = re.search(r'^version:\s*([^"\'\n]+)', fm, re.M)
    if vm and vm.group(1).strip() != '1.6.0':
        ver_issues.append((d.name, vm.group(1).strip()))
rfm = re.match(r'^---\n(.*?)\n---\n', (ROOT/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
rvm = re.search(r'^version:\s*([^"\'\n]+)', rfm, re.M)
if rvm and rvm.group(1).strip() != '1.6.0':
    ver_issues.append(('ROOT', rvm.group(1).strip()))

# 4. related_skills 悬空 + 对称性
all_names = set(d.name for d in skills) | {'qa-test-skills'}  # 根入口技能也算合法引用
ref_issues = []
for d in skills:
    fm = re.match(r'^---\n(.*?)\n---\n', (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
    for m in re.finditer(r'^\s+-\s+(qa-[\w-]+)', fm, re.M):
        if m.group(1) not in all_names:
            ref_issues.append(f"{d.name}: 引用不存在的 {m.group(1)}")
dep = subprocess.run(['python','scripts/validate_deps.py'], capture_output=True, text=True, encoding='utf-8', cwd=str(ROOT))
dep_ok = '✅ 没有警告' in dep.stdout and '✅ 没有引用错误' in dep.stdout

# 5. references/ 引用悬空
ref_file_issues = []
for d in skills:
    txt = (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n')
    fm = re.match(r'^---\n(.*?)\n---\n', txt, re.S).group(1)
    for m in re.finditer(r'^\s+-\s+references/([\w.-]+)', fm, re.M):
        if not (d/'references'/m.group(1)).exists():
            ref_file_issues.append(f"{d.name}: references/{m.group(1)} 不存在")
    body = txt.split('---\n',2)[-1]
    for m in re.finditer(r'references/([\w.-]+\.md)', body):
        ref = m.group(1)
        if not (d/'references'/ref).exists() and not (ROOT/'references'/ref).exists():
            ref_file_issues.append(f"{d.name}: 正文引用 references/{ref} 不存在")
for m in re.finditer(r'references/([\w.-]+\.md)', (ROOT/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n')):
    if not (ROOT/m.group(0)).exists():
        ref_file_issues.append(f"ROOT: {m.group(0)} 不存在")

# 6. ID 规范一致性
std = (ROOT/'docs'/'standards.md').read_text(encoding='utf-8').replace('\r\n','\n')
declared = set(re.findall(r'([A-Z]+)-\{模块缩写\}', std))
used = set()
for d in skills:
    fm = re.match(r'^---\n(.*?)\n---\n', (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
    for tr in re.finditer(r'唯一ID（([A-Z]+)-XXXX', fm):
        used.add(tr.group(1))
missing_in_std = used - declared

# 7. 正文结构（检查清单）
struct_issues = []
for d in skills:
    body = (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n').split('---\n',2)[-1]
    if not re.search(r'^##\s*检查清单', body, re.M):
        struct_issues.append(d.name)

# 8. UTF-8 BOM
bom_issues = []
for d in skills:
    if (d/'SKILL.md').read_bytes().startswith(b'\xef\xbb\xbf'):
        bom_issues.append(d.name)
for f in [ROOT/'SKILL.md'] + list((ROOT/'scripts').glob('*.py')) + list((ROOT/'evals').glob('*.json')):
    if f.read_bytes().startswith(b'\xef\xbb\xbf'):
        bom_issues.append(str(f.relative_to(ROOT)))

# 9. evals.json 结构
data = json.load(open(ROOT/'evals'/'evals.json', encoding='utf-8'))
eval_issues = []
ids = set()
for e in data['evals']:
    eid = e.get('id')
    if eid in ids: eval_issues.append(f"eval id {eid} 重复")
    ids.add(eid)
    for fld in ['prompt','expected_output','assertions']:
        if fld not in e: eval_issues.append(f"eval#{eid}: 缺 {fld}")
    for a in e.get('assertions',[]):
        if 'type' not in a or 'name' not in a:
            eval_issues.append(f"eval#{eid}: assertion 缺 type/name")

# 10. 安全审计残留
risky = []
for d in skills:
    fm = re.match(r'^---\n(.*?)\n---\n', (d/'SKILL.md').read_text(encoding='utf-8').replace('\r\n','\n'), re.S).group(1)
    wtu = re.search(r'^when_to_use:\s*(.*?)(?:\n\S|\n---)', fm, re.S | re.M)
    if not wtu: continue
    for kw in re.findall(r'"([^"]+)"', wtu.group(1)):
        if len(kw) <= 3 and kw in ['测试','分析','评估','评审','管理','设计','策略','报告','复盘']:
            risky.append((d.name, kw))
sensitive = ['qa-boundary-deep-dive','qa-bug-lifecycle','qa-bug-reporting','qa-bug-root-cause-analysis',
             'qa-combination-strategy','qa-critical-thinking','qa-exploratory-testing','qa-input-validation',
             'qa-question-framework','qa-req-deconstruction','qa-scenario-tree','qa-stakeholder-communication',
             'qa-test-automation-arch']
missing_warn = sum(1 for d in sensitive if '⚠️ 安全警告' not in ((ROOT/'skills')/d/'SKILL.md').read_text(encoding='utf-8'))

# 报告
print("=== 1. frontmatter 12 字段+traceability ===")
print(f"  {'✅' if not fm_issues else '❌'} {len(fm_issues)} 项")
for i in fm_issues[:5]: print(f"    {i}")
print(f"\n=== 2. name vs 目录名 ===")
print(f"  {'✅' if not name_issues else '❌'} {len(name_issues)} 项")
print(f"\n=== 3. version 一致性 ===")
print(f"  {'✅' if not ver_issues else '❌'} {len(ver_issues)} 项")
print(f"\n=== 4. related_skills 悬空+对称 ===")
print(f"  {'✅' if not ref_issues and dep_ok else '❌'} 悬空{len(ref_issues)} 对称{'OK' if dep_ok else 'FAIL'}")
print(f"\n=== 5. references/ 引用悬空 ===")
print(f"  {'✅' if not ref_file_issues else '❌'} {len(ref_file_issues)} 项")
for i in ref_file_issues[:5]: print(f"    {i}")
print(f"\n=== 6. ID 规范一致性 ===")
print(f"  {'✅' if not missing_in_std else '❌'} standards定义{len(declared)} 用{len(used)} 缺{sorted(missing_in_std)[:5]}")
print(f"\n=== 7. 正文检查清单 ===")
print(f"  {'✅' if not struct_issues else '⚠️'} {len(struct_issues)} 缺检查清单")
for i in struct_issues[:5]: print(f"    {i}")
print(f"\n=== 8. UTF-8 BOM ===")
print(f"  {'✅' if not bom_issues else '❌'} {len(bom_issues)} 项")
print(f"\n=== 9. evals.json 结构 ===")
print(f"  {'✅' if not eval_issues else '❌'} {len(data['evals'])} eval, {len(eval_issues)} 项")
print(f"\n=== 10. 安全审计残留 ===")
print(f"  {'✅' if not risky else '❌'} 裸泛化词: {len(risky)}")
print(f"  {'✅' if missing_warn==0 else '❌'} Missing Warnings: {missing_warn}/13")

total = len(fm_issues)+len(name_issues)+len(ver_issues)+len(ref_issues)+len(ref_file_issues)+len(missing_in_std)+len(bom_issues)+len(eval_issues)+len(risky)+missing_warn
print(f"\n{'='*50}")
print(f"汇总: ❌{total} 项硬问题 + ⚠️{len(struct_issues)} 项软问题")
print(f"{'='*50}")
