# QA Test Skills 技能分类手册

> 说明：本文档基于各技能 `SKILL.md` frontmatter 的 `upstream/downstream` 依赖标注与正文输出定义整理，
> 用于帮助用户理解：哪些技能可单独调用、哪些需要前置输入、哪些产出文件、哪些是经验型无输出。
> 覆盖范围：入口工作流 `qa-test-skills` + 48 个专家级子技能（共 49 个）。

---

## 一、总览

| 分类维度 | 数量 | 说明 |
|----------|:---:|------|
| 可单独使用（无前置依赖） | 8 | 用户直接说关键词即可触发，无需其他技能产物 |
| 依赖上游输入 | 40 | 需要前置技能的分析结果作为输入（工作流中按步骤串联） |
| 有明确文件输出 | 41 | 产出独立文件（报告/清单/表/图/CSV 等） |
| 经验型无文件输出 | 7 | 认知/思维/方法论型，输出是给 AI 的判断与建议，不落独立文件 |

---

## 二、按"可单独使用 / 依赖上游"分类

### 可单独使用（8 个）——无 frontmatter 上游输入标注，用户可直接触发

| 技能 | 典型触发 | 说明 |
|------|---------|------|
| `qa-input-validation` | "解析这份需求" | 直接读取需求文档，无需前置 |
| `qa-critical-thinking` | "帮我批判性分析" | 纯思维型，无输入依赖 |
| `qa-question-framework` | "帮我提问" | 提问框架，无输入依赖 |
| `qa-heuristic-checklist` | "支付功能测什么" | 内置默认清单，无复盘数据也可用 |
| `qa-risk-intuition` | "风险在哪里" | 风险直觉，直接对需求/代码评估 |
| `qa-exploratory-testing` | "帮我探索测试" | 可独立对被测对象执行 |
| `qa-bug-reporting` | "记录这个Bug" | 直接生成标准 Bug 报告 |
| `qa-bug-lifecycle` | "缺陷生命周期" | 缺陷管理流程，独立可用 |

### 依赖上游输入（40 个）——需要前置技能产物作为输入

