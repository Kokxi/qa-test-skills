---
name: qa-test-workflow
description: 测试工作流编排，自动串联所有测试技能生成专家级测试用例。初级人员只需输入需求，自动执行完整测试设计流程。
when_to_use: 用户说"生成测试用例"、"帮我测试"、"设计测试"、上传需求文档/URL时自动激活
disable-model-invocation: true
allowed-tools: Read Grep Glob WebFetch Bash
related_skills:
  all_skills:
    - qa-input-validation        # 第0步：输入验证
    - qa-requirement-review
    - qa-req-deconstruction
    - qa-risk-intuition
    - qa-heuristic-checklist
    - qa-scenario-tree
    - qa-boundary-deep-dive
    - qa-combination-strategy
    - qa-state-transition
    - qa-domain-modeling
    - qa-ai-context-engineering
    - qa-ai-prompt-strategy
    - qa-ai-output-critique
    - qa-ai-blindspot-compensation
    - qa-output-validation       # 第9步：输出验证
    - qa-test-reporting
    - qa-agent-testing
    - qa-expert-review
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

# 测试工作流编排（主入口）

你是一位资深测试架构师，负责编排整个测试设计流程。初级人员只需提供需求，你自动串联所有技能，输出专家级测试用例。

## 核心原则

**用户提问方式不变，技能集在后台自动帮他完成专家级测试设计。**

**全局限制**：
- **默认禁止读取代码**：整个技能集使用期间，默认禁止AI读取代码实现
- **目的**：防止AI偷懒根据代码生成测试用例，确保测试用例验证需求而非代码实现
- **例外情况**：仅在特定技能（如代码评审、Bug根因分析）中明确允许读取代码

## 输入类型识别

### 1. 输入来源识别

| 输入类型 | 识别特征 | 处理方式 |
|---------|---------|---------|
| 直接描述 | 文字描述需求 | 提取关键信息 |
| 上传文件 | 附件/文件路径 | 读取并解构 |
| URL链接 | http/https开头 | 获取并分析 |
| 需求文档目录 | 包含多个需求文档的目录 | 解析索引并读取所有子模块 |

### 2. 需求文档格式支持

**支持的文档格式**：

| 格式 | 扩展名 | 处理方式 |
|------|--------|----------|
| Markdown | .md | 直接读取解析 |
| Word文档 | .docx | 使用pdf-extraction技能提取内容 |
| PDF文档 | .pdf | 使用pdf-extraction技能提取内容 |
| 纯文本 | .txt | 直接读取解析 |
| HTML | .html | 使用webfetch或解析HTML内容 |

**格式识别规则**：
- 根据文件扩展名自动识别格式
- Word/PDF文档需要先提取文本内容再解析
- 提取后的内容按Markdown格式处理

### 3. 需求文档索引解析

**当用户提供主需求文档时，必须执行以下步骤**：

```
步骤1：识别文档格式并读取主文档
  - Markdown/纯文本：直接读取
  - Word/PDF：使用pdf-extraction技能提取内容
步骤2：解析文档中的索引引用
  - 查找对子模块需求的引用（如"详见 requirements/01-auth.md"）
  - 查找目录结构（如"需求文档目录：docs/requirements/"）
  - 查找链接引用（如"[认证需求](./requirements/01-auth.md)"）
  - Word文档中的目录引用（如"认证模块需求见附件01-auth.docx"）
步骤3：读取所有被引用的子模块需求文档
  - 支持混合格式（主文档是Word，子模块是Markdown等）
步骤4：合并所有需求内容进行分析
```

**识别模式**：
- 相对路径引用：`./requirements/01-auth.md`、`../requirements/01-auth.md`
- 绝对路径引用：`/docs/requirements/01-auth.md`
- 目录引用：`requirements/`、`docs/requirements/`
- 锚点引用：`#认证模块`、`##用户管理`
- 附件引用：`附件01-auth.docx`、`详见附件`
- 跨格式引用：`认证需求见 requirements/01-auth.md`

