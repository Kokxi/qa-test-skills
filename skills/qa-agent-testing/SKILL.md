---
name: qa-agent-testing
description: >-
  当需要测试 AI Agent（智能体、聊天机器人、AI 助手）时使用此技能。Agent 测试和传统功能测试完全不同——你要测的不是"点按钮看结果"，而是它的推理链路、工具调用时机、幻觉率、Prompt 注入防护、角色边界保持和记忆一致性。安全三维（安全/高级安全/可控性）对任何 Agent 都是必选项，其余六维按 Agent 类型与风险追加。输出九维测试矩阵、工具调用与幻觉专项用例、安全审计清单。
  触发场景：Agent测试、智能体测试、AI助手、聊天机器人、Agent幻觉、Prompt注入、AI安全审计、LLM测试、需要测试AI Agent或评估AI行为时。 Use when the user asks about: AI agent, LLM, or chatbot testing — tool-calling behavior, hallucination rates, prompt injection defense, role-boundary keeping, and memory consistency.
license: MIT
allowed-tools: Read Grep Glob Bash WebFetch
metadata:
  slug: "qa-agent-testing"
  display-name: "Agent Testing"
  version: "1.8.0"
  when-to-use: "用户说\"Agent测试\"、\"智能体测试\"、\"AI助手\"、\"聊天机器人\"、\"Agent幻觉\"、\"Prompt注入\"、\"AI安全审计\"、\"LLM测试\"、需要测试AI Agent或评估AI行为时"
  related-skills: "{\"upstream\":[\"qa-specialized-testing\",\"qa-risk-intuition\"],\"downstream\":[\"qa-release-risk-governance\"]}"
  references: "[\"references/dimensions.md\",\"references/typical-cases.md\",\"references/scenarios.md\",\"assets/case-template.md\"]"
  input-format: "{\"required\":[{\"name\":\"Agent需求\",\"type\":\"string\",\"description\":\"AI Agent的功能需求和行为规范\"},{\"name\":\"风险评估\",\"type\":\"object\",\"description\":\"来自qa-risk-intuition的风险评估\"}],\"optional\":[{\"name\":\"测试策略\",\"type\":\"object\",\"description\":\"来自qa-test-strategy-design的测试策略\"}]}"
  output-format: "{\"traceability\":[\"每个Agent测试用例带唯一ID：TC_{模块缩写}_{功能缩写}_{序号}（如 TC_CSRF_SEC_001）\",\"关联需求ID：REQ-{需求模块缩写}-{序号}（REQ- 才是需求ID前缀，TC_ 是用例前缀）\"],\"structure\":[\"测试用例表格：固定 9 列（用例编号|测试类型|功能模块|测试标题|用例级别|预置条件|测试步骤|预期结果|风险等级）\",\"用例级别：P0≤20%（核心流程）/ P1≤40%（主要功能）/ P2≤30%（次要功能）/ P3≤10%（边缘场景）\",\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",\"占比取整：每维允许偏差 ≤1 条；用例数少时以每维至少 1 条兜底并注明实际分布\"],\"agent_test_plan\":\"Agent测试方案\",\"tool_call_tests\":\"工具调用测试用例\",\"hallucination_checks\":\"幻觉检测清单\",\"safety_audit\":\"安全审计项目\",\"reasoning_validation\":\"推理链路验证\"}"
  error-recovery-guidance: "{\"on_failure\":\"Agent行为异常时回退到确定性测试方案，配合人工验证\",\"retry_behavior\":\"调整测试参数后重新执行Agent测试\"}"
  categories: "[\"Development\",\"Automation\",\"Agents\"]"
  depth-requirement: "{\"reference_value\":\"见正文「深度要求」表：简单Agent=30条 / 中等Agent=50条 / 复杂Agent=80条（绝对条数，非乘数）\",\"minimum\":\"安全三维（安全测试/高级安全测试/可控性）为必选；其余六维按 Agent 类型速查表的必测维选取，未覆盖维度须在覆盖率报告标注原因\"}"
---

# AI Agent 测试专项

## 核心原则

Agent 测试的核心——验证 AI 决策的**正确性、安全性、可控性**。功能能不能用只是及格线；
能不能被诱导、能不能被叫停、会不会瞎编，才是这个领域特有的风险面。

## 1. 先定位 Agent 类型（决定重心）

