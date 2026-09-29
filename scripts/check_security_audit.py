#!/usr/bin/env python3
"""
自动化 ClawHub security audit 检查（替代 CLAUDE.md 的手动 4 步工作流）。
用法：
  python scripts/check_security_audit.py              # 检查所有技能
  python scripts/check_security_audit.py qa-api-testing  # 检查单个技能

说明：
- ClawHub 暂无公开 audit API，此脚本先做本地静态预检（Vague Triggers / Missing Warnings），
  再生成需人工访问的 audit URL 清单，避免逐个手翻。
- 输出：每技能一行结论 + 汇总需人工复核的 URL 列表。
"""
import re, sys, pathlib, json

import skillmeta

ROOT = pathlib.Path(__file__).resolve().parent.parent
SLUG = "kokxi"  # ClawHub user slug

# Vague Triggers 检测：when_to_use 里跨技能重叠的关键词
SHARED_KEYWORDS = {
    "左移": ["qa-shift-left"],
    "右移": ["qa-shift-right"],
    "需求评审": ["qa-requirement-review", "qa-shift-left"],
    "安全测试": ["qa-specialized-testing", "qa-api-testing", "qa-mobile-testing"],
    "自动化测试": ["qa-ci-cd-testing", "qa-test-automation-arch"],
}

def check_vague_triggers(skill_name):
    """检测 when_to_use 里的关键词是否与其他技能独占。"""
    issues = []
    wtu = skillmeta.when_to_use(skill_name)
    if not wtu:
        return ["when_to_use missing (metadata.when-to-use)"]
    for kw, owners in SHARED_KEYWORDS.items():
        if kw in wtu and skill_name not in owners:
            issues.append(f"Vague Trigger: '{kw}' 也被 {owners} 声明，建议限定或删除")
    return issues

def check_missing_warnings(body):
    """检测涉险操作（删除/重置/发布）是否有 ⚠️ 警告。"""
    issues = []
    risky = re.search(r'(删除|重置|发布|回滚|drop|reset|publish|rollback)', body, re.I)
    has_warn = '⚠️' in body or '安全警告' in body
    if risky and not has_warn:
        issues.append("Missing User Warnings: 涉险操作无 ⚠️ 警告")
    return issues

def main():
    args = sys.argv[1:]
    skills_dir = ROOT / 'skills'
    targets = [args[0]] if args else sorted(p.name for p in skills_dir.glob('qa-*'))
    results = []
    manual_urls = []
    for name in targets:
        d = skills_dir / name
        if not (d / 'SKILL.md').exists(): continue
        body = skillmeta.load(name)['body']
        issues = check_vague_triggers(name) + check_missing_warnings(body)
        status = '✅ pass' if not issues else '❌ ' + '; '.join(issues)
        results.append((name, status))
        manual_urls.append(f"https://clawhub.ai/{SLUG}/skills/{name}/security-audit")
    print("=== ClawHub Security Audit 本地预检 ===")
    for name, status in results:
        print(f"  {status.split(';')[0]:<8} {name}: {status.split(';',1)[1] if ';' in status else ''}")
    fail = sum(1 for _, s in results if s.startswith('❌'))
    print(f"\n汇总: {len(results)} 技能, {fail} 本地预检失败")
    print(f"\n需人工复核的 ClawHub audit URL（{len(manual_urls)} 个）:")
    for u in manual_urls[:5]:
        print(f"  {u}")
    if len(manual_urls) > 5:
        print(f"  ... 其余 {len(manual_urls)-5} 个 URL 同理")

if __name__ == '__main__':
    main()
