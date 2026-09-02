#!/usr/bin/env python3
"""
校验根工作流⚠️标注与 enforcement.md 一致 + ID 规范与子技能 traceability 一致。
用法：python scripts/validate_standards.py
"""
import re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def check_workflow_warnings():
    """入口工作流 SKILL.md 工作流表里的⚠️不得跳过标注，应与 enforcement.md 的强制步骤一致。"""
    root = (ROOT / 'skills' / 'qa-test-skills' / 'SKILL.md').read_text(encoding='utf-8').replace('\r\n', '\n')
    enf = (ROOT / 'skills' / 'qa-test-skills' / 'references' / 'enforcement.md').read_text(encoding='utf-8').replace('\r\n', '\n')
    # enforcement.md 声明不得跳过步骤 7（提示词）和 8（输出评审）
    must_not_skip = set(re.findall(r'步骤(\d+)', enf))
    # 根 SKILL.md 工作流表里的⚠️标注
    flagged = set(re.findall(r'第(\d+)步.*⚠️', root))
    issues = []
    for step in must_not_skip:
        if step not in flagged:
            issues.append(f"enforcement.md 声明步骤{step}不得跳过，但根 SKILL.md 工作流表未标⚠️")
    return issues

def check_id_standards():
    """docs/standards.md 定义的 ID 前缀应与子技能 traceability 声明一致。"""
    std = (ROOT / 'docs' / 'standards.md').read_text(encoding='utf-8').replace('\r\n', '\n')
    declared_prefixes = set(re.findall(r'([A-Z]+)-\{模块缩写\}', std))
    # 子技能 traceability 里声明的 ID 前缀
    used = set()
    for d in sorted((ROOT / 'skills').glob('qa-*')):
        f = d / 'SKILL.md'
        txt = f.read_text(encoding='utf-8').replace('\r\n', '\n')
        m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
        if not m: continue
        for tr in re.finditer(r'唯一ID（([A-Z]+)-XXXX', m.group(1)):
            used.add(tr.group(1))
    missing = used - declared_prefixes
    issues = [f"子技能用 ID 前缀 {p} 但 docs/standards.md 未定义" for p in missing]
    return issues

def main():
    issues = check_workflow_warnings() + check_id_standards()
    if not issues:
        print("✅ 标准一致性校验全过")
    else:
        print(f"❌ {len(issues)} 项不一致:")
        for i in issues: print(f"  - {i}")
    sys.exit(1 if issues else 0)

if __name__ == '__main__':
    main()
