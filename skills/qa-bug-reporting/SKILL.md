---
name: qa-bug-reporting
description: >-
  当发现了一个 Bug 需要提交、自己提的 Bug 被开发打回来了、或者团队 Bug 质量参差不齐需要统一规范时使用此技能。一个高质量的 Bug 报告应该让开发看一遍就能复现并定位，不需要来回追问。包含清晰的复现步骤（从环境准备到操作序列到预期/实际结果）、根因推测、影响范围评估和必要附件。 ⚠️ 本技能示例可能调用外部抓包/日志工具，请在受控环境执行。 触发场景：提Bug、写Bug报告、Bug描述、报告格式、复现步骤、加附件、开发打回Bug报告需要改进时。 Use when the user asks about: writing a bug report an engineer can reproduce without asking follow-up questions, or fixing reports that got rejected.
license: MIT
allowed-tools: Read Grep Glob Bash
metadata:
  slug: "qa-bug-reporting"
  display-name: "Bug Reporting"
  version: "1.8.0"
  when-to-use: "用户说\"提Bug\"、\"写Bug报告\"、\"Bug描述\"、\"报告格式\"、\"复现步骤\"、\"加附件\"、需要编写或优化Bug报告、开发打回Bug报告需要改进时"
  related-skills: "{\"upstream\":[\"qa-execution-observation\",\"qa-bug-root-cause-analysis\",\"qa-question-framework\"],\"downstream\":[\"qa-bug-lifecycle\",\"qa-stakeholder-communication\"]}"
  references: "[\"references/bug-report-structure.md\"]"
  input-format: "{\"required\":[{\"name\":\"Bug描述\",\"type\":\"string\",\"description\":\"缺陷的详细描述\"},{\"name\":\"复现步骤\",\"type\":\"array\",\"description\":\"缺陷复现的具体步骤\"}],\"optional\":[{\"name\":\"环境信息\",\"type\":\"string\",\"description\":\"缺陷发现时的环境配置\"},{\"name\":\"日志信息\",\"type\":\"string\",\"description\":\"相关执行日志\"}]}"
  output-format: "{\"traceability\":[\"每个Bug带唯一ID（TC_{缺陷模块缩写}_{功能缩写}_{序号}，如 TC_BUG_LOGIN_001；缺陷追溯保留 BUG 前缀）\",\"关联执行用例ID（TC_{模块缩写}_{功能缩写}_{序号}，如 TC_API_LOGIN_001）\"],\"structure\":[{\"bug_title\":\"缺陷标题\"},{\"severity\":\"严重级别\"},{\"priority\":\"优先级\"},{\"reproduction_steps\":\"复现步骤\"},{\"expected_vs_actual\":\"预期vs实际结果\"},{\"root_cause\":\"根因推测（可选）\"},{\"impact_assessment\":\"影响范围评估\"},{\"attachments\":\"附件清单\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"Bug报告被开发打回时回退到执行观察步骤补充信息\",\"retry_behavior\":\"补充复现步骤或环境信息后重新提交\"}"
  categories: "[\"Development\",\"Testing\",\"Quality\"]"
  depth-requirement: "{\"reference_value\":\"根据缺陷严重度调整报告深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少包含复现步骤、预期vs实际、影响评估3个核心结构\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及订单号、支付金额、截图、身份证、手机号等敏感数据。
> 实际使用时请勿粘贴真实生产数据、客户信息或财务凭证；测试前应脱敏/掩码处理。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# Bug报告艺术

## 核心原则

好的Bug报告不只是"描述问题"，而是帮开发缩小排查范围。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 写缺陷报告时，取七段式结构与各段写法 | [`references/bug-report-structure.md`](references/bug-report-structure.md) |

> `Bug报告黄金结构`的完整内容已下沉至 `references/bug-report-structure.md`，避免每次触发都占用上下文。

## Bug报告模板

> 📌 本节与 qa-bug-lifecycle「缺陷报告模板」为同一概念的两个版本。本技能模板侧重执行（含前置条件、影响评估），lifecycle 模板侧重管理（含状态、优先级字段）。修改字段时请同步更新两个模板。

```markdown
# Bug报告

## 基本信息
- Bug标题：[功能模块] + [具体现象] + [触发条件]
- 严重程度：P0/P1/P2/P3
- Bug类型：功能/性能/安全/UI/兼容性
- 发现版本：[版本号]
- 环境信息：[浏览器/系统/设备]

## 前置条件
1. [条件1]
2. [条件2]
3. [条件3]

## 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]
4. 观察[现象]

## 预期结果
[应该发生什么]

## 实际结果
[实际发生了什么]

## 附件
- 截图：[截图描述]
- 日志：[日志内容]
- 网络：[请求/响应]

## 根因推测（可选）
[可能是...因为...建议检查...]

## 影响评估
- 影响功能：[功能]
- 影响用户：[用户范围]
- 影响程度：[严重/一般/轻微]
- 修复优先级：[P0-P3]
```

## 输出示例

**用户发现登录功能报错**
→ 使用Bug报告结构生成：
  - 标题：[登录] 输入正确密码后提示"密码错误"（Chrome浏览器）
  - 前置条件：已注册用户testuser001，Chrome 120.0
  - 复现步骤和预期vs实际结果

**用户需要提交支付Bug**
→ 自动组装Bug报告7个结构部分，生成标准格式的Bug报告

**开发打回Bug报告说"无法复现"**
→ 触发本技能补充复现步骤细节和环境信息

## 检查清单

Bug报告完成后检查：
- [ ] 标题是否清晰（是什么+在哪+条件下）？
- [ ] 前置条件是否完整？
- [ ] 复现步骤是否可操作？
- [ ] 预期vs实际是否明确？
- [ ] 附件是否充分？
- [ ] 根因推测是否合理？
- [ ] 影响评估是否准确？
