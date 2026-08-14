# QA Test Skills 使用演示（Claude Code / Codex）

> 本文档演示如何在主流 AI Agent（Claude Code、Codex）中安装并使用本技能集，
> 从"一句话需求"到"完整测试用例集"的完整流程。无需配图——按步骤操作即可复现。

---

## 一、安装

### Claude Code

```bash
# 一键安装（全局）
npx skills add Kokxi/qa-test-skills -a claude-code

# 或在项目内安装（装到当前项目 .claude/skills/）
npx skills add Kokxi/qa-test-skills -a claude-code -p
```

安装后技能落在 `~/.claude/skills/`（全局）或 `.claude/skills/`（项目），共 **49 个技能目录**：

```
~/.claude/skills/
├── qa-test-skills/              ← 入口工作流（12 步编排）
├── qa-requirement-review/       ← 48 个专家级子技能
├── qa-test-case-design/
└── ...（共 49 个）
```

### Codex

```bash
# 一键安装
npx skills add Kokxi/qa-test-skills -a codex
```

安装后技能落在 `~/.codex/skills/`（全局）或 `.agents/skills/`（项目），结构同上（49 个技能目录）。

---

## 二、使用演示

### 方式 1：对话自动触发（推荐）

安装后无需任何配置。**直接对 Agent 说需求**，`qa-test-skills` 入口工作流会根据 `when_to_use` 自动激活：

```
你：帮我测试这个项目：docs/prd.md
```

Agent 自动执行 12 步工作流，产出到 `test-output/`：

```
test-output/
├── 需求文档集合.md        ← 第0步 需求解析
├── 需求评审报告.md        ← 第1步 需求评审
├── 需求解构表.md          ← 第2步 需求解构
├── 风险评估.md / 启发式清单.md / 场景树.md   ← 第3步 场景构建
├── 边界清单.md / 组合矩阵.md / 状态转换图.md / 领域模型.md  ← 第4步 深度设计
├── 回归策略.md            ← 第5步 回归策略
├── AI上下文包.md          ← 第6步 上下文工程
├── AI提示词.md            ← 第7步 提示词生成
├── 测试用例_初版.csv      ← AI 生成用例
├── 用例评审报告.md / 盲区补偿用例.md  ← 第8步 评审补盲
├── 测试报告.md            ← 第9步 测试报告
├── 测试用例.csv           ← ★ 最终交付（标准 CSV，Excel 可直接打开）
├── 输出验证报告.md        ← 第10步 输出验证
└── 专家评审报告.md        ← 第11步 专家评审（可选）
```

### 方式 2：显式调用入口技能

```
Claude Code：/qa-test-skills 帮我设计登录模块的测试用例
Codex：      @qa-test-skills 帮我设计登录模块的测试用例
```

### 方式 3：单独调用子技能

每个子技能也可独立触发（无需跑完整工作流）：

```
你：帮我评审这份需求文档            → 激活 qa-requirement-review
你：分析登录功能的边界场景          → 激活 qa-boundary-deep-dive
你：这个接口的测试要点是什么        → 激活 qa-api-testing
```

---

## 三、完整演示（ecommerce 示例项目）

以下是一个真实可复现的完整演示（基于 `examples/ecommerce-project`）：

### 第 1 步：给出需求

```
你：请完整测试这个项目：examples/ecommerce-project/docs/prd.md
```

### 第 2 步：Agent 自动执行

Agent 按 12 步工作流逐步执行，每步产出独立文件（见上文 test-output/ 结构）。

### 第 3 步：查看最终产物

```bash
# 打开最终测试用例（标准 CSV，9 列：编号/类型/模块/标题/级别/前置/步骤/预期/风险）
open test-output/测试用例.csv

# 查看测试报告（含覆盖率分析与缺口标注）
open test-output/测试报告.md
```

### 预期结果（真实执行数据）

| 指标 | ecommerce 示例 | agent 示例 |
|------|:---:|:---:|
| 测试用例 | 116 条（P0 19/P1 53/P2 38/P3 6） | 88 条 |
| 覆盖率 | 26/26 需求点（基于现有需求文档） | — |
| 过程文件 | 20 个（12 步全流程） | 20 个 |

> 参考：`examples/ecommerce-project/test-output/`、`examples/agent-project/test-output/` 为真实执行产物。

---

## 四、关键约束（Agent 会自动遵守）

| 约束 | 说明 |
|------|------|
| **覆盖率标注口径** | 报告注明"基于现有需求文档的覆盖率"，不用"全覆盖/100%"绝对化表述 |
| **缺口不编造** | 缺失模块只标注"未覆盖+原因+建议补充" |
| **CSV 格式** | 标准 CSV：逗号分隔 / RFC 4180 引号转义 / UTF-8 含 BOM / 9 列 / 禁竖线 |
| **每步独立落盘** | 第 0-11 步各产出独立文件，不合并 |

---

## 五、常见问题

**Q：安装后 Agent 没自动触发怎么办？**
显式调用入口：Claude Code 输入 `/qa-test-skills`，Codex 输入 `@qa-test-skills`。

**Q：想了解技能集包含哪些技能？**
对 Agent 说"QA Test Skills 包含哪些技能"，入口工作流会自动列出 49 个技能分类。

**Q：安装路径在哪？**
Claude Code：`~/.claude/skills/`；Codex：`~/.codex/skills/`（或项目级 `.claude/skills/`、`.agents/skills/`）。

---

## 参考

- 完整技能目录与安装方式：`README.md`
- 技能分类（可单独使用/依赖/有输出/经验型）：`docs/skill-classification.md`
- 12 步工作流详细执行指南：`skills/qa-test-skills/references/workflow-detail.md`