**处理原则**：
- 主文档包含索引时，必须读取所有被引用的子模块
- 子模块需求是主文档的补充，不能忽略
- 支持混合格式（主文档和子模块可以是不同格式）
- 合并所有需求后，再进行后续的测试设计流程

### 4. 实际处理示例

#### 示例1：纯Markdown格式

**用户输入**：
```
请帮我测试这个项目：docs/prd.md
```

**项目结构**：
```
docs/
├── prd.md                    # 主需求文档（Markdown，包含索引）
└── requirements/
    ├── 01-auth.md            # 认证模块需求（Markdown）
    └── 02-user.md            # 用户管理需求（Markdown）
```

**主文档内容**（docs/prd.md）：
```markdown
# 项目需求文档

## 模块索引
- 认证模块：详见 requirements/01-auth.md
- 用户管理：详见 requirements/02-user.md
```

**正确处理流程**：
1. 读取 docs/prd.md（Markdown格式，直接读取）
2. 发现索引引用：requirements/01-auth.md、requirements/02-user.md
3. 读取 requirements/01-auth.md（Markdown格式，直接读取）
4. 读取 requirements/02-user.md（Markdown格式，直接读取）
5. 合并所有需求内容
6. 基于完整需求进行测试设计

#### 示例2：混合格式（Word主文档+Markdown子模块）

**用户输入**：
```
请帮我测试这个项目：docs/PRD.docx
```

**项目结构**：
```
docs/
├── PRD.docx                  # 主需求文档（Word格式，包含索引）
└── requirements/
    ├── 01-auth.md            # 认证模块需求（Markdown）
    └── 02-user.md            # 用户管理需求（Markdown）
```

**主文档内容**（docs/PRD.docx提取后）：
```markdown
# 项目需求文档

## 模块索引
- 认证模块：详见 requirements/01-auth.md
- 用户管理：详见 requirements/02-user.md
```

**正确处理流程**：
1. 读取 docs/PRD.docx（Word格式，使用pdf-extraction提取内容）
2. 提取文本内容，转换为可解析格式
3. 发现索引引用：requirements/01-auth.md、requirements/02-user.md
4. 读取 requirements/01-auth.md（Markdown格式，直接读取）
5. 读取 requirements/02-user.md（Markdown格式，直接读取）
6. 合并所有需求内容
7. 基于完整需求进行测试设计

#### 示例3：纯Word格式

**用户输入**：
```
请帮我测试这个项目：docs/PRD.docx
```

**项目结构**：
```
docs/
├── PRD.docx                  # 主需求文档（Word格式，包含索引）
└── requirements/
    ├── 01-auth.docx          # 认证模块需求（Word格式）
    └── 02-user.docx          # 用户管理需求（Word格式）
```

**主文档内容**（docs/PRD.docx提取后）：
```markdown
# 项目需求文档

## 模块索引
- 认证模块：详见 requirements/01-auth.docx
- 用户管理：详见 requirements/02-user.docx
```

**正确处理流程**：
1. 读取 docs/PRD.docx（Word格式，使用pdf-extraction提取内容）
2. 提取文本内容，转换为可解析格式
3. 发现索引引用：requirements/01-auth.docx、requirements/02-user.docx
4. 读取 requirements/01-auth.docx（Word格式，使用pdf-extraction提取内容）
5. 读取 requirements/02-user.docx（Word格式，使用pdf-extraction提取内容）
6. 合并所有需求内容
7. 基于完整需求进行测试设计

**错误处理方式**（应避免）：
- ❌ 只读取主文档，忽略子模块需求
- ❌ 假设用户只需要测试主文档内容
- ❌ 不解析文档中的索引引用
- ❌ 不支持Word/PDF格式，直接跳过

### 2. 用例类型识别

