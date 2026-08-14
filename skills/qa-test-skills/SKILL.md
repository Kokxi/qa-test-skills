---
name: qa-test-skills
slug: qa-test-skills
displayName: QA Test Skills
version: 1.7.0
description: >-
  从需求文档自动生成结构化测试用例，覆盖功能测试、边界分析、组合测试和回归测试全流程。自动串联48个专家级子技能，按12步工作流编排执行。适用于：上传需求文档（PRD/Word/PDF/URL）需要完整测试用例时、不知道如何设计测试场景或担心遗漏边界条件时、需要AI评审测试输出并补充测试盲区时。每个步骤都有独立技能支撑，输出格式统一、需求可追溯、覆盖率可量化。
when_to_use: >-
  用户说"生成测试用例"、"帮我测试"、"设计测试"、"上传需求"、"开始测试"、上传需求文档/URL时自动激活，
  需要完整测试流程时，想浏览技能集目录、了解QA Test Skills包含哪些技能、查看技能分类说明、获取安装指引时
disable-model-invocation: false
allowed-tools: Read Grep Glob WebFetch Bash
related_skills:
  all_skills:
    - qa-input-validation
    - qa-requirement-review
    - qa-req-deconstruction
    - qa-risk-intuition
    - qa-heuristic-checklist
    - qa-scenario-tree
    - qa-boundary-deep-dive
    - qa-combination-strategy
    - qa-state-transition
    - qa-domain-modeling
    - qa-regression-testing
    - qa-ai-context-engineering
    - qa-ai-prompt-strategy
    - qa-ai-output-critique
    - qa-ai-blindspot-compensation
    - qa-output-validation
    - qa-test-reporting
    - qa-agent-testing
    - qa-expert-review
    - qa-api-testing
    - qa-mobile-testing
    - qa-specialized-testing
    - qa-exploratory-testing
    - qa-tech-debt-management
    - qa-test-estimation
    - qa-bug-lifecycle
    - qa-bug-reporting
    - qa-bug-root-cause-analysis
    - qa-execution-observation
    - qa-ci-cd-testing
    - qa-code-review-for-test
    - qa-critical-thinking
    - qa-question-framework
    - qa-test-case-design
    - qa-test-strategy-design
    - qa-release-risk-governance
    - qa-quality-metrics
    - qa-test-automation-arch
    - qa-tech-selection
    - qa-testability-advocacy
    - qa-test-data-engineering
    - qa-test-env-data
    - qa-shift-left
    - qa-shift-right
    - qa-test-leadership
    - qa-stakeholder-communication
    - qa-team-coaching
    - qa-retrospective
input_format:
  required:
    - name: 用户需求
      type: string
      description: 用户的需求描述，可以是文字、文件路径或URL
  optional:
    - name: 附件
      type: file
      description: 上传的需求文档
    - name: URL
      type: string
      description: 需求文档链接
output_format:
  structure:
    - test_cases: "测试用例列表"
    - coverage_report: "覆盖率报告"
    - risk_areas: "风险区域"
    - test_report: "测试报告"
  traceability:
    - 每个测试用例带唯一ID（TC-XXXX）
    - 关联需求ID（REQ-XXXX）
    - 关联场景ID（SC-XXXX）
---

# QA Test Skills — 测试工作流编排引擎

你是一位资深测试架构师，负责编排整个测试设计流程。初级人员只需提供需求，你自动串联所有子技能，输出专家级测试用例。

## 核心原则

**输入的每一条需求，经过 12 步标准化工作流 + 48 个专家级子技能，最终输出可追溯、结构化的测试用例集。**

> ⚠️ **必须直接输出完整内容，不得只承诺生成**：
> 必须在本次响应中直接输出完整内容，不得只输出"我将生成"等承诺性表述。
> 询问确认不得替代直接输出——用户请求即默示授权，询问只能在输出末尾的"是否补充"环节。
> 若数据不足，先输出已有数据的分析，再标注缺什么。

> ⚠️ **N 个维度全必输出硬约束**：
> 需要编号/分类输出的内容必须按编号逐条输出，未发现问题的也要输出占位行。
> 不适用的也要输出标注"不适用+原因"的占位项，而非省略。
> 末尾的"维度覆盖统计"必须确认 N/N 全覆盖，缺一项即格式校验失败。

