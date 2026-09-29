# 技能内容拆分约定（SKILL.md / references / assets / scripts）

> 依据 [Agent Skills 规范](https://agentskills.io/specification#progressive-disclosure) 的渐进式披露机制。
> `qa-api-testing` 与 `qa-agent-testing` 是按本约定重组的样板，其余技能照此办。

## 为什么要拆

技能有三种加载时机，混在一起就是浪费：

| 时机 | 成本 | 谁决定 |
|------|------|--------|
| **Discovery** | 每个会话启动，所有技能都付 | 客户端 |
| **Activation** | 技能被触发时 | 客户端 |
| **Execution** | 执行过程中按需 | 技能自己 |

`SKILL.md` 正文属于 **Activation** —— 技能一触发就整篇进上下文。所以正文的每一行都在和
用户的对话历史抢注意力。判断标准只有一条：**这一行是不是每次运行都要用？**

## 四类内容的归属

### `SKILL.md` —— 只放"每次都要的决策逻辑"

必须留下：

- **核心原则**：这个领域真正的风险面在哪（1-3 行）
- **路由表**：判断"该走哪条分支"的那张表（接口类型速查、Agent 类型速查）
- **硬约束**：占比、配额、编号规则、覆盖率口径
- **加载时机地图**：下面那张表 —— **这是拆分的关键，没有它拆分就等于把内容藏起来**
- **输出格式骨架**：最精简的样例 + 指向 `assets/` 的完整模板
- **交付自检**：机器校验命令

必须移走：可查的清单、详细维度的展开、场景示例、完整工具矩阵、产出模板。

### `references/` —— "看情况才读"的领域知识

判断标准：**存在一个明确的触发条件**（"被测接口是 GraphQL 时"、"需要选工具时"）。

- 每份聚焦一件事（`dimensions.md` / `tool-cases.md` / `tooling.md` / `scenarios.md`）
- 大文件（>300 行）加目录
- 拆分的收益是**粒度**：agent 只加载需要的那一份，不是整个知识库

### `assets/` —— 会被抄进产出的东西

判断标准：**agent 会原样复制/填充它**。

- 产出模板、schema、boilerplate —— 放这里而不是让模型每次重打一遍
- 带"填写要求 + 常见错误"表，模型 pattern-match 模板比读散文描述可靠得多

### `scripts/` —— 确定性的重复逻辑

判断标准：**每次跑结果都一样的机械校验**。

- 格式校验、ID 唯一性、配额计算这类规则
- 本仓库目前统一放在根 `scripts/`（`python scripts/xxx.py`），尚未下沉到单个技能

## 加载时机地图（必须有）

拆分后如果只是"把内容挪走"而不告诉 agent 什么时候读，等于把内容藏起来了。规范原话：
*"A generic 'see references/ for details' is less useful than 'Read X if the API returns a
non-200 status code.'"*

样板（`qa-api-testing`）：

| 什么时候读 | 读哪个 |
|-----------|--------|
| 展开某一维的测试范围，或交付前逐项自检 | `references/core-flows.md`（六维详图 + Mock + 检查清单） |
| 生成具体测试用例；被测接口是 GraphQL/gRPC/WebSocket | `references/test-cases.md`（39 条用例 + OWASP 对照 + 协议专项） |
| 选工具，或展开某工具能力边界 | `references/tooling.md`（默认选型 + 能力矩阵 + 性能工具） |
| 用户情况命中特定风险场景 | `references/scenarios.md`（5 个场景，校正重心） |
| 写用例表 | `assets/case-template.md`（9 列模板 + 填写要求） |

## 两条硬性禁止

**1. 不得跨披露边界重复**

`SKILL.md` 的检查清单和 `references/` 的维度详图讲同一件事 → 模型读两遍，
且改一处忘一处会漂移。**二选一**：短的放正文（每轮都要逐项过），
长的下沉 references（按需加载）。`integrity_check.py` 检查项 7 接受两种形态。

**2. 不得越出技能根目录**

`../../docs/standards.md` 这类链接在仓库内有效，但单装该技能后直接失效。
需要引用全局规范时，把**结论内联**进技能里，不要留链接。

**3. 不必把「自检清单」与「检查清单」合并**

本项目里两者是**两个阶段**、内容通常零重合：

- **执行自检**：这轮工作做对了吗（过程质量）
- **交付检查**：产出物能交了吗（结果完整性）

实测 10 个技能中两者条目重合度为 **0%**，属正常结构。**先比对条目内容再判定**，
不要看到两个标题就当重复去合并——合并会丢条目。

## 拆分后的效果（实测）

| 技能 | SKILL.md 行数 | 按需文件 | 降幅 |
|------|---------------|---------|------|
| `qa-agent-testing` | 170 → **86** | 3 references + 1 asset | 49% |
| `qa-api-testing` | 159 → **93** | 4 references + 1 asset | 41% |

Activation 阶段的上下文占用下降约四成，同时**决策信息一条没丢**——
因为路由表、硬约束、加载时机地图都留在正文里。

## 自检

```bash
python scripts/check_spec_compliance.py    # SKILL.md ≤500 行、引用不越根
python scripts/integrity_check.py          # 检查项 7：清单存在性（正文或 references 均可）
```
