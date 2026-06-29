# 工作流详细执行指南

> 本文档是 `SKILL.md` 中标准化工作流的详细展开，包含每步的输入/输出/执行内容/输出格式。
> 需要在执行某步时遇到疑问时查阅，不作为主流程的直接执行指令。

---

## 第0步：需求文档解析

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

---

## 第1步：需求评审（qa-requirement-review）

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

---

## 第2步：需求解构（qa-req-deconstruction）

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

---

## 第3步：场景构建（并行执行3个技能）

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

---

## 第4步：深度设计（并行执行4个技能）

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

---

## 第5步：回归策略设计（qa-regression-testing）

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

---

## 第6步：上下文工程（qa-ai-context-engineering）

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

---

## 第7步：提示词生成（qa-ai-prompt-strategy）

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

⚠️ **不得跳过此步骤**

---

## 第8步：输出评审与补盲（qa-ai-output-critique + qa-ai-blindspot-compensation）

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

⚠️ **不得跳过此步骤**

---

## 第9步：测试报告（qa-test-reporting）

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

---

## 执行指令（速查）

```
 0. qa-input-validation                      → 输入验证报告.md
 1. qa-requirement-review                     → 需求评审报告.md
 2. qa-req-deconstruction                     → 需求解构表.md
 3. [并行] qa-risk-intuition                  → 风险评估.md
    [并行] qa-heuristic-checklist             → 启发式清单.md
    [并行] qa-scenario-tree                   → 场景树.md
 4. [并行] qa-boundary-deep-dive              → 边界清单.md
    [并行] qa-combination-strategy            → 组合矩阵.md
    [并行] qa-state-transition                → 状态转换图.md
    [并行] qa-domain-modeling                 → 领域模型.md
 5. qa-regression-testing                     → 回归策略.md
 6. qa-ai-context-engineering                 → AI上下文包.md
 7. qa-ai-prompt-strategy                     → AI提示词.md
 → [AI生成测试用例]                            → 测试用例_初版.csv
 8. qa-ai-output-critique                     → 用例评审报告.md
    qa-ai-blindspot-compensation              → 盲区补偿用例.md
 9. qa-test-reporting                         → 测试报告.md、测试用例.csv
10. qa-output-validation                      → 输出验证报告.md
11. [可选] qa-expert-review                   → 专家评审报告.md
```