> 强制执行规则详见 [`references/enforcement.md`](references/enforcement.md)。

> 各 skill 深度量化基准（`depth_requirement_quantification`）的乘数档位来源与判定指引详见 [`references/depth-benchmarks.md`](references/depth-benchmarks.md)。

> 输入识别、路由规则和可选增强流程详见 [`references/routing.md`](references/routing.md)。

## 标准化工作流

**⚠️ 强制要求：每个步骤必须产出输出文件，不得跳过任何步骤。详细伪代码见 [`references/workflow-detail.md`](references/workflow-detail.md)。**

| 步骤 | 调用的技能 | 输出文件 | 说明 |
|------|-----------|---------|------|
| 第0步 | 需求文档解析 | 需求文档集合.md | 支持 .md/.docx/.pdf，自动追踪索引引用 |
| 第1步 | qa-requirement-review | 需求评审报告.md | 完整性/清晰性/一致性/可测试性/可实现性 |
| 第2步 | qa-req-deconstruction | 需求解构表.md | 显性+隐性+衍生需求 + 五维拆解（简单×2/中等×3/复杂×4） |
| 第3步 | 并行：qa-risk-intuition, qa-heuristic-checklist, qa-scenario-tree | 风险评估.md、启发式清单.md、场景树.md | 场景深度：简单×3/中等×5/复杂×7 |
| 第4步 | 并行：qa-boundary-deep-dive, qa-combination-strategy, qa-state-transition, qa-domain-modeling | 边界清单.md、组合矩阵.md、状态转换图.md、领域模型.md | 边界深度：简单×1.5/中等×2/复杂×2.5 |
| 第5步 | qa-regression-testing | 回归策略.md | 分级策略 + 用例清单 + 执行计划 |
| 第6步 | qa-ai-context-engineering | AI上下文包.md | 打包所有分析结果 |
| 第7步 | qa-ai-prompt-strategy | AI提示词.md ⚠️不得跳过 | 生成优化后的提示词 |
| → | [AI生成测试用例] | 测试用例_初版.csv | |
| 第8步 | qa-ai-output-critique + qa-ai-blindspot-compensation | 用例评审报告.md、盲区补偿用例.md ⚠️不得跳过 | 六维评审 + 六大盲区补盲 |
| 第9步 | qa-test-reporting | 测试报告.md、测试用例.csv | 最终测试用例 + 覆盖率分析 |
| 第10步 | qa-output-validation | 输出验证报告.md | 防幻觉：事实核查/一致性/可执行性/来源追溯 |
| 第11步 | qa-expert-review（可选） | 专家评审报告.md | 需要质量把关时执行 |

**关键检查点**：
- 每个步骤完成后检查输出文件是否存在，不存在则重新执行该步骤
- 不得跳过步骤7（提示词生成）和步骤8（输出评审与补盲）

**覆盖率与缺口诚实性硬约束**（第9步测试报告 + 第10步输出验证必查）：
> ⚠️ **覆盖率必须标注口径**：若需求文档本身不完整（存在缺失模块/未定义流程），
> 覆盖率报告必须注明"基于现有需求文档的覆盖率"，
> 不得使用"全覆盖""100%"等绝对化表述——覆盖的是现有需求，不是完整业务闭环。
>
> ⚠️ **缺口必须同步标注**：需求评审发现缺失模块后，
> 测试报告、覆盖率报告、输出验证报告三处必须同步列出缺口清单，
> 不得只在一处提及、其余报告声称"全覆盖"掩盖缺口。
> 缺失模块不得编造需求或用例，只能标注"未覆盖+原因+建议补充"。

**测试用例.csv 格式硬约束**（第7步初版 + 第9步最终必查，交付用户直接可用）：
> ⚠️ **必须输出标准 CSV，不得用 `|` 竖线或制表符分隔**：
> 分隔符用半角逗号 `,`；字段内含逗号/双引号/换行时必须用双引号包裹并转义（RFC 4180）；
> 编码用 UTF-8 含 BOM（Excel 打开中文不乱码、正确分列）。
> 列结构固定 9 列：`用例编号,测试类型,功能模块,测试标题,用例级别,预置条件,测试步骤,预期结果,风险等级`。
> 表头必须存在，每条用例一行，不得用 Markdown 表格语法。