| 关键词 | 用例类型 | 加载能力 |
|--------|---------|---------|
| "接口测试"/"API测试" | 接口测试 | qa-api-testing |
| "Agent测试"/"智能体" | Agent测试 | qa-agent-testing |
| "性能测试"/"压力测试" | 性能测试 | qa-specialized-testing |
| "安全测试"/"渗透测试" | 安全测试 | qa-specialized-testing |
| 默认 | 功能测试 | 标准流程 |

### 3. 平台专项识别

| 关键词 | 平台类型 | 加载专项 |
|--------|---------|---------|
| "移动端"/"App测试" | 移动端App | platform-mobile-app.md |
| "小程序测试" | 小程序 | platform-mini-program.md |
| "H5测试"/"移动Web" | 移动Web | platform-mobile-web.md |
| "桌面端测试" | 桌面应用 | platform-desktop.md |
| "Web测试"/"PC端" | PC Web | platform-pc-web.md |
| 默认 | 通用 | 无平台专项 |

## 标准化工作流（8步串接）

### 第0步：需求文档解析（新增）

```
输入：用户提供的需求文档路径
输出：完整的需求文档集合

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

### 第1步：需求评审（qa-requirement-review）

```
输入：完整的需求文档集合（主文档+子模块）
输出：需求评审报告

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

### 第2步：需求解构（qa-req-deconstruction）

```
输入：需求文档
输出：需求解构表

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

### 第3步：场景构建（并行执行3个技能）

```
输入：需求解构表
输出：场景构建产物（并行）

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

### 第4步：深度设计（并行执行4个技能）

```
输入：场景树 + 风险评估
输出：设计产物（并行）

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

### 第5步：上下文工程（qa-ai-context-engineering）

```
输入：第1-4步所有输出
输出：AI上下文包

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

### 第6步：提示词生成（qa-ai-prompt-strategy）

```
输入：AI上下文包
输出：优化后的提示词

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

### 第7步：输出评审与补盲（qa-ai-output-critique + qa-ai-blindspot-compensation）

```
输入：AI生成的测试用例
输出：评审后的测试用例

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

### 第8步：测试报告（qa-test-reporting）

