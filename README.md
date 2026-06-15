# 软件测试 Skills 集 — Claude Code 安装与使用

## 是什么

41 个 QA 技能点，覆盖资深测试工程师的完整能力光谱。每个技能包含：**思维框架 → 标准 Prompt → 验收 Checklist → 常见翻车点**。

```
认知与思维 → 需求到模型 → 深度设计 → AI 协作 → 执行洞察 → 策略架构 → 沟通传承
```

## 安装

### 方式一：全局安装（推荐）

把整个 skills 目录复制到 Claude Code 的全局技能目录，所有项目都能用：

```bash
# Windows
xcopy /E /I skills %USERPROFILE%\.claude\skills\qa-skills

# macOS / Linux
cp -r skills ~/.claude/skills/qa-skills
```

然后创建（或编辑）项目根目录的 `CLAUDE.md`，加上一行：

```markdown
Skills available at ~/.claude/skills/qa-skills/
```

重启 Claude Code 后生效。

### 方式二：项目级引用

如果只想在当前项目用，在项目根目录的 `CLAUDE.md` 中引用：

```markdown
## QA Skills

本项目的 skills 目录包含 QA 技能库。当用户提出测试相关问题（如设计用例、分析缺陷、制定策略等），先检查 skills/ 下有无匹配的 SKILL.md，有则加载使用。
```

这样 Claude Code 会在处理 QA 相关问题时自动查找 `skills/` 下的文件。

### 方式三：按需复制单个技能

不需要全部 41 个技能，可以只挑常用的复制到 `~/.claude/skills/`：

```bash
cp skills/qa-boundary-deep-dive/SKILL.md ~/.claude/skills/qa-boundary-deep-dive.md
```

## 使用

### 在对话中触发

技能安装后，当你在 Claude Code 中提出 QA 相关问题，AI 会根据关键词自动加载对应的技能。例如：

| 你说 | 触发技能 |
|------|---------|
| "帮我设计这个功能的测试用例" | `qa-req-deconstruction` + `qa-scenario-tree` |
| "分析这个 Bug 的根因" | `qa-bug-root-cause-analysis` |
| "评估这次发布的风险" | `qa-release-risk-governance` |
| "上传一份文件帮我写测试用例" | `qa-doc-to-test` + `qa-scenario-tree` |
| "这个接口怎么测" | `qa-api-testing` |
| "Review 一下这段代码的测试" | `qa-code-review-for-test` |
| "组织一次项目复盘" | `qa-retrospective` |
| "帮我检查测试覆盖率够不够" | `qa-quality-metrics` |

你也可以直接用技能名提问：

> 用 qa-boundary-deep-dive 分析这个输入框的边界

### 加载特定技能

如果你明确想用某个技能，直接说技能名即可：

> 我想用 qa-test-strategy-design 来规划这个版本的测试策略

### 配合 Prompt 模板使用

每个 SKILL.md 都内置了标准 Prompt 模板，可以直接复制使用。以 `qa-retrospective` 为例：

```
我需要主持一场复盘，请帮我设计复盘方案：

复盘场景：迭代复盘
参与人：QA + 开发 + PM
时长：45 分钟
背景：上个版本上线后发现一个严重漏测

请输出：
1. 复盘议程
2. 开场话术
3. 引导问题清单
4. 改进措施模板
5. 常见陷阱预警
```

## 技能清单

### 簇 1：认知与思维（内功）

| 技能 | 作用 |
|------|------|
| `qa-critical-thinking` | 测试批判性思维——质疑需求、逆向思维 |
| `qa-risk-intuition` | 风险直觉——识别"什么会出事" |
| `qa-question-framework` | 提问框架——知道该问什么问题 |
| `qa-task-router` | 任务路由——判断任务价值和优先级 |

### 簇 2：需求到模型

| 技能 | 作用 |
|------|------|
| `qa-req-deconstruction` | 需求解构——把模糊需求拆成可测单元 |
| `qa-scenario-tree` | 场景树——穷举业务场景 |
| `qa-doc-to-test` | 文档转测试用例——上传文件自动提取并生成测试用例 |
| `qa-domain-modeling` | 领域建模——理解业务的实体和规则 |
| `qa-state-transition` | 状态转换——分析状态变更路径 |

### 簇 3：深度设计