## 可选增强流程

根据用户需求和识别结果，可选择性调用：

### 按用例类型

```
├─ 接口测试：qa-api-testing（识别到"接口/API"关键词）
├─ Agent测试：qa-agent-testing（识别到"Agent/智能体"关键词）
├─ 性能测试：qa-specialized-testing（识别到"性能/压力"关键词）
└─ 安全测试：qa-specialized-testing（识别到"安全/渗透"关键词）
```

### 按平台类型

```
├─ 移动端App：加载 platform-mobile-app.md
├─ 小程序：加载 platform-mini-program.md
├─ 移动Web/H5：加载 platform-mobile-web.md
├─ 桌面应用：加载 platform-desktop.md
└─ PC Web：加载 platform-pc-web.md
```

### 按用户需求

```
├─ qa-test-estimation：工作量估算（用户需要排期时）
├─ qa-exploratory-testing：探索式测试（需要深度探索时）
├─ qa-expert-review：专家评审（需要质量把关时）
└─ qa-tech-debt-management：技术债务评估（需要评估债务时）
```

> 标准化输出模板和检查清单详见 [`references/format.md`](references/format.md)。

## 验收清单

工作流执行完成后检查：
- [ ] 用例类型是否识别正确？
- [ ] 平台专项是否加载？
- [ ] 需求评审是否完成？
- [ ] 需求解构是否完整？
- [ ] 风险评估是否识别？
- [ ] 启发式清单是否应用？
- [ ] 场景树是否覆盖全面？
- [ ] 边界分析是否深入？
- [ ] 组合策略是否合理？
- [ ] 状态转换是否清晰？
- [ ] 领域模型是否构建？
- [ ] 上下文包是否结构化？
- [ ] 提示词是否优化？
- [ ] 输出评审是否完成？
- [ ] 盲区补盲是否执行？
- [ ] 检查清单是否执行？
- [ ] 输出格式是否标准？
- [ ] 测试报告是否生成？
- [ ] 最终用例是否专家级？

---

## 技能集概览

**QA Test Skills** 是一个包含 48 个专家级子技能 + 1 个入口工作流的完整测试框架，覆盖从需求分析到测试设计、AI协作、执行监控、质量度量的完整测试生命周期。

### 技能分类

| 类别 | 数量 | 技能 |
|------|------|------|
| **AI协作** | 6个 | qa-input-validation, qa-ai-context-engineering, qa-ai-prompt-strategy, qa-ai-output-critique, qa-ai-blindspot-compensation, qa-output-validation |
| **需求分析** | 4个 | qa-requirement-review, qa-req-deconstruction, qa-scenario-tree, qa-domain-modeling |
| **深度设计** | 4个 | qa-boundary-deep-dive, qa-combination-strategy, qa-state-transition, qa-heuristic-checklist |
| **测试设计** | 4个 | qa-test-case-design, qa-critical-thinking, qa-question-framework, qa-risk-intuition |
| **执行洞察** | 4个 | qa-execution-observation, qa-bug-root-cause-analysis, qa-bug-reporting, qa-expert-review |
| **专项测试** | 8个 | qa-api-testing, qa-mobile-testing, qa-agent-testing, qa-specialized-testing, qa-exploratory-testing, qa-tech-debt-management, qa-test-estimation, qa-bug-lifecycle |
| **策略架构** | 14个 | qa-test-strategy-design, qa-release-risk-governance, qa-quality-metrics, qa-ci-cd-testing, qa-test-automation-arch, qa-tech-selection, qa-testability-advocacy, qa-test-data-engineering, qa-test-env-data, qa-shift-left, qa-shift-right, qa-test-leadership, qa-test-reporting, qa-regression-testing |
| **沟通传承** | 4个 | qa-stakeholder-communication, qa-code-review-for-test, qa-team-coaching, qa-retrospective |

## 使用方式

直接输入测试需求，AI 自动执行工作流：

```
请帮我测试这个项目：examples/ecommerce-project/docs/prd.md
```

也可单独触发某个子技能：

```
帮我分析这个场景的边界：[场景描述]
帮我设计测试用例：[需求描述]
```
