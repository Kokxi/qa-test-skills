---
name: qa-quality-metrics
description: >-
  当管理层问"质量到底怎么样"、需要量化质量数据来做决策、或者想建立质量看板来跟踪趋势时使用此技能。从过程质量（需求评审通过率/用例覆盖度）、结果质量（Bug 密度/线上事故数）、效率（测试周期/回归耗时）和健康度（自动化通过率/环境稳定性）四个维度设计度量指标。⚠️ 度量的目的不是打分，是发现问题趋势——如果只报喜不报忧，度量就没用了。 触发场景：质量度量、质量指标、怎么量化质量、质量看板、质量数据、趋势分析、向管理层展示质量数据时。 Use when the user asks about: test quality metrics and dashboards — process, result, efficiency, and health indicators for management reporting.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-quality-metrics"
  display-name: "Quality Metrics"
  version: "1.8.0"
  when-to-use: "用户说\"质量度量\"、\"质量指标\"、\"怎么量化质量\"、\"质量看板\"、\"质量数据\"、\"趋势分析\"、需要建立度量体系、向管理层展示质量数据时"
  related-skills: "{\"upstream\":[\"qa-release-risk-governance\",\"qa-bug-lifecycle\"],\"downstream\":[\"qa-retrospective\",\"qa-testability-advocacy\",\"qa-stakeholder-communication\",\"qa-tech-debt-management\",\"qa-test-reporting\"]}"
  references: "[\"references/metrics-dimensions.md\"]"
  input-format: "{\"required\":[{\"name\":\"测试数据\",\"type\":\"object\",\"description\":\"测试执行数据和结果\"},{\"name\":\"缺陷数据\",\"type\":\"object\",\"description\":\"缺陷统计和分析数据\"}],\"optional\":[{\"name\":\"历史基线\",\"type\":\"object\",\"description\":\"历史质量基线数据\"}]}"
  output-format: "{\"traceability\":[\"每份度量报告带唯一ID（METRIC-XXXX）\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"quality_dashboard\":\"质量仪表盘\"},{\"defect_density\":\"缺陷密度分析\"},{\"test_coverage\":\"测试覆盖率\"},{\"pass_fail_rate\":\"通过/失败率\"},{\"trend_analysis\":\"质量趋势分析\"},\"覆盖率：涉及覆盖率的结论必须标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述\"]}"
  error-recovery-guidance: "{\"on_failure\":\"度量数据缺失时回退到测试执行和缺陷数据收集\",\"retry_behavior\":\"补齐数据后重新计算指标\"}"
  categories: "[\"Development\",\"Testing\",\"DevOps\"]"
  depth-requirement: "{\"reference_value\":\"根据度量维度调整指标深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少覆盖过程质量、结果质量、效率、健康度4个维度\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

# 质量度量体系

## 核心原则

质量不是感觉，是可以量化的。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 选指标、算指标或查数据来源时，取四类详表 | [`references/metrics-dimensions.md`](references/metrics-dimensions.md) |

> `四类度量指标`的完整内容已下沉至 `references/metrics-dimensions.md`，避免每次触发都占用上下文。

## 度量报告模板

```markdown
# 质量度量报告

## 1. 过程度量
- 用例执行率：[X]% (目标≥95%)
- 用例通过率：[X]% (目标≥90%)
- 需求覆盖率：[X]% (目标100%)
- 自动化覆盖率：[X]%

## 2. 结果度量
- 缺陷密度：[X]/功能点
- 缺陷修复率：[X]% (目标≥95%)
- 漏测率：[X]% (目标≤5%)
- 逃逸率：[X]% (目标≤10%)

## 3. 效率度量
- 测试周期：[X]天
- 用例执行效率：[X]条/人天
- 缺陷发现效率：[X]个/人天
- 缺陷修复周期：[X]天

## 4. 健康度量
- 缺陷趋势：[上升/稳定/下降]
- 缺陷收敛：[收敛/发散]
- 质量趋势：[改善/稳定/恶化]

## 5. 风险分析
- 高风险模块：[模块列表]
- 主要问题：[问题描述]
- 改进建议：[建议列表]
```

## 输出示例

**需要度量当前迭代的质量**
→ 四类度量：
  - 过程度量：用例评审通过率、缺陷发现率
  - 结果度量：遗留缺陷密度、线上故障数
  - 效率度量：测试执行效率、缺陷平均修复时间
  - 健康度量：缺陷趋势图、质量评分变化
→ 输出：质量度量报告，含目标值对比和改进方向

**用户说"质量到底怎么样"**
→ 自动生成质量度量报告，用数据展示质量趋势

## 检查清单

质量度量完成后检查：
- [ ] 度量指标是否定义？
- [ ] 数据收集是否可行？
- [ ] 目标值是否合理？
- [ ] 报告格式是否清晰？
- [ ] 改进建议是否可行？
