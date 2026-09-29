---
name: qa-stakeholder-communication
description: >-
  当需要告诉开发"这个 Bug 必须修"、跟产品经理沟通需求变更的影响、或者向管理层汇报质量风险时使用此技能。不同角色关注的事情不同——开发要的是复现步骤和定位信息，产品要的是影响范围和优先级建议，管理层要的是风险判断和决策依据。此技能提供针对开发/产品/管理层的沟通模板和策略。产出根据不同角色定制的沟通话术和汇报材料模板。 触发场景：怎么沟通、跟开发说、跟PM说、跟领导说、沟通策略、向上汇报、干系人沟通、推动问题解决需要有效沟通时。 Use when the user asks about: communicating test findings to engineers, product managers, and management using role-tailored templates and escalation strategy.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-stakeholder-communication"
  display-name: "Stakeholder Communication"
  version: "1.8.0"
  when-to-use: "用户说\"怎么沟通\"、\"跟开发说\"、\"跟PM说\"、\"跟领导说\"、\"沟通策略\"、\"向上汇报\"、\"干系人沟通\"、需要与不同角色沟通、推动问题解决需要有效沟通时"
  related-skills: "{\"upstream\":[\"qa-bug-reporting\",\"qa-release-risk-governance\",\"qa-quality-metrics\"],\"downstream\":[]}"
  references: "[\"references/comms-patterns.md\"]"
  input-format: "{\"required\":[{\"name\":\"测试报告\",\"type\":\"object\",\"description\":\"来自qa-test-reporting的测试报告\"},{\"name\":\"受众分析\",\"type\":\"string\",\"description\":\"报告接收方的角色和信息需求\"}],\"optional\":[{\"name\":\"沟通渠道\",\"type\":\"string\",\"description\":\"可用的沟通渠道和频率\"}]}"
  output-format: "{\"traceability\":[\"每份沟通策略带唯一ID（COMM-XXXX）\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"communication_plan\":\"沟通计划\"},{\"tailored_report\":\"定制化报告\"},{\"key_metrics\":\"关键指标呈现\"},{\"risk_highlight\":\"风险提示\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"沟通策略未能推动问题解决时回退到问题定位补充\",\"retry_behavior\":\"补充定位后重新设计沟通策略\"}"
  categories: "[\"Development\",\"Team\"]"
  depth-requirement: "{\"reference_value\":\"根据沟通场景调整策略深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少覆盖开发、PM、领导3类角色的沟通策略\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及订单号、支付金额、截图、身份证、手机号等敏感数据。
> 实际使用时请勿粘贴真实生产数据、客户信息或财务凭证；测试前应脱敏/掩码处理。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# 干系人沟通

## 核心原则

同样一个Bug，跟不同人说完全不同的表述方式——说对方关心的，而不是你关心的。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 按受众选沟通话术时 | [`references/comms-patterns.md`](references/comms-patterns.md) |

> `三类沟通模式`的完整内容已下沉至 `references/comms-patterns.md`，避免每次触发都占用上下文。

## 高危表达对比

| 场景 | 不要说 | 可以说 |
|------|--------|--------|
| Bug修复延迟 | "开发没时间" | "这个Bug涉及核心逻辑，需要更多时间确保质量" |
| 测试延期 | "测试做不完" | "为了保证质量，建议延长2天测试时间" |
| 质量问题 | "质量很差" "这个功能有风险" | "这个功能需要更多测试时间" |
| 资源不足 | "人不够" | "为了按时交付，建议增加1名测试人员" |
| 需求变更 | "需求又变了" | "这个变更会影响测试范围，建议重新评估时间" |

## 沟通场景模板

### 场景1：Bug评审会

```text
参会角色：开发、测试、PM
沟通内容：
├─ 测试：Bug描述、复现步骤、影响范围
├─ 开发：根因分析、修复方案、修复时间
└─ PM：优先级评估、资源协调
```

### 场景2：发布评审会

```text
参会角色：开发、测试、PM、运维
沟通内容：
├─ 测试：测试结果、质量评估、风险提示
├─ 开发：变更内容、技术风险
├─ PM：业务影响、发布决策
└─ 运维：部署方案、回滚方案
```

### 场景3：质量报告

```text
报告对象：老板、PM
报告内容：
├─ 质量指标：缺陷密度、漏测率
├─ 质量趋势：改善/稳定/恶化
├─ 风险提示：高风险区域
└─ 改进建议：建议措施
```

## 应用场景

**发现一个支付Bug，需要同步给不同角色**
→ 跟开发说：技术细节+复现步骤+日志截图（定位问题）
→ 跟PM说：影响用户数+严重程度+修复时间（评估影响）
→ 跟老板说：一句话结论+业务影响+风险等级（决策依据）

**Bug评审会上开发说"这个没问题"**
→ 沟通场景应对：用数据和截图说话，避免"我觉得"，使用"数据显示"

## 自检清单

沟通完成后检查：
- [ ] 是否针对受众定制了信息？
- [ ] 是否包含了对方需要的决策信息？
- [ ] 是否避免了高危表达？
- [ ] 是否达成了沟通目标？


## 检查清单

- [ ] 受众角色是否识别？
- [ ] 沟通策略是否定制？
- [ ] 关键信息是否突出？
- [ ] 推动方案是否可行？
- [ ] 反馈机制是否建立？
