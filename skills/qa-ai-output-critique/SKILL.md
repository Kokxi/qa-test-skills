---
name: qa-ai-output-critique
description: >-
  对AI生成的测试用例进行八维评审（完整性、正确性、可执行性、风险覆盖、规范性、一致性、追溯性、冗余度），是AI生成用例后的第一个质量门禁。当AI刚刚生成了一大批测试用例、你需要确保这些用例真的有价值而不是"看起来不错"时，应当使用此技能。不要假设AI输出的都是对的——AI经常生成语义正确但实际操作不了的用例。每个维度评分低于7分的必须标注问题并使用MISSING/WRONG/VAGUE等规范格式标记。无上游场景树/风险清单时降级为六维评审（跳过追溯性、简化完整性）。
  触发场景：检查一下输出、评审用例质量、验证完整性、这个用例对吗、自动检查时。 Use when the user asks about: critiquing AI-generated test cases across completeness, correctness, executability, risk coverage, conformance, consistency, traceability, and redundancy.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-ai-output-critique"
  display-name: "AI 测试输出评审"
  version: "1.8.0"
  when-to-use: "AI生成用例后自动激活（最终输出前的必过门禁）；用户说\"检查一下输出\"、\"评审用例质量\"、\"验证完整性\"、\"这个用例对吗\"、\"自动检查\"时"
  related-skills: "{\"upstream\":[\"qa-ai-prompt-strategy\",\"qa-scenario-tree\",\"qa-risk-intuition\"],\"downstream\":[\"qa-ai-blindspot-compensation\",\"qa-expert-review\",\"qa-output-validation\"]}"
  references: "[\"references/review-dimensions.md\",\"references/deep-review-techniques.md\",\"assets/critique-report.md\"]"
  input-format: "{\"required\":[{\"name\":\"AI生成测试用例\",\"type\":\"array\",\"description\":\"AI生成的9列标准测试用例\"}],\"optional\":[{\"name\":\"场景树\",\"type\":\"object\",\"description\":\"来自qa-scenario-tree，用于完整性评审\"},{\"name\":\"风险清单\",\"type\":\"object\",\"description\":\"来自qa-risk-intuition，用于风险覆盖评审\"},{\"name\":\"需求ID列表\",\"type\":\"array\",\"description\":\"REQ-{模块缩写}-{序号} 列表，用于追溯性评审\"}]}"
  output-format: "{\"traceability\":[\"本技能只评审、不新增 ID；评审问题关联到被评审的原用例ID：TC_{模块缩写}_{功能缩写}_{三位序号}\",\"覆盖遗漏的依据引用上游 ID：REQ- 需求 / SC- 场景 / RISK- 风险点\"],\"structure\":[{\"critique_report\":\"评审报告：八维评分（降级模式为六维）+ 问题清单（用例ID|维度|标记|问题描述|修正建议）+ 覆盖遗漏 + 改进方向 + 三选一结论\"},\"评分：每维 10 分、总分≥64 合格；任一维 <7 分必须标问题并修改（总分达标不豁免单维不合格）\",\"问题标记三选一：MISSING（缺失）/ WRONG（错误）/ VAGUE（含糊）\",\"覆盖遗漏必须给出依据 ID，不接受凭感觉的\\\"还不够全面\\\"\",\"本技能不产出 9 列用例表 —— 只评审，用例由 qa-test-case-design 定义、qa-ai-prompt-strategy 驱动生成\"]}"
  error-recovery-guidance: "{\"on_failure\":\"评审发现系统性问题时回退到AI生成步骤修正\",\"retry_behavior\":\"修正提示词或上下文后重新生成并评审\"}"
  categories: "[\"Development\",\"Testing\",\"AI\"]"
  depth-requirement: "{\"reference_value\":\"按用例数量与复杂度调整评审投入；用例越多越要分维度逐条评，不抽样\",\"minimum\":\"至少覆盖功能正确性、边界条件、异常场景 3 个评审维度；低于 7 分的维度必须标问题\"}"
---

> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及测试用例整理、合并或删除建议。
> 实际使用时请勿直接执行批量删除操作，先备份原数据并确认非关键用例。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# AI 输出评审

## 核心原则

AI 输出**看起来**都对，但专家能看出哪里不够。

这个技能是 AI 生成用例后的**第一个质量门禁**——不要假设 AI 输出的都是对的。

## 1. 八维评审速查

每维 10 分，**总分 ≥ 64 合格**。**但总分达标不豁免单维不合格**：任一维 < 7 分必须改。

