"""浅层组轻量改造工具：把超长章节原文下沉到 references/，并在 SKILL.md 补加载时机地图。

设计原则（对照 docs/skill-content-layout.md）：
- 大节内容**原文搬运**到 references/，不做删改（浅层组不做深度重写）
- SKILL.md 保留：核心原则 / 决策表 / 硬约束 / 加载时机地图 / 交付自检
- 补 loading map 是强制的——没有它就等于把内容藏起来

用法
----
  python scripts/light_split.py qa-bug-root-cause-analysis
  python scripts/light_split.py --plan qa-bug-root-cause-analysis   # 只看会拆什么
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skillmeta

# 逐个技能：大节标题 -> (references 文件名, references 标题, 加载时机说明, SKILL.md 里替换成的一行指针)
PLAN = {
    'qa-bug-root-cause-analysis': {
        'section': '症状分类与根因映射',
        'ref': 'references/symptom-rca-map.md',
        'ref_title': '# 症状分类与根因映射',
        'ref_note': '> 本文是 `qa-bug-root-cause-analysis` 的**症状→根因对照表**。'
                    '拿到线上/测试发现的具体症状后查对应根因时读本文；\n'
                    '只想了解 5Why/鱼骨图等方法怎么用时不必读。',
        'loadmap': ('定位到具体症状后，查对应的根因与验证手段', 'ref'),
    },
    'qa-question-framework': {
        'section': '四大提问场景',
        'ref': 'references/question-scenarios.md',
        'ref_title': '# 四大提问场景提问模板',
        'ref_note': '> 本文是 `qa-question-framework` 的**四类提问模板库**。'
                    '确定要问哪一类问题时读对应小节；\n'
                    '只需要提问框架与原则时不必读。',
        'loadmap': ('确定提问类别后，取对应模板', 'ref'),
    },
    'qa-ai-prompt-strategy': {
        'section': '六大提示词模式',
        'ref': 'references/prompt-patterns.md',
        'ref_title': '# 六大提示词模式模板',
        'ref_note': '> 本文是 `qa-ai-prompt-strategy` 的**六种提示词模式模板**。'
                    '选定模式后取对应模板填写；\n'
                    '只需要选模式的判断依据时不必读。',
        'loadmap': ('选定提示词模式后，取对应模板', 'ref'),
    },
    'qa-testability-advocacy': {
        'section': '可测试性检查维度',
        'ref': 'references/testability-dimensions.md',
        'ref_title': '# 可测试性五维检查详表',
        'ref_note': '> 本文是 `qa-testability-advocacy` 的**五维检查详表**。'
                    '逐维打分或需要举例时读本文；\n'
                    '只需要评估框架与推动策略时不必读。',
        'loadmap': ('逐维打分或找改进项时，取五维详表', 'ref'),
    },
    'qa-domain-modeling': {
        'section': '三种建模视图',
        'ref': 'references/modeling-views.md',
        'ref_title': '# 三种建模视图详解',
        'ref_note': '> 本文是 `qa-domain-modeling` 的**状态机/数据流图/服务依赖图**三视图详解。'
                    '选视图并绘制时读本文；\n'
                    '只需要选型判断时不必读。',
        'loadmap': ('选定视图后，取对应画法与要素', 'ref'),
    },
    'qa-retrospective': {
        'section': '复盘五步法',
        'ref': 'references/five-steps.md',
        'ref_title': '# 复盘五步法详解',
        'ref_note': '> 本文是 `qa-retrospective` 的**五步法详解**。'
                    '需要方法细节或推进要点时读本文；\n'
                    '只需要复盘报告模板时不必读。',
        'loadmap': ('需要五步法的方法细节时，取对应小节', 'ref'),
    },
    'qa-bug-reporting': {
        'section': 'Bug报告黄金结构',
        'ref': 'references/bug-report-structure.md',
        'ref_title': '# 缺陷报告黄金结构',
        'ref_note': '> 本文是 `qa-bug-reporting` 的**七段式报告结构详解**。'
                    '写缺陷报告、取各段写法时读本文；\n'
                    '只需要报告模板时不必读。',
        'loadmap': ('写缺陷报告时，取七段式结构与各段写法', 'ref'),
    },
    'qa-team-coaching': {
        'section': '四种赋能方式',
        'ref': 'references/coaching-methods.md',
        'ref_title': '# 四种赋能方式详解',
        'ref_note': '> 本文是 `qa-team-coaching` 的**四种赋能方式详解**。'
                    '选赋能方式或需要落地做法时读本文；\n'
                    '只需要赋能与培训的原则时不必读。',
        'loadmap': ('选定赋能方式后，取对应做法', 'ref'),
    },
    'qa-test-estimation': {
        'section': '估算方法',
        'ref': 'references/estimation-methods.md',
        'ref_title': '# 测试工作量估算方法',
        'ref_note': '> 本文是 `qa-test-estimation` 的**估算方法详解**。'
                    '做估算或需要复杂度分级依据时读本文；\n'
                    '只需要估算报告结构时不必读。',
        'loadmap': ('做估算或查复杂度分级依据时，取对应方法', 'ref'),
    },
    'qa-critical-thinking': {
        'section': '思维练习',
        'ref': 'references/thinking-exercises.md',
        'ref_title': '# 批判性思维练习集',
        'ref_note': '> 本文是 `qa-critical-thinking` 的**思维练习集**。'
                    '拿不准还有什么可质疑时读本文找切入点；\n'
                    '只需要质疑框架与问法时不必读。',
        'loadmap': ('想不出新的质疑角度时，取练习集找切入点', 'ref'),
    },
    'qa-quality-metrics': {
        'section': '四类度量指标',
        'ref': 'references/metrics-dimensions.md',
        'ref_title': '# 四类质量度量指标详解',
        'ref_note': '> 本文是 `qa-quality-metrics` 的**四类度量指标详解**。'
                    '选指标、算指标或找埋点来源时读本文；\n'
                    '只需要度量框架与看板设计原则时不必读。',
        'loadmap': ('选指标、算指标或查数据来源时，取四类详表', 'ref'),
    },
    'qa-mobile-testing': {
        'section': '移动端测试检查清单',
        'ref': 'references/mobile-checklist.md',
        'ref_title': '# 移动端测试检查清单（全平台）',
        'ref_note': '> 本文是 `qa-mobile-testing` 的**跨平台检查清单**。'
                    '需要通用移动端检查项时读本文；\n'
                    '只测单一平台时直接读该平台的 `references/platform-*.md`，不必读本文。',
        'loadmap': ('需要跨平台通用检查项时，取全平台清单', 'ref'),
    },
    'qa-output-validation': {
        'section': '验证维度',
        'ref': 'references/validation-dimensions.md',
        'ref_title': '# 验证维度详解',
        'ref_note': '> 本文是 `qa-output-validation` 的**验证维度详解**。'
                    '逐维做防幻觉校验时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('逐维做防幻觉校验时', 'ref'),
    },
    'qa-tech-debt-management': {
        'section': '债务治理',
        'ref': 'references/debt-governance.md',
        'ref_title': '# 测试技术债治理详解',
        'ref_note': '> 本文是 `qa-tech-debt-management` 的**测试技术债治理详解**。'
                    '识别/评估/偿还测试债时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('识别/评估/偿还测试债时', 'ref'),
    },
    'qa-test-env-data': {
        'section': '测试数据管理',
        'ref': 'references/data-management.md',
        'ref_title': '# 测试数据管理详解',
        'ref_note': '> 本文是 `qa-test-env-data` 的**测试数据管理详解**。'
                    '准备、脱敏、清理测试数据时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('准备、脱敏、清理测试数据时', 'ref'),
    },
    'qa-tech-selection': {
        'section': '选型框架',
        'ref': 'references/selection-framework.md',
        'ref_title': '# 测试工具选型框架详解',
        'ref_note': '> 本文是 `qa-tech-selection` 的**测试工具选型框架详解**。'
                    '做工具选型评估时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('做工具选型评估时', 'ref'),
    },
    'qa-specialized-testing': {
        'section': '维度1：性能测试',
        'ref': 'references/performance-depth.md',
        'ref_title': '# 性能测试维度详解',
        'ref_note': '> 本文是 `qa-specialized-testing` 的**性能测试维度详解**。'
                    '做性能测试专项时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('做性能测试专项时', 'ref'),
    },
    'qa-regression-testing': {
        'section': '回归用例筛选策略',
        'ref': 'references/regression-selection.md',
        'ref_title': '# 回归用例筛选策略详解',
        'ref_note': '> 本文是 `qa-regression-testing` 的**回归用例筛选策略详解**。'
                    '确定"回归哪些"时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('确定"回归哪些"时', 'ref'),
    },
    'qa-ci-cd-testing': {
        'section': 'CI/CD 流水线设计',
        'ref': 'references/pipeline-design.md',
        'ref_title': '# CI/CD 流水线设计详解',
        'ref_note': '> 本文是 `qa-ci-cd-testing` 的**CI/CD 流水线设计详解**。'
                    '设计流水线分层卡点时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计流水线分层卡点时', 'ref'),
    },
    'qa-code-review-for-test': {
        'section': '测试视角CR四看',
        'ref': 'references/cr-lens.md',
        'ref_title': '# 测试视角 CR 四看详解',
        'ref_note': '> 本文是 `qa-code-review-for-test` 的**测试视角 CR 四看详解**。'
                    '从测试角度评审代码变更时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('从测试角度评审代码变更时', 'ref'),
    },
    'qa-shift-left': {
        'section': '左移阶段',
        'ref': 'references/shift-left-stages.md',
        'ref_title': '# 测试左移三阶段详解',
        'ref_note': '> 本文是 `qa-shift-left` 的**测试左移三阶段详解**。'
                    '介入需求/设计/开发阶段时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('介入需求/设计/开发阶段时', 'ref'),
    },
    'qa-test-automation-arch': {
        'section': '分层架构设计',
        'ref': 'references/layered-architecture.md',
        'ref_title': '# 测试分层架构设计详解',
        'ref_note': '> 本文是 `qa-test-automation-arch` 的**测试分层架构设计详解**。'
                    '设计自动化框架分层时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计自动化框架分层时', 'ref'),
    },
    'qa-combination-strategy': {
        'section': '三种简化策略',
        'ref': 'references/reduction-strategies.md',
        'ref_title': '# 组合爆炸简化三策略详解',
        'ref_note': '> 本文是 `qa-combination-strategy` 的**组合爆炸简化三策略详解**。'
                    '设计 Pairwise/正交/风险加权时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计 Pairwise/正交/风险加权时', 'ref'),
    },
    'qa-bug-lifecycle': {
        'section': '缺陷分析',
        'ref': 'references/defect-analysis.md',
        'ref_title': '# 缺陷分析与度量详解',
        'ref_note': '> 本文是 `qa-bug-lifecycle` 的**缺陷分析与度量详解**。'
                    '做缺陷趋势/密度分析时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('做缺陷趋势/密度分析时', 'ref'),
    },
    'qa-test-leadership': {
        'section': '绩效评估',
        'ref': 'references/performance-review.md',
        'ref_title': '# 团队绩效评估详解',
        'ref_note': '> 本文是 `qa-test-leadership` 的**团队绩效评估详解**。'
                    '做绩效评估与能力模型时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('做绩效评估与能力模型时', 'ref'),
    },
    'qa-exploratory-testing': {
        'section': '漫游测试方法',
        'ref': 'references/charter-methods.md',
        'ref_title': '# 探索式漫游方法详解',
        'ref_note': '> 本文是 `qa-exploratory-testing` 的**探索式漫游方法详解**。'
                    '设计 charter、选漫游手法时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计 charter、选漫游手法时', 'ref'),
    },
    'qa-state-transition': {
        'section': '测试用例设计',
        'ref': 'references/transition-cases.md',
        'ref_title': '# 状态转换用例设计详解',
        'ref_note': '> 本文是 `qa-state-transition` 的**状态转换用例设计详解**。'
                    '设计合法/非法/临界/并发转换用例时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计合法/非法/临界/并发转换用例时', 'ref'),
    },
    'qa-test-data-engineering': {
        'section': '数据脱敏',
        'ref': 'references/data-masking.md',
        'ref_title': '# 测试数据脱敏详解',
        'ref_note': '> 本文是 `qa-test-data-engineering` 的**测试数据脱敏详解**。'
                    '做脱敏规则与实现时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('做脱敏规则与实现时', 'ref'),
    },
    'qa-expert-review': {
        'section': '元学习机制',
        'ref': 'references/meta-learning.md',
        'ref_title': '# 评审反馈元学习机制详解',
        'ref_note': '> 本文是 `qa-expert-review` 的**评审反馈元学习机制详解**。'
                    '把评审反馈沉淀为可复用资产时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('把评审反馈沉淀为可复用资产时', 'ref'),
    },
    'qa-release-risk-governance': {
        'section': '灰度策略设计',
        'ref': 'references/canary-rollout.md',
        'ref_title': '# 灰度发布与回滚策略详解',
        'ref_note': '> 本文是 `qa-release-risk-governance` 的**灰度发布与回滚策略详解**。'
                    '设计灰度放量阶梯与回滚阈值时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('设计灰度放量阶梯与回滚阈值时', 'ref'),
    },
    'qa-stakeholder-communication': {
        'section': '三类沟通模式',
        'ref': 'references/comms-patterns.md',
        'ref_title': '# 三类沟通模式详解',
        'ref_note': '> 本文是 `qa-stakeholder-communication` 的**三类沟通模式详解**。'
                    '按受众选沟通话术时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('按受众选沟通话术时', 'ref'),
    },
    'qa-input-validation': {
        'section': '输出格式',
        'ref': 'references/output-formats.md',
        'ref_title': '# 需求输入校验与输出格式详解',
        'ref_note': '> 本文是 `qa-input-validation` 的**需求输入校验与输出格式详解**。'
                    '校验输入完整性或需要输出格式时读本文；\n'
                    '其余部分留在 SKILL.md，不必读本文。',
        'loadmap': ('校验输入完整性或需要输出格式时', 'ref'),
    },
}


def do(name: str, plan_only: bool) -> None:
    cfg = PLAN.get(name)
    if not cfg:
        print(f'❌ {name}: 未登记改造计划')
        sys.exit(1)
    d = Path('skills') / name
    p = d / 'SKILL.md'
    raw = p.read_text(encoding='utf-8')
    body = skillmeta.load(name)['body']

    # 定位大节：从 "## <section>" 到下一个 "## " 之前
    m = re.search(rf'^##\s+{re.escape(cfg["section"])}\s*$(.*?)(?=^##\s|\Z)',
                  body, re.M | re.S)
    if not m:
        print(f'❌ {name}: 找不到章节「{cfg["section"]}」')
        sys.exit(1)
    section_body = m.group(1).rstrip('\n')
    n_lines = len(m.group(0).splitlines())
    print(f'  {name}: 章节「{cfg["section"]}」{n_lines} 行 → {cfg["ref"]}')
    if plan_only:
        return

    # 1. 写 references
    ref_path = d / cfg['ref']
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(
        f"{cfg['ref_title']}\n\n{cfg['ref_note']}\n\n---\n\n{section_body}\n",
        encoding='utf-8', newline='\n')

    # 2. SKILL.md 里把该节替换为指针 + 加载时机地图
    load_line = cfg['loadmap'][0]
    replacement = (
        f"## 加载时机\n\n"
        f"| 什么时候读 | 读哪个 |\n|-----------|--------|\n"
        f"| {load_line} | [`{cfg['ref']}`]({cfg['ref']}) |\n\n"
        f"> `{cfg['section']}`的完整内容已下沉至 `{cfg['ref']}`，避免每次触发都占用上下文。\n"
    )
    new_body = body[:m.start()] + replacement + '\n' + body[m.end():]

    # 3. 写回 SKILL.md（保留 frontmatter 原样）
    fm_text = re.match(r'^(---\n.*?\n---\n)', raw, re.S).group(1)
    p.write_text(fm_text + new_body, encoding='utf-8', newline='\n')

    # 4. 登记 metadata.references
    skillmeta.load.cache_clear()
    real = {f'references/{x.name}' for x in (d / 'references').glob('*') if x.is_file()}
    real |= {f'assets/{x.name}' for x in (d / 'assets').glob('*') if x.is_file()} \
        if (d / 'assets').is_dir() else set()
    cur = set(skillmeta.references(name))
    if real - cur:
        merged = sorted(real | cur)
        raw2 = p.read_text(encoding='utf-8')
        # 双重编码：外层给 YAML 字符串，内层是 JSON 数组文本（metadata 规范要求 string->string）
        encoded = json.dumps(json.dumps(merged, ensure_ascii=False, separators=(',', ':')),
                             ensure_ascii=False)
        mm = re.search(r'^(  references: ).*$(,?\n)', raw2, re.M)
        if mm:
            new2 = raw2[:mm.start()] + mm.group(1) + encoded + mm.group(2) + raw2[mm.end():]
        else:
            anchor = re.search(r'^(  related-skills: .*?)(?=^\s{2}[\w-]+: )', raw2, re.M | re.S)
            new2 = raw2[:anchor.end()] + f'  references: {encoded}\n' + raw2[anchor.end():]
        p.write_text(new2, encoding='utf-8', newline='\n')
        print(f'  已登记 references: {sorted(real - cur)}')
    print(f'  ✅ 完成')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('skills', nargs='+')
    ap.add_argument('--plan', action='store_true', help='只看会拆什么，不写盘')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    for s in args.skills:
        do(s, args.plan)
    return 0


if __name__ == '__main__':
    sys.exit(main())
