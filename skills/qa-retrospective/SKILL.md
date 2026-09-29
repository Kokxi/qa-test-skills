---
name: qa-retrospective
description: >-
  当一个迭代结束、一个项目完成、或者发生线上事故需要事后分析时使用此技能。通过系统性的回顾会议和数据复盘，把个人和团队的经验教训转化为可复用的组织资产。不要沦为"说说好话走个形式"——有效的复盘需要有数据支撑（缺陷趋势/漏测分析/效率数据）、有根因分析（为什么出问题）和有 action items（下次怎么做不一样）。输出复盘报告和改进项追踪表。 触发场景：测试复盘、迭代复盘、项目复盘、经验沉淀、漏测分析、回顾总结、事后分析、反复出现同类问题需要根因改进时。 Use when the user asks about: test retrospectives and post-incident review — defect trends, escaped-defect analysis, efficiency data, and turning lessons into reusable assets.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-retrospective"
  display-name: "测试复盘"
  version: "1.8.0"
  when-to-use: "用户说\"测试复盘\"、\"迭代复盘\"、\"项目复盘\"、\"经验沉淀\"、\"漏测分析\"、\"回顾总结\"、\"事后分析\"、需要复盘总结经验、反复出现同类问题需要根因改进时"
  related-skills: "{\"upstream\":[\"qa-bug-root-cause-analysis\",\"qa-quality-metrics\",\"qa-bug-lifecycle\"],\"downstream\":[\"qa-heuristic-checklist\",\"qa-team-coaching\",\"qa-test-leadership\"]}"
  references: "[\"references/five-steps.md\"]"
  input-format: "{\"required\":[{\"name\":\"迭代数据\",\"type\":\"object\",\"description\":\"迭代的测试和缺陷数据\"},{\"name\":\"团队反馈\",\"type\":\"array\",\"description\":\"团队成员反馈和意见\"}],\"optional\":[{\"name\":\"历史回顾\",\"type\":\"object\",\"description\":\"历史回顾记录\"}]}"
  output-format: "{\"traceability\":[\"每次复盘带唯一ID（RETRO-XXXX）\"],\"structure\":[{\"retrospective_report\":\"复盘报告\"},{\"what_went_well\":\"做得好的事项\"},{\"improvement_areas\":\"改进领域\"},{\"action_items\":\"行动项清单\"},{\"follow_up_plan\":\"跟踪计划\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"复盘数据不充分时回退到质量度量收集更多数据\",\"retry_behavior\":\"补齐数据后重新复盘\"}"
  categories: "[\"Development\",\"Team\"]"
  depth-requirement: "{\"reference_value\":\"根据迭代数据调整复盘深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少包含数据支撑、根因分析、action items 3要素\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及发布流程优化和协作流程调整建议。
> 这些是复盘议题不是直接操作；请勿未经评审即变更团队流程，先达成共识再落地。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# 复盘与经验沉淀

## 核心原则

复盘的目的是找到系统性的改进点，而不是找谁背锅。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 需要五步法的方法细节时，取对应小节 | [`references/five-steps.md`](references/five-steps.md) |

> `复盘五步法`的完整内容已下沉至 `references/five-steps.md`，避免每次触发都占用上下文。

## 复盘报告模板

```markdown
# 复盘报告

## 1. 基本信息
- 迭代版本：[版本号]
- 复盘时间：[日期]
- 参与人员：[人员列表]

## 2. 数据回顾
- 缺陷数据：[新增X个，严重X个]
- 漏测数据：[线上X个]
- 测试数据：[执行率X%，通过率X%]

## 3. 问题分析
- 主要问题：[问题描述]
- 根因分析：[5 Whys分析]
- 根因归类：[思维/信息/流程/工具/能力]

## 4. 改进措施
- 措施1：[具体措施]
- 措施2：[具体措施]
- 措施3：[具体措施]

## 5. 资产沉淀
- Checklist更新：[更新内容]
- 模板更新：[更新内容]
- 知识库更新：[更新内容]

## 6. 跟踪计划
- 检查时间：[时间]
- 负责人：[人员]
- 验收标准：[标准]
```

## 应用场景

**迭代结束后复盘：用户登录模块出现了3个线上Bug**
→ 第1步：收集数据（Bug报告、修复记录、测试用例覆盖）
→ 第2步：5 Whys分析（why漏测？→边界用例未覆盖→why？→测试设计时未识别边界→why？→需求未说明边界）
→ 第3步：改进措施（增加边界分析环节、补充典型边界checklist）
→ 第4步：资产沉淀（将边界checklist更新到启发式清单）
→ 第5步：跟踪计划（下个迭代验证新增checklist的有效性）

**用户说"这个问题又发生了"**
→ 触发复盘：系统性的根因分析，避免同类问题再次发生

## 自检清单

复盘完成后检查：
- [ ] 数据收集是否完整？
- [ ] 根因分析是否深入？
- [ ] 改进措施是否具体？
- [ ] 资产沉淀是否完成？
- [ ] 跟踪计划是否制定？
- [ ] 经验是否分享？


## 检查清单

- [ ] 数据是否支撑结论？
- [ ] 根因是否分析？
- [ ] action items是否可执行？
- [ ] 责任人和时限是否明确？
- [ ] 追踪机制是否建立？