| 维度 | 评分核心 | 最常见问题 |
|------|---------|-----------|
| **完整性** | 场景覆盖是否完整 | 缺异常路径 |
| **正确性** | 业务规则和预期是否正确 | 预期结果不自洽 |
| **可执行性** | 步骤是否清晰可执行 | 步骤写"按正常流程" |
| **风险覆盖** | 高风险区域是否深测 | 资损/并发场景缺失 |
| **规范性** | 格式是否符合标准 | 编号断号、列错位 |
| **追溯性** | `REQ-`/`SC-` ID 是否完整 | 用例无需求关联 |
| **一致性** | 用例间是否自相矛盾 | 前置与步骤不匹配 |
| **冗余度** | 是否有无价值用例 | 多条用例覆盖同一点 |

> 逐维详细评分标准与评审清单见 [`references/review-dimensions.md`](references/review-dimensions.md)。

## 2. 评审模式

| 模式 | 条件 | 评审维度 | 适用 |
|------|------|---------|------|
| **A 完整评审** | 场景树 **AND** 风险清单 **AND** 需求 ID 列表 | 八维全启用 | 工作流标准评审 |
| **B 降级评审** | 缺任一上游 | 六维（跳过追溯性，简化完整性） | 独立使用、快速检查 |

**降级处理**

| 缺少的上游 | 降级策略 |
|-----------|---------|
| 场景树 | 完整性基于通用场景清单（主流程/分支/异常/边界） |
| 风险清单 | 风险覆盖基于默认风险类型（资金/安全/并发/数据一致性） |
| 需求 ID 列表 | **追溯性维度直接跳过**，标注"需补充追溯信息" |

> **降级必须显式声明**。静默降级会让评审报告看起来比实际更权威。

## 3. 国产模型特有评审点

除八维通用评审外，国产模型输出还需额外检查（这些是通用维度覆盖不到的失败模式）：

| 评审点 | 典型表现 | 处理 |
|--------|---------|------|
| **中文语义漂移** | 标题"验证登录"但步骤在测注册 | 用"步骤是否支撑标题"反向核查，漂移即降分 |
| **数字/单位幻觉** | 凭空编造超时值、并发数、金额单位 | 核对来源，无依据标 `MISSING：需基准数据` |
| **政策/合规表述** | 预期结果含不合规表述（支付/个人信息） | 标合规风险，提示对照监管要求 |
| **格式不稳定** | 表格列错位、编号断号（`TC_001`→`TC_003`）、中文标点混入 | 按规范性维度检查编号连续性 |
| **过度泛化** | 写得"像测试指南"而非"可执行用例" | 按可执行性维度扣分，要求补具体步骤 |
| **伪正确性** | 预期结果"返回正确"但未定义什么算正确 | 要求可验证（具体状态码/字段值） |

**评审动作**：发现任一问题 → 按对应八维维度降分 + 输出规范标记（`MISSING`/`WRONG`/`VAGUE`）+ 修正建议。

## 4. 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 逐维详细评分标准与评审清单 | [`references/review-dimensions.md`](references/review-dimensions.md) |
| 报告已出，想再深挖一层或决定砍哪些用例 | [`references/deep-review-techniques.md`](references/deep-review-techniques.md)（假设挖掘 / 迭代决策树 / AI 反驳 / ROI） |
| 写评审报告 | [`assets/critique-report.md`](assets/critique-report.md)（模式 A/B 模板 + 填写要求 + 自检） |

## 5. 产出

```markdown
# 测试用例评审报告

## 一、八维评分          → 每维 10 分，<7 分标问题
## 二、问题清单          → 用例 ID | 维度 | 标记 | 问题描述 | 修正建议
## 三、覆盖遗漏          → 必须给依据 ID（RISK- / REQ- / SC-）
## 四、改进方向          → 可执行的具体动作
## 五、评审结论          → 需重新生成 / 需修改后复审 / 通过
```

标记三选一：`MISSING`（缺失）/ `WRONG`（错误）/ `VAGUE`（含糊）

> 完整模板见 `assets/critique-report.md`。**本技能只评审，不产出用例。**

## 6. 交付前自检

- [ ] 八维（或六维）逐维评分，低于 7 分的已标问题
- [ ] **总分达标但存在高严重度问题时，明确要求修改**（不因总分豁免）
- [ ] 每个问题关联到具体用例 ID，且有 `MISSING`/`WRONG`/`VAGUE` 标记
- [ ] 覆盖遗漏都给出了依据 ID（`RISK-`/`REQ-`/`SC-`），不是凭感觉
- [ ] 国产模型 6 项特有评审点已逐项检查
- [ ] 降级模式已显式声明缺哪些上游数据
- [ ] 评审结论三选一且明确
- [ ] 用例编号格式为 3 段式，无断号、无 `TC_`/`SC-` 混用