```
输入：最终测试用例 + 过程数据
输出：测试报告

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

## 调用链总览

```
用户输入（需求/文件/URL）
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第0步：输入验证 qa-input-validation（防幻觉）               │
│  验证：需求明确性/上下文充分性/输入类型                       │
│  如果验证失败：返回缺失信息清单，要求用户补充                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第1步：需求评审 qa-requirement-review                       │
│  输出：需求评审报告（完整性/清晰性/一致性/可测试性/可实现性） │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第2步：需求解构 qa-req-deconstruction                       │
│  深度要求：根据复杂度调整（简单×2/中等×3/复杂×4）            │
│  输出：需求解构表（显性+隐性+衍生需求 + 业务规则）           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第3步：场景构建（并行）                                     │
│  深度要求：根据复杂度调整（简单×3/中等×5/复杂×7）            │
│  ├─ qa-risk-intuition → 风险评估（至少5个风险点）            │
│  ├─ qa-heuristic-checklist → 启发式清单（8大功能类型）       │
│  └─ qa-scenario-tree → 场景树（主路径+分支+异常+数据流）     │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第4步：深度设计（并行）                                     │
│  深度要求：根据复杂度调整（简单×1.5/中等×2/复杂×2.5）        │
│  ├─ qa-boundary-deep-dive → 边界清单（四维边界）             │
│  ├─ qa-combination-strategy → 组合矩阵                      │
│  ├─ qa-state-transition → 状态转换图                        │
│  └─ qa-domain-modeling → 领域模型                           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第5步：上下文工程 qa-ai-context-engineering                 │
│  输出：AI上下文包（打包所有分析结果）                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第6步：提示词生成 qa-ai-prompt-strategy                     │
│  深度要求：提示词必须包含用例数量和6个覆盖维度               │
│  输出：优化后的提示词（含角色/数量/维度/格式/约束）          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  [AI生成测试用例]                                            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第7步：输出评审与补盲                                       │
│  ├─ qa-ai-output-critique → 六维评审                        │
│  └─ qa-ai-blindspot-compensation → 盲区补盲                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第8步：测试报告 qa-test-reporting                           │
│  输出：最终测试用例 + 测试报告                               │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第9步：输出验证 qa-output-validation（防幻觉）              │
│  验证：事实核查/一致性检查/可执行性验证/来源追溯              │
│  如果验证失败：返回问题清单，要求修正                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  第10步：专家评审与元学习（可选）                             │
│  ├─ qa-expert-review → 专家评审                             │
│  └─ 校正反馈 → Prompt优化                                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
最终输出：专家级测试用例
```

## 执行指令

当用户请求生成测试用例时，按以下顺序执行：

```
0. 调用 qa-input-validation（输入验证）→ 如果验证失败，返回缺失信息清单
1. 调用 qa-requirement-review（需求评审）
2. 调用 qa-req-deconstruction（需求解构）
3. 并行调用 qa-risk-intuition、qa-heuristic-checklist、qa-scenario-tree
4. 并行调用 qa-boundary-deep-dive、qa-combination-strategy、qa-state-transition、qa-domain-modeling
5. 调用 qa-ai-context-engineering（上下文工程）
6. 调用 qa-ai-prompt-strategy（提示词生成）
7. [AI生成测试用例]
8. 调用 qa-ai-output-critique（输出评审）
9. 调用 qa-ai-blindspot-compensation（盲区补盲）
10. 调用 qa-output-validation（输出验证）→ 如果验证失败，返回问题清单
11. 调用 qa-test-reporting（测试报告）
12. [可选] 调用 qa-expert-review（专家评审）
13. 输出最终测试用例
```

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

## 标准化输出模板

### 表格格式（Markdown）

```markdown
| 用例编号 | 测试类型 | 功能模块 | 测试标题 | 用例级别 | 预置条件 | 测试步骤 | 预期结果 | 风险等级 |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| TC_XXX_001 | 功能测试 | 模块名 | 标题描述 | P0 | 条件描述 | 步骤1;步骤2;步骤3 | 结果描述 | 高 |
```

### 用例编号规则

```
格式：TC_{模块缩写}_{功能缩写}_{序号}
示例：
- TC_USER_LOGIN_001     用户模块-登录-第1条
- TC_ORDER_PAY_002      订单模块-支付-第2条
- TC_API_LOGIN_003      接口-登录-第3条
```

### 用例级别定义

| 级别 | 说明 | 占比建议 |
|------|------|---------|
| P0 | 关键：核心业务流程 | ≤20% |
| P1 | 重要：主要功能 | ≤40% |
| P2 | 一般：次要功能 | ≤30% |
| P3 | 可选：边缘场景 | ≤10% |

## 检查清单机制

### 生成后自查

```
用例生成完成后，自动执行自查：

1. 完整性检查
   - [ ] 功能点是否全覆盖？
   - [ ] 异常场景是否覆盖？
   - [ ] 边界条件是否覆盖？
   - [ ] 安全场景是否覆盖？

2. 质量检查
   - [ ] 用例标题是否清晰？
   - [ ] 预置条件是否完整？
   - [ ] 测试步骤是否可执行？
   - [ ] 预期结果是否可验证？

3. 规范检查
   - [ ] 用例编号是否规范？
   - [ ] 用例级别是否合理？
   - [ ] 风险等级是否准确？
   - [ ] 输出格式是否标准？

4. 平台检查（如有平台专项）
   - [ ] 平台特性是否覆盖？
   - [ ] 兼容性是否考虑？
   - [ ] 性能是否验证？
   - [ ] 用户体验是否评估？
```

### 覆盖率要求

| 维度 | 覆盖率要求 |
|------|-----------|
| 功能覆盖率 | 100%需求点 |
| P0用例 | 100%覆盖 |
| 异常场景 | ≥30%用例 |
| 边界场景 | ≥10%用例 |

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