| 技能 | 上游输入（# 输入标注） | 前置产出 |
|------|------------------------|---------|
| `qa-requirement-review` | qa-input-validation, qa-critical-thinking, qa-question-framework | 需求文档集合 |
| `qa-req-deconstruction` | qa-requirement-review | 需求评审报告 |
| `qa-scenario-tree` | qa-req-deconstruction | 需求解构表 |
| `qa-boundary-deep-dive` | qa-scenario-tree | 场景树 |
| `qa-combination-strategy` | qa-scenario-tree | 场景树 |
| `qa-state-transition` | qa-scenario-tree | 场景树 |
| `qa-domain-modeling` | qa-scenario-tree | 场景树 |
| `qa-regression-testing` | qa-risk-intuition, qa-test-case-design | 风险清单/用例集 |
| `qa-ai-context-engineering` | （工作流第6步） | 前 5 步全部分析产物 |
| `qa-ai-prompt-strategy` | qa-ai-context-engineering | AI 上下文包 |
| `qa-ai-output-critique` | qa-ai-prompt-strategy | AI 提示词/初版用例 |
| `qa-ai-blindspot-compensation` | qa-ai-output-critique | 用例评审报告 |
| `qa-test-reporting` | qa-quality-metrics, qa-bug-lifecycle, qa-execution-observation | 度量数据/缺陷/观察记录 |
| `qa-output-validation` | qa-ai-output-critique, qa-ai-blindspot-compensation | 用例评审/补盲结果 |
| `qa-expert-review` | qa-ai-output-critique, qa-ai-blindspot-compensation | 用例评审/补盲结果 |
| `qa-test-case-design` | qa-req-deconstruction, qa-boundary-deep-dive, qa-scenario-tree | 解构表/边界/场景树 |
| `qa-execution-observation` | qa-scenario-tree, qa-boundary-deep-dive | 场景树/边界清单 |
| `qa-bug-root-cause-analysis` | qa-execution-observation | 观察记录 |
| `qa-retrospective` | qa-bug-root-cause-analysis, qa-quality-metrics, qa-bug-lifecycle | 根因/度量/缺陷数据 |
| `qa-quality-metrics` | qa-release-risk-governance, qa-bug-lifecycle | 发布风险/缺陷数据 |
| `qa-api-testing` | qa-test-automation-arch, qa-req-deconstruction | 自动化架构/解构表 |
| `qa-mobile-testing` | qa-test-automation-arch, qa-specialized-testing | 自动化架构/专项 |
| `qa-agent-testing` | qa-specialized-testing, qa-risk-intuition | 专项清单/风险 |
| `qa-specialized-testing` | qa-risk-intuition, qa-test-strategy-design | 风险/策略 |
| `qa-ci-cd-testing` | qa-tech-selection, qa-test-strategy-design | 技术选型/策略 |
| `qa-code-review-for-test` | qa-boundary-deep-dive, qa-risk-intuition | 边界/风险 |
| `qa-release-risk-governance` | qa-test-strategy-design, qa-risk-intuition | 策略/风险 |
| `qa-shift-left` | qa-req-deconstruction, qa-testability-advocacy | 解构表/可测试性 |
| `qa-shift-right` | qa-release-risk-governance, qa-ci-cd-testing | 发布风险/CI |
| `qa-stakeholder-communication` | qa-bug-reporting, qa-release-risk-governance, qa-quality-metrics | Bug/风险/度量 |
| `qa-state-transition` | qa-scenario-tree | 场景树 |
| `qa-team-coaching` | qa-retrospective, qa-heuristic-checklist | 复盘/清单 |
| `qa-tech-debt-management` | qa-test-automation-arch, qa-quality-metrics | 架构/度量 |
| `qa-tech-selection` | qa-test-strategy-design | 测试策略 |
| `qa-test-automation-arch` | qa-tech-selection, qa-test-strategy-design | 选型/策略 |
| `qa-test-data-engineering` | qa-test-env-data, qa-req-deconstruction | 环境/解构表 |
| `qa-test-env-data` | qa-testability-advocacy, qa-test-strategy-design | 可测试性/策略 |
| `qa-test-estimation` | qa-req-deconstruction, qa-risk-intuition | 解构表/风险 |
| `qa-test-leadership` | qa-team-coaching, qa-retrospective | 赋能/复盘 |
| `qa-test-strategy-design` | qa-risk-intuition, qa-req-deconstruction | 风险/解构表 |
| `qa-testability-advocacy` | qa-quality-metrics, qa-execution-observation | 度量/观察 |

> 注：`qa-ai-context-engineering` 在 frontmatter 无显式 # 输入标注，但按 12 步工作流语义它是第 6 步、
> 打包前 5 步全部分析产物，故归入依赖型。

---

## 三、按"有输出 / 经验型无输出"分类

### 有明确文件输出（41 个）——产出独立文件（报告/清单/表/图/CSV）

| 技能 | 输出产物 |
|------|---------|
| `qa-input-validation` | 需求文档集合 |
| `qa-requirement-review` | 需求评审报告 |
| `qa-req-deconstruction` | 需求解构表（显性+隐性+衍生清单） |
| `qa-scenario-tree` | 场景树 |
| `qa-boundary-deep-dive` | 边界清单 |
| `qa-combination-strategy` | 组合矩阵 |
| `qa-state-transition` | 状态转换表/图 |
| `qa-domain-modeling` | 领域模型（含状态转换表） |
| `qa-regression-testing` | 回归策略/回归风险报告 |
| `qa-risk-intuition` | 风险评估报告（RISK 编号清单） |
| `qa-heuristic-checklist` | 功能类型测试要点清单 |
| `qa-ai-context-engineering` | AI 上下文包 |
| `qa-ai-prompt-strategy` | AI 提示词（结构化 Markdown 表） |
| `qa-ai-output-critique` | 用例评审报告 |
| `qa-ai-blindspot-compensation` | 补盲报告/盲区补偿用例 |
| `qa-test-reporting` | 测试报告 + 测试用例.csv |
| `qa-output-validation` | 输出验证报告 |
| `qa-expert-review` | 专家评审报告 |
| `qa-test-case-design` | 测试用例集（初版） |
| `qa-api-testing` | 接口测试用例/兼容性影响分析报告 |
| `qa-mobile-testing` | 移动端测试要点/执行记录 |
| `qa-agent-testing` | 安全漏洞报告/工具调用安全报告 |
| `qa-specialized-testing` | 专项测试清单/漏洞报告 |
| `qa-bug-reporting` | 标准格式 Bug 报告 |
| `qa-bug-lifecycle` | 缺陷状态流转记录 |
| `qa-bug-root-cause-analysis` | 根因分析结论 |
| `qa-execution-observation` | 执行观察记录 |
| `qa-quality-metrics` | 质量度量报告 |
| `qa-release-risk-governance` | 发布风险评估/治理清单 |
| `qa-ci-cd-testing` | CI/CD 测试策略/集成验证记录 |
| `qa-code-review-for-test` | 代码评审意见清单 |
| `qa-shift-left` | 左移检查清单/阶段性介入记录 |
| `qa-shift-right` | 线上验证清单/灰度策略 |
| `qa-stakeholder-communication` | 干系人沟通要点/报告摘要 |
| `qa-tech-debt-management` | 技术债清单/偿还计划 |
| `qa-tech-selection` | 技术评估报告/推荐方案 |
| `qa-test-automation-arch` | 自动化测试架构方案 |
| `qa-test-data-engineering` | 测试数据方案/数据集 |
| `qa-test-env-data` | 测试环境/数据需求清单 |
| `qa-test-estimation` | 测试工作量估算表 |
| `qa-testability-advocacy` | 可测试性评估报告/改造建议 |

