---
name: qa-team-coaching
description: >-
  当团队里有测试新人需要带、想提升团队整体测试水平、或者需要把个人经验转化为团队能力时使用此技能。通过 Pair 测试、经验分享、checklist 沉淀、模板建设和培训材料等方式赋能团队。不要等着新人犯错再教——好的赋能是提前给工具和方法论，让新人在第一次做之前就知道"正确的做法是什么"。 触发场景：培训、赋能、新人、怎么教、带人、培养、团队成长、新成员加入需要快速上手时。 Use when the user asks about: coaching and enabling a QA team — pairing, knowledge sharing, checklist and template creation, and onboarding new members.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-team-coaching"
  display-name: "测试团队赋能"
  version: "1.8.0"
  when-to-use: "用户说\"培训\"、\"赋能\"、\"新人\"、\"怎么教\"、\"带人\"、\"培养\"、\"团队成长\"、需要赋能团队、新成员加入需要快速上手时"
  related-skills: "{\"upstream\":[\"qa-retrospective\",\"qa-heuristic-checklist\"],\"downstream\":[]}"
  references: "[\"references/coaching-methods.md\"]"
  input-format: "{\"required\":[{\"name\":\"团队评估\",\"type\":\"string\",\"description\":\"团队测试能力评估结果\"},{\"name\":\"培训需求\",\"type\":\"string\",\"description\":\"团队技能提升需求\"}],\"optional\":[{\"name\":\"培训资源\",\"type\":\"string\",\"description\":\"可用的培训资源和预算\"}]}"
  output-format: "{\"traceability\":[\"每份赋能方案带唯一ID（COACH-XXXX）\"],\"structure\":[{\"coaching_plan\":\"教练计划\"},{\"skill_matrix\":\"技能矩阵\"},{\"training_materials\":\"培训材料清单\"},{\"mentorship_guide\":\"导师指导方案\"},{\"progress_metrics\":\"进步度量方式\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"赋能方案未能补齐能力差距时回退到能力评估补充\",\"retry_behavior\":\"补充评估后重新设计赋能方案\"}"
  categories: "[\"Development\",\"Team\"]"
  depth-requirement: "{\"reference_value\":\"根据团队能力差距调整赋能深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少包含能力评估、培训计划、效果验收3环节\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及发布检查清单和评审流程的培训材料。
> 这些是培训示例不是直接操作；请勿未经授权即变更团队流程或发布标准。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# 团队赋能

## 核心原则

授人以渔——把经验做成checklist、把案例做成模板、把评判标准量化。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 选定赋能方式后，取对应做法 | [`references/coaching-methods.md`](references/coaching-methods.md) |

> `四种赋能方式`的完整内容已下沉至 `references/coaching-methods.md`，避免每次触发都占用上下文。

## 培训材料设计

### 新人培训大纲

```text
第1周：基础认知
├─ 测试基础概念
├─ 公司测试流程
├─ 测试工具使用
└─ 常用Checklist

第2周：技能提升
├─ 用例设计方法
├─ 缺陷管理流程
├─ 测试执行技巧
└─ 常见问题处理

第3周：实战演练
├─ 参与实际项目
├─ 结对测试
├─ 用例评审
└─ Bug评审

第4周：独立工作
├─ 独立负责模块
├─ 定期Review
├─ 问题解答
└─ 能力评估
```

### 培训练习设计

```text
练习类型：
├─ 案例分析：分析真实Bug案例
├─ 用例设计：设计测试用例
├─ Bug报告：编写Bug报告
└─ 场景模拟：模拟测试执行

练习设计原则：
├─ 真实性：基于真实场景
├─ 渐进性：从简单到复杂
├─ 可衡量：有明确评判标准
└─ 可反馈：及时给予反馈
```

## 能力评估体系

### 评估维度

```text
评估维度：
├─ 测试设计能力：用例设计质量
├─ 测试执行能力：执行效率和质量
├─ 缺陷发现能力：Bug发现数量和质量
├─ 沟通协作能力：团队协作效果
└─ 问题解决能力：问题分析和解决

评估标准：
├─ 初级：能完成基础测试任务
├─ 中级：能独立负责模块测试
├─ 高级：能指导新人、优化流程
└─ 专家：能制定策略、推动改进
```

### 评估方法

```text
评估方法：
├─ 日常观察：工作表现观察
├─ 产出评审：用例/Bug报告评审
├─ 能力测试：技能测试
├─ 360度评估：多维度反馈
└─ 成长记录：成长轨迹记录
```

## 应用场景

**新入职的测试同学不知道怎么写测试用例**
→ Checklist式赋能：提供测试用例设计checklist，逐项check即可完成
→ 模板式赋能：提供标准测试用例模板，填空即用
→ Review式赋能：Review他的输出，给出改进建议
→ Pair式赋能：Pair设计一个模块，示范思路

**团队测试能力参差不齐**
→ 能力评估：按维度（需求分析/用例设计/自动化/性能）评估每位成员
→ 针对性培训：根据评估结果设计分层培训内容

## 自检清单

团队赋能完成后检查：
- [ ] 是否设计了Checklist？
- [ ] 是否制作了模板？
- [ ] 是否制定了Review标准？
- [ ] 是否安排了Pair测试？
- [ ] 是否设计了培训材料？
- [ ] 是否建立了评估体系？


## 检查清单

- [ ] 能力差距是否评估？
- [ ] 培训计划是否定制？
- [ ] 效果验收机制是否建立？
- [ ] 个性化建议是否给出？
- [ ] 赋能追踪是否建立？