| 技能 | 作用 |
|------|------|
| `qa-boundary-deep-dive` | 边界分析——四维边界模型 |
| `qa-combination-strategy` | 组合策略——Pairwise / 正交 |
| `qa-heuristic-checklist` | 启发式检查清单 |
| `qa-test-oracle-expansion` | 测试预言——"什么是对的" |
| `qa-multi-round-polishing` | 多轮打磨——迭代优化用例 |

### 簇 4：AI 协作

| 技能 | 作用 |
|------|------|
| `qa-ai-context-engineering` | 上下文工程——给 AI 高质量输入 |
| `qa-ai-prompt-strategy` | Prompt 策略——结构化提问 |
| `qa-ai-output-critique` | AI 输出评审——辨别幻觉和遗漏 |
| `qa-ai-blindspot-compensation` | AI 盲区补偿——补 AI 做不到的事 |

### 簇 5：执行洞察

| 技能 | 作用 |
|------|------|
| `qa-log-analysis` | 日志分析——从日志中找异常信号 |
| `qa-debug-strategy` | Debug 策略——系统化定位问题 |
| `qa-data-verification` | 数据验证——数据库/接口数据准确性 |
| `qa-execution-observation` | 执行观察——测试时在看什么 |
| `qa-bug-root-cause-analysis` | Bug 根因分析——从现象挖到根因 |

### 簇 6：策略架构

| 技能 | 作用 |
|------|------|
| `qa-test-strategy` | 测试策略——整体测试方案设计 |
| `qa-test-strategy-design` | 策略设计——分层策略设计方法 |
| `qa-change-impact` | 变更影响分析——改动波及范围评估 |
| `qa-test-automation-decisions` | 自动化决策——什么该自动化、什么不该 |
| `qa-environment-management` | 环境管理——测试环境治理 |
| `qa-release-risk-governance` | 发布风险治理——上线前风险把控 |
| `qa-quality-metrics` | 质量度量——用数据说话 |
| `qa-testability-advocacy` | 可测试性推动——让代码更可测 |

### 簇 7：沟通传承

| 技能 | 作用 |
|------|------|
| `qa-knowledge-transfer` | 知识传递——经验文档化 |
| `qa-collaboration` | 协作——跨角色配合 |
| `qa-test-review` | 测试评审——用例/方案评审 |
| `qa-bug-reporting` | Bug 报告——写出让人愿意修的 Bug |
| `qa-stakeholder-communication` | 利益相关方沟通——对齐预期 |
| `qa-code-review-for-test` | 代码评审——从代码层面找测试点 |
| `qa-team-coaching` | 团队教练——指导初级测试成长 |
| `qa-retrospective` | 回顾复盘——从经验中提炼改进 |

## 文件结构

```
opentest/
├── README.md                 ← 本文件
├── CLAUDE.md                 ← Claude Code 项目配置（可选）
├── skills/
│   ├── qa-critical-thinking/
│   │   └── SKILL.md
│   ├── qa-boundary-deep-dive/
│   │   └── SKILL.md
│   ├── qa-bug-root-cause-analysis/
│   │   └── SKILL.md
│   ├── qa-doc-to-test/
│   │   └── SKILL.md
│   └── ... 共 41 个技能目录
└── chat-logs/                ← 架构设计讨论记录
```

## 每个 SKILL.md 的结构

```yaml
---
name: 技能名
description: 一句话说明 + 触发词
allowed-tools: 允许使用的工具
metadata:
  trigger: 关键词列表
  cluster: 所属簇
---
# 技能名

## 概述
## 解决的问题
## 核心框架（思维模型 + 步骤）
## AI 协作模式（标准 Prompt 模板）
## 验收 Checklist
## 常见翻车点
```

## 常见问题

**Q: 必须全部安装吗？**
不用。选你需要的技能复制即可，每个技能独立。

**Q: 技能之间会冲突吗？**
不会。每个技能独立，同名技能会覆盖（后安装的生效）。

**Q: 安装了但 Claude Code 没识别？**
检查 CLAUDE.md 是否正确引用了 skills 路径，或者直接说技能名触发。

**Q: 可以自己修改技能内容吗？**
可以。SKILL.md 就是普通 Markdown，按你团队的实际情况修改即可。

**Q: 技能是针对 Claude Code 还是 OpenCode 的？**
SKILL.md 格式两者兼容。OpenCode 支持更丰富的技能注册（opencode.json），Claude Code 通过 CLAUDE.md + 技能目录加载。
