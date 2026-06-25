---
name: qa-test-skills
description: >-
  从需求文档自动生成结构化测试用例，覆盖功能测试、边界分析、组合测试和回归测试全流程。自动串联48个专家级子技能，按10步工作流编排执行。适用于：上传需求文档（PRD/Word/PDF/URL）需要完整测试用例时、不知道如何设计测试场景或担心遗漏边界条件时、需要AI评审测试输出并补充测试盲区时。每个步骤都有独立技能支撑，输出格式统一、需求可追溯、覆盖率可量化。
when_to_use: >-
  用户说"生成测试用例"、"帮我测试"、"设计测试"、"上传需求"、"开始测试"、上传需求文档/URL时自动激活，
  需要完整测试流程时，想浏览技能集目录、了解QA Test Skills包含哪些技能、查看技能分类说明、获取安装指引时
disable-model-invocation: true
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

**用户提问方式不变，技能集在后台自动帮他完成专家级测试设计。**

> 强制执行规则详见 [`references/enforcement.md`](references/enforcement.md)。

> 输入识别、路由规则和可选增强流程详见 [`references/routing.md`](references/routing.md)。

## 标准化工作流（9步串接）

**⚠️ 强制要求：每个步骤必须产出明确的输出文件，不得跳过任何步骤**

### 第0步：需求文档解析

```
输入：用户提供的需求文档路径
输出：完整的需求文档集合
输出文件：需求文档集合（合并后的内容）

执行内容：
1. 读取主需求文档
2. 解析文档中的索引引用
3. 识别子模块需求文档路径
4. 读取所有子模块需求文档
5. 合并需求内容
6. 构建完整的需求上下文

处理逻辑：
if 主文档包含索引引用:
    for each 引用的子模块:
        读取子模块需求文档
        合并到需求上下文
else:
    直接使用主文档内容
```

**关键检查点**：
- 主文档是否包含对子模块的引用？
- 引用的子模块文件是否存在？
- 是否有遗漏的需求文档？

**必须产出**：需求文档集合（合并后的内容）

### 第1步：需求评审（qa-requirement-review）

```
输入：完整的需求文档集合（主文档+子模块）
输出：需求评审报告
输出文件：需求评审报告.md

执行内容：
1. 评审需求完整性
2. 评审需求清晰性
3. 评审需求一致性
4. 评审可测试性
5. 评审可实现性
6. 输出问题清单

输出格式：
{
  "review_result": "通过/有条件通过/不通过",
  "completeness": {...},
  "clarity": {...},
  "consistency": {...},
  "testability": {...},
  "feasibility": {...},
  "issues": [...]
}
```

**必须产出**：需求评审报告.md

### 第2步：需求解构（qa-req-deconstruction）

```
输入：需求文档
输出：需求解构表
输出文件：需求解构表.md

执行内容：
1. 提取显性需求
2. 挖掘隐性需求
3. 推导衍生需求
4. 五维拆解（输入/操作/状态/输出/规则）

输出格式：
{
  "explicit_requirements": [...],
  "implicit_requirements": [...],
  "derived_requirements": [...],
  "five_dimensions": {...}
}
```

**必须产出**：需求解构表.md

### 第3步：场景构建（并行执行3个技能）

```
输入：需求解构表
输出：场景构建产物（并行）
输出文件：风险评估.md、启发式清单.md、场景树.md

并行执行：
├─ qa-risk-intuition → 风险评估
├─ qa-heuristic-checklist → 启发式清单
└─ qa-scenario-tree → 场景树

输出格式：
{
  "risk_assessment": {...},
  "heuristic_checklist": {...},
  "scenario_tree": {...}
}
```

**必须产出**：风险评估.md、启发式清单.md、场景树.md

### 第4步：深度设计（并行执行4个技能）

```
输入：场景树 + 风险评估
输出：设计产物（并行）
输出文件：边界清单.md、组合矩阵.md、状态转换图.md、领域模型.md

并行执行：
├─ qa-boundary-deep-dive → 边界清单
├─ qa-combination-strategy → 组合矩阵
├─ qa-state-transition → 状态转换图
└─ qa-domain-modeling → 领域模型

输出格式：
{
  "boundary_analysis": {...},
  "combination_strategy": {...},
  "state_transition": {...},
  "domain_model": {...}
}
```