| Agent 类型 | 典型代表 | 必测维度 | 重点关注 |
|-----------|---------|---------|---------|
| **对话助手型** | AI客服/智能导购/知识问答 | 功能+安全+高级安全+可控性+幻觉 | 意图识别、上下文记忆、幻觉控制、多轮诱导 |
| **任务执行型** | 工单处理/审批流转/数据录入 | 功能+工具调用+可控性+边界 | 工具选择、参数生成、执行顺序、人工确认 |
| **数据分析型** | BI助手/报表生成/趋势分析 | 功能+幻觉+推理+安全 | 数据准确性、来源归因、逻辑正确性、越权查询 |
| **自主决策型** | 风控系统/资源调度/智能运维 | 安全+高级安全+可控性+推理+工具调用 | 间接注入、权限边界、HITL、决策归因 |

> **接了 RAG 的 Agent 必须测间接注入**：检索到的文档/网页内容本身就是攻击面，
> 用户没发恶意指令不代表没有注入。只测用户直发注入是这类 Agent 最常见的漏测。

## 2. 九维覆盖要求

| 维度 | 占比 | 说明 |
|------|------|------|
| 功能测试 | 25% | 任务执行/决策/交互/工具调用 |
| 安全测试 | 15% | Prompt注入/越权/敏感信息 |
| 高级安全测试 | 12% | 间接注入/多轮诱导/编码绕过 |
| 边界测试 | 10% | 输入/能力/并发边界 |
| 可控性 | 12% | 中止/人工确认/权限边界/速率限制 |
| 可靠性测试 | 8% | 稳定性/容错/降级 |
| 幻觉与事实性 | 8% | 事实核查/来源归因/RAG准确性 |
| 推理链路 | 5% | 可解释性/逻辑/自纠错 |
| 工具调用测试 | 5% | 参数生成/工具链编排/副作用 |

**必选与选配**：
- **必选三维**（任何 Agent 都不能省）：安全测试、高级安全测试、可控性 —— 这三维出问题就是安全事件
- **选配六维**：按上表"必测维度"列选取，其余按风险评估追加
- 未覆盖的维度必须在覆盖率报告写"未覆盖 + 原因"，**不得静默省略**

> 占比是分配目标不是硬门槛：条数必须取整。分配顺序见 `references/dimensions.md` 末尾的「占比取整规则」
> （先保 P0 所属维 → 其余向下取整 → 每维允许偏差 ≤1 条 → 用例少时每维至少 1 条兜底）。

## 3. 深度要求

| 复杂度 | 用例数要求 | 说明 |
|--------|-----------|------|
| 简单Agent | 30 条 | 单一任务 Agent，无工具或单工具 |
| 中等Agent | 50 条 | 多任务 Agent，多工具 |
| 复杂Agent | 80 条 | 多工具 + 多轮对话 + RAG 的组合 |

## 4. 加载时机

**需要时才读，不要一上来全读**：

| 什么时候读 | 读哪个 |
|-----------|--------|
| 要展开某一维的测试范围，或交付前逐项自检 | [`references/dimensions.md`](references/dimensions.md)（9 维详图 + 9 组检查清单 + 取整规则） |
| 要挑现成用例起点 | [`references/typical-cases.md`](references/typical-cases.md)（37 条，按维分布 + 级别/风险建议） |
| 用户描述的情况命中特定 Agent 形态或风险 | [`references/scenarios.md`](references/scenarios.md)（8 个场景，校正测试重心） |
| 要写用例表 | [`assets/case-template.md`](assets/case-template.md)（9 列模板 + 填写要求） |

## 5. 测试方案输出结构

```text
1. Agent 类型识别   → 判定属于哪一类（对话/任务/分析/决策），列出判定理由
2. 必测维度清单     → 必选三维 + 速查表必测维 + 风险追加维，标注哪些维度未覆盖及原因
3. 测试范围详解     → 每个选中维度的核心测试点（读 dimensions.md）
4. 典型用例参考     → 从 37 条典型用例中选取适用的（读 typical-cases.md）
5. 安全与可控性专项 → 注入 / 工具安全 / HITL 等 Agent 特有风险
6. 风险提示         → 基于场景的高风险区域预警
```

## 6. 交付前自检

- [ ] 必选三维（安全/高级安全/可控性）均有用例
- [ ] 百分比分配取整后每维偏差 ≤1 条；用例数 <30 时已注明实际分布
- [ ] 用例编号为 `TC_{模块}_{功能}_{序号}`，同批不重号
- [ ] P0-P3 占比符合要求
- [ ] 覆盖率已标注口径，无"全覆盖/100%"绝对化表述
- [ ] 未覆盖维度已写明"未覆盖 + 原因"
- [ ] Agent 类型判定的理由已列出

**机器校验**（列数、编号唯一性、级别取值、占比、覆盖率措辞）：

```bash
python scripts/validate_testcase_table.py <用例文件>
```
