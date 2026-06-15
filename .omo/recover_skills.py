#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate all 41 corrupted SKILL.md files from recovery metadata.
Fixes garbled frontmatter, restores slop-quote section, generates body.
"""

import json, os, sys

METADATA_PATH = r'E:\opentest\.omo\skills-recovery-metadata.json'
SKILLS_DIR = r'E:\opentest\skills'

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

CLUSTER_CTX = {
    '00-router':                  'QA任务路由和技能分发',
    '1-认知与思维':                '测试分析和批判性思维',
    '2-需求到模型':                '测试需求分析和场景建模',
    '3-深度设计':                  '测试用例深度设计',
    '4-AI协作':                   'AI辅助测试设计',
    '5-执行洞察':                  '测试执行和缺陷分析',
    '6-策略架构':                  '测试策略和质量架构',
    '7-沟通传达':                  '测试沟通和质量传承',
}

CLUSTER_PROMPT_OBJ = {
    '00-router': '根据用户输入判断调用哪个QA技能',
    '1-认知与思维': '对需求、用例和结果做深度分析和质疑',
    '2-需求到模型': '将模糊需求转化为结构化测试模型',
    '3-深度设计': '设计高覆盖率的测试用例和场景',
    '4-AI协作': '利用AI高效产出高质量测试内容',
    '5-执行洞察': '从测试执行中提取关键信息和定位问题',
    '6-策略架构': '设计整体测试策略和质量保障方案',
    '7-沟通传达': '做好测试沟通、知识传递和团队协作',
}

def esc_yaml(s):
    """Escape string for YAML value."""
    if not s:
        return '""'
    if any(c in s for c in ':",#[]{}'):
        return '"' + s.replace('"', '\\"') + '"'
    return s

def make_frontmatter(skill_data, cluster_name):
    lines = ['---']
    lines.append(f'name: {skill_data["name"]}')
    lines.append(f'description: {esc_yaml(skill_data["description"])}')
    lines.append('allowed-tools:')
    for t in skill_data.get('allowedTools', ['Read', 'Write']):
        lines.append(f'  - {t}')
    lines.append(f'when_to_use: {esc_yaml(skill_data["whenToUse"])}')
    lines.append('metadata:')
    lines.append(f'  cluster: {cluster_name}')
    lines.append('---')
    return '\n'.join(lines)

def to_display_name(name):
    """qa-critical-thinking -> qa-critical-thinking (keep as-is, it's the skill id)."""
    return name

def gen_must_items(skill_data, cluster_name):
    desc = skill_data.get('description', '')
    sq = skill_data.get('slotQuote', '')
    rb = skill_data.get('rebuttal', '')
    items = []

    # Cluster-specific musts
    cluster_musts = {
        '00-router': [
            '准确识别用户输入中隐含的QA任务类型',
            '路由决策附带判断依据',
        ],
        '1-认知与思维': [
            '对需求和假设保持结构化质疑',
            '区分事实、推测和个人观点',
            '输出分析结论附带可信度标注',
        ],
        '2-需求到模型': [
            '明确需求来源和约束条件后再开始建模',
            '模型覆盖主路径、分支路径和异常路径',
            '标注模型中每个节点的验证要点',
        ],
        '3-深度设计': [
            '设计前先明确测试目标和范围',
            '覆盖正向、负向、边界和异常场景',
            '输出用例附带测试数据和预期结果',
        ],
        '4-AI协作': [
            '给AI的输入要结构化、完整、无歧义',
            'AI输出后必须人工复核关键判断',
            '记录AI的推理过程和自己的审核结论',
        ],
        '5-执行洞察': [
            '执行前明确要验证的关键点',
            '记录实际结果与预期的差异',
            '异常信号出现时先隔离再分析',
        ],
        '6-策略架构': [
            '策略设计基于风险和资源数据',
            '每种策略附带可量化的验收标准',
            '定期回顾和调整策略',
        ],
        '7-沟通传达': [
            '根据受众调整沟通内容和形式',
            '输出结论附带依据和上下文',
            '关键信息留痕可追溯',
        ],
    }

    items.extend(cluster_musts.get(cluster_name, [
        '明确目标和输入条件',
        '输出结构化结果',
        '标注不确定项和风险',
    ]))

    # Rebuttal-based must
    if '文' in rb or '记录' in rb or '记' in rb:
        items.append('关键分析过程和结论必须文档化')
    if '确认' in rb or '验证' in rb:
        items.append('AI/工具的结论必须人工确认')
    if '更新' in rb or '刷新' in rb or '版本' in rb:
        items.append('产出物需要版本管理和定期更新')

    return items[:5]

def gen_must_not_items(skill_data):
    sq = skill_data.get('slotQuote', '')
    items = []

    # Derive must-nots from slop quotes
    all_nots = [
        '不要拿到第一轮输出就停止追问和深挖',
        '不要在信息不完整的情况下下结论',
        '不要忽略边界条件和异常场景',
        '不要把AI的输出直接当最终答案',
        '不要做完分析不记录过程和结论',
        '不要用猜测代替数据验证',
        '不要跳过风险高但测起来麻烦的场景',
        '不要让工具替你做判断决策',
        '不要在评审中只找茬不帮改进',
        '不要做完就丢，定期回顾和更新',
        '不要忽略上下游依赖的影响',
        '不要把不确定的事情说死',
    ]

    # Select most relevant must-nots based on skill
    if 'AI' in sq or 'AI' in skill_data.get('name', ''):
        items.extend([a for a in all_nots if 'AI' in a][:2])
    if '文' in sq or '记' in sq or '记录' in sq:
        items.extend([a for a in all_nots if '记录' in a or '文' in a][:2])
    if '确' in sq or '确认' in sq:
        items.extend([a for a in all_nots if '確認' in a or '确认' in a][:1])
    if '回' in sq or '更新' in sq or '版本' in sq:
        items.extend([a for a in all_nots if '更新' in a or '回顾' in a][:1])

    # Fill with defaults
    defaults = [
        '不要凭感觉代替结构化分析',
        '不要为了省事跳过风险判断',
        '不要让流程空转没有实际产出',
    ]
    while len(items) < 3:
        for d in defaults:
            if d not in items:
                items.append(d)
                break

    return items[:4]

def gen_prompt_template(skill_data, cluster_name):
    desc = skill_data.get('description', '')
    sq = skill_data.get('slotQuote', '')
    rb = skill_data.get('rebuttal', '')
    ctx = CLUSTER_CTX.get(cluster_name, '软件测试')
    obj = CLUSTER_PROMPT_OBJ.get(cluster_name, '完成测试任务')
    name = skill_data['name']

    # Parse key action from description
    action = desc.split('——')[0] if '——' in desc else desc[:30]

    return f"""## 角色
你是一名资深的{ctx}工程师，擅长{obj}。

## 任务
{action}。

## 输入
{{输入内容：需求描述 / PRD / 测试结果 / 问题描述等}}

## 输出要求

1. **结构化输出**：按标准格式输出，包括分析过程、结论、依据
2. **风险标注**：对不确定的判断标注可信度（高/中/低）
3. **可执行**：输出结果可以直接用于下一阶段工作

## 注意事项

> {sq}

> 提示：{rb}

## 输出格式

```markdown
## 分析过程

## 结论

## 风险与不确定性

## 下一步建议
```"""

def gen_checklist(skill_data, cluster_name):
    desc = skill_data.get('description', '')
    items = []

    cluster_checks = {
        '00-router': [
            '路由判断是否覆盖所有已知QA场景',
            '路由逻辑是否有明确的触发条件',
            '是否存在路由死循环或漏路由',
        ],
        '1-认知与思维': [
            '分析过程是否基于足够的信息',
            '是否区分了客观事实和主观推测',
            '是否有遗漏的关键角度',
        ],
        '2-需求到模型': [
            '模型是否覆盖了主路径和所有分支',
            '模型中的节点是否都有明确的验证方法',
            '模型是否经过干系人确认',
        ],
        '3-深度设计': [
            '用例是否覆盖了正向、负向、边界场景',
            '每条用例的预期结果是否明确可验证',
            '测试数据是否准备完整',
        ],
        '4-AI协作': [
            '给AI的输入是否完整无歧义',
            'AI输出的关键点是否经过人工复核',
            '是否记录了AI推理和人工审核的过程',
        ],
        '5-执行洞察': [
            '是否记录了执行环境和执行条件',
            '异常信号是否都经过分析确认',
            '结论是否有足够的数据支撑',
        ],
        '6-策略架构': [
            '策略是否基于实际风险和数据',
            '是否设定了可量化的质量门禁',
            '策略更新机制是否明确',
        ],
        '7-沟通传达': [
            '沟通内容是否根据受众调整',
            '关键信息是否留痕可追溯',
            '改进建议是否可执行可跟踪',
        ],
    }

    items.extend(cluster_checks.get(cluster_name, [
        '输出是否结构化、可复用',
        '关键判断是否有依据支撑',
        '是否符合当前项目上下文',
    ]))
    return items[:4]

def build_skill_md(skill_data, cluster_name):
    # Frontmatter
    parts = [make_frontmatter(skill_data, cluster_name), '']

    name = skill_data['name']
    desc = skill_data.get('description', '')
    sq = skill_data.get('slotQuote', '')
    rb = skill_data.get('rebuttal', '')

    # Title
    parts.append(f'# {name}')
    parts.append('')

    # Slop quote section (skip if no quote)
    if sq and sq.strip():
        parts.append(f'> **"{sq}"**')
        if rb and rb.strip():
            parts.append(f'>')
            parts.append(f'> *{rb}*')
        parts.append('')

    # 使用指南
    parts.append('## 使用指南')
    parts.append('')

    parts.append('### ✅ 推荐做法')
    parts.append('')
    for i, item in enumerate(gen_must_items(skill_data, cluster_name), 1):
        parts.append(f'{i}. {item}')
    parts.append('')

    parts.append('### ❌ 避免做法')
    parts.append('')
    for i, item in enumerate(gen_must_not_items(skill_data), 1):
        parts.append(f'{i}. {item}')
    parts.append('')

    # 模板 Prompt
    parts.append('## 模板 Prompt')
    parts.append('')
    parts.append(gen_prompt_template(skill_data, cluster_name))
    parts.append('')

    # 验收 Checklist
    parts.append('## 验收 Checklist')
    parts.append('')
    for item in gen_checklist(skill_data, cluster_name):
        parts.append(f'- [ ] {item}')
    parts.append('')

    return '\n'.join(parts)

def main():
    ok = 0
    fail = 0
    for cluster_name, cluster_data in metadata['clusters'].items():
        for skill_name, skill_data in cluster_data['skills'].items():
            skill_dir = os.path.join(SKILLS_DIR, skill_name)
            target = os.path.join(skill_dir, 'SKILL.md')
            if not os.path.isdir(skill_dir):
                print(f'⚠  SKIP {skill_name} (dir not found)')
                continue
            try:
                content = build_skill_md(skill_data, cluster_name)
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'OK  {skill_name} -> {target}')
                ok += 1
            except Exception as e:
                print(f'FAIL  {skill_name} FAIL: {e}')
                fail += 1

    print(f'\n--- Done: {ok} ok, {fail} fail ---')
    return 1 if fail else 0

if __name__ == '__main__':
    sys.exit(main())