**必须产出**：边界清单.md、组合矩阵.md、状态转换图.md、领域模型.md

### 第5步：回归策略设计（qa-regression-testing）

```
输入：变更分析结果 + 风险评估 + 场景树
输出：回归测试方案
输出文件：回归策略.md

执行内容：
1. 确定回归级别（冒烟/核心/全量）
2. 选择筛选策略（变更驱动/风险驱动/时间驱动）
3. 生成回归用例清单
4. 输出未覆盖的风险区域报告
```

**必须产出**：回归策略.md

### 第6步：上下文工程（qa-ai-context-engineering）

```
输入：第1-5步所有输出
输出：AI上下文包
输出文件：AI上下文包.md

执行内容：
1. 打包所有分析结果
2. 构建上下文金字塔
3. 格式化为结构化输入

输出格式：
{
  "business_context": {...},
  "functional_context": {...},
  "technical_context": {...},
  "output_requirements": {...}
}
```

**必须产出**：AI上下文包.md

### 第7步：提示词生成（qa-ai-prompt-strategy）

```
输入：AI上下文包
输出：优化后的提示词
输出文件：AI提示词.md

执行内容：
1. 选择最佳提示词模式
2. 注入上下文
3. 生成最终提示词

输出格式：
{
  "prompt_mode": "结构化输出模式",
  "final_prompt": "..."
}
```

**必须产出**：AI提示词.md（⚠️ 不得跳过此步骤）

### 第8步：输出评审与补盲（qa-ai-output-critique + qa-ai-blindspot-compensation）

```
输入：AI生成的测试用例
输出：评审后的测试用例
输出文件：用例评审报告.md、盲区补偿用例.md

执行内容：
1. 六维评审（完整性/深度/风险/一致性/可实现性/冗余度）
2. 假设挖掘
3. 盲区补盲（时序/并发/资源/状态/数据/第三方）

输出格式：
{
  "review_result": {...},
  "blindspot_compensation": {...},
  "final_test_cases": [...]
}
```

**必须产出**：用例评审报告.md、盲区补偿用例.md（⚠️ 不得跳过此步骤）

### 第9步：测试报告（qa-test-reporting）

```
输入：最终测试用例 + 过程数据
输出：测试报告
输出文件：测试报告.md、测试用例.csv

执行内容：
1. 生成测试用例清单
2. 统计覆盖情况
3. 标注风险区域
4. 输出测试报告

输出格式：
{
  "test_case_summary": {...},
  "coverage_statistics": {...},
  "risk_areas": [...],
  "test_report": "..."
}
```

**必须产出**：测试报告.md、测试用例.csv

## 调用链总览

**⚠️ 强制要求：每个步骤必须产出明确的输出文件，不得跳过任何步骤**