### 经验型无文件输出（7 个）——认知/思维/方法论型，输出给 AI 的判断与建议

| 技能 | 输出形态 | 为什么无文件 |
|------|---------|-------------|
| `qa-critical-thinking` | 思维盲区清单（内嵌思考） | 明确声明"质疑思维，不产出唯一ID"；输出是发现与挑战，关联到需求/场景 ID |
| `qa-question-framework` | 结构化提问清单 | 明确声明"本技能设计提问，不产出唯一ID"；输出是问题集，供其他技能使用 |
| `qa-exploratory-testing` | 探索发现/建议 | 探索过程产出发现，不强制落独立文件 |
| `qa-test-leadership` | 测试策略/团队计划/质量报告方向 | 产出的是管理方向与决策建议，不固定文件格式 |
| `qa-team-coaching` | 培训材料清单/辅导建议 | 输出赋能建议，供人使用，不强制文件 |
| `qa-retrospective` | 复盘结论/改进项方向 | 产出改进建议（复盘报告可由 qa-test-reporting 汇总），自身不固定文件 |
| `qa-test-strategy-design` | 测试策略方向 | 输出策略决策建议，具体策略报告由 qa-test-reporting 承载 |

> 说明：经验型技能并非"没有输出"，而是**输出不落独立文件**——它们产生判断、清单、建议，
> 作为其他有文件输出技能的输入，或直接呈现给用户/AI 使用。

---

## 四、依赖关系速查（12 步工作流主线）

```
qa-input-validation → qa-requirement-review → qa-req-deconstruction
  → (qa-risk-intuition, qa-heuristic-checklist, qa-scenario-tree) 并行
  → (qa-boundary-deep-dive, qa-combination-strategy, qa-state-transition, qa-domain-modeling) 并行
  → qa-regression-testing → qa-ai-context-engineering → qa-ai-prompt-strategy
  → qa-test-case-design（AI 生成初版用例）
  → (qa-ai-output-critique, qa-ai-blindspot-compensation) 并行
  → qa-test-reporting（测试报告 + 测试用例.csv）
  → qa-output-validation → qa-expert-review（可选）
```

---

## 五、使用建议

1. **完整工作流**：直接说"帮我测试这个项目"，入口 `qa-test-skills` 自动编排 48 个子技能按 12 步执行
2. **单独调用**：可单独使用的 8 个技能（输入解析/批判思维/提问框架/启发式清单/风险直觉/探索测试/Bug报告/缺陷生命周期）随时可用
3. **依赖技能**：40 个依赖型技能建议在完整工作流中使用，或先手动准备其上游产物（如先跑 `qa-requirement-review` 再跑 `qa-req-deconstruction`）
4. **经验型技能**：无文件输出，用于提升 AI 的判断质量，通常作为流程中的"思考环节"而非"产出环节"