```
用户输入（需求/文件/URL）
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第0步：输入验证 qa-input-validation（防幻觉）               │
│  验证：需求明确性/上下文充分性/输入类型                       │
│  如果验证失败：返回缺失信息清单，要求用户补充                 │
│  输出文件：输入验证报告.md                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第1步：需求评审 qa-requirement-review                       │
│  输出：需求评审报告（完整性/清晰性/一致性/可测试性/可实现性） │
│  输出文件：需求评审报告.md                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第2步：需求解构 qa-req-deconstruction                       │
│  深度要求：根据复杂度调整（简单×2/中等×3/复杂×4）            │
│  输出：需求解构表（显性+隐性+衍生需求 + 业务规则）           │
│  输出文件：需求解构表.md                                      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第3步：场景构建（并行）                                     │
│  深度要求：根据复杂度调整（简单×3/中等×5/复杂×7）            │
│  ├─ qa-risk-intuition → 风险评估（至少5个风险点）            │
│  ├─ qa-heuristic-checklist → 启发式清单（8大功能类型）       │
│  └─ qa-scenario-tree → 场景树（主路径+分支+异常+数据流）     │
│  输出文件：风险评估.md、启发式清单.md、场景树.md              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第4步：深度设计（并行）                                     │
│  ├─ qa-boundary-deep-dive → 边界清单                        │
│  ├─ qa-combination-strategy → 组合矩阵                      │
│  ├─ qa-state-transition → 状态转换图                        │
│  └─ qa-domain-modeling → 领域模型                           │
│  输出文件：边界清单.md、组合矩阵.md、状态转换图.md、领域模型.md │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第5步：回归策略设计 qa-regression-testing                   │
│  输出：回归测试方案（分级策略 + 用例清单 + 执行计划）         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第6步：上下文工程 qa-ai-context-engineering                 │
│  输出：AI上下文包（打包所有分析结果）                        │
│  输出文件：AI上下文包.md                                      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第7步：提示词生成 qa-ai-prompt-strategy                     │
│  输出：优化后的提示词（含角色/数量/维度/格式/约束）          │
│  输出文件：AI提示词.md（⚠️ 不得跳过此步骤）                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  [AI生成测试用例]                                            │
│  输出文件：测试用例_初版.csv                                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第8步：输出评审与补盲                                       │
│  ├─ qa-ai-output-critique → 六维评审                        │
│  └─ qa-ai-blindspot-compensation → 盲区补盲                 │
│  输出文件：用例评审报告.md、盲区补偿用例.md                  │
│  ⚠️ 不得跳过此步骤                                          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第9步：测试报告 qa-test-reporting                           │
│  输出：最终测试用例 + 测试报告                               │
│  输出文件：测试报告.md、测试用例.csv                         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第10步：输出验证 qa-output-validation（防幻觉）             │
│  验证：事实核查/一致性检查/可执行性验证/来源追溯             │
│  如果验证失败：返回问题清单，要求修正                        │
│  输出文件：输出验证报告.md                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第11步：专家评审与元学习（可选）                             │
│  ├─ qa-expert-review → 专家评审                             │
│  └─ 校正反馈 → Prompt优化                                   │
│  输出文件：专家评审报告.md（如执行）                          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
最终输出：专家级测试用例 + 完整报告文件集
```

## 执行指令

**⚠️ 强制要求：必须严格按照以下顺序执行，每步必须产出输出文件，不得跳过任何步骤**

当用户请求生成测试用例时，按以下顺序执行：

```
0. 调用 qa-input-validation（输入验证）→ 如果验证失败，返回缺失信息清单
   输出文件：输入验证报告.md

1. 调用 qa-requirement-review（需求评审）
   输出文件：需求评审报告.md

2. 调用 qa-req-deconstruction（需求解构）
   输出文件：需求解构表.md

3. 并行调用 qa-risk-intuition、qa-heuristic-checklist、qa-scenario-tree
   输出文件：风险评估.md、启发式清单.md、场景树.md

4. 并行调用 qa-boundary-deep-dive、qa-combination-strategy、qa-state-transition、qa-domain-modeling
   输出文件：边界清单.md、组合矩阵.md、状态转换图.md、领域模型.md

5. 调用 qa-regression-testing（回归策略设计）
   输出文件：回归策略.md

6. 调用 qa-ai-context-engineering（上下文工程）
   输出文件：AI上下文包.md

7. 调用 qa-ai-prompt-strategy（提示词生成）
   输出文件：AI提示词.md（⚠️ 不得跳过此步骤）

8. [AI生成测试用例]
   输出文件：测试用例_初版.csv

9. 调用 qa-ai-output-critique（输出评审）
   输出文件：用例评审报告.md

10. 调用 qa-ai-blindspot-compensation（盲区补盲）
    输出文件：盲区补偿用例.md

11. 调用 qa-output-validation（输出验证）→ 如果验证失败，返回问题清单
    输出文件：输出验证报告.md

12. 调用 qa-test-reporting（测试报告）
    输出文件：测试报告.md、测试用例.csv

13. [可选] 调用 qa-expert-review（专家评审）
    输出文件：专家评审报告.md

14. 输出最终测试用例
    输出文件：最终测试用例.csv
```

**关键检查点**：
- 每个步骤完成后必须检查输出文件是否存在
- 如果输出文件不存在，必须重新执行该步骤
- 不得跳过任何步骤，特别是步骤7（提示词生成）和步骤9-10（输出评审与补盲）

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

## 安装方式

```bash
# 方式一：npx skills（推荐）
npx skills add Kokxi/qa-test-skills

# 方式二：ClawHub 插件
openclaw plugins install clawhub:@kokxi/qa-test-skills

# 方式三：GitHub 克隆
git clone https://github.com/Kokxi/qa-test-skills.git
cd qa-test-skills
/plugin dir ./qa-test-skills
```

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
