# QA Test Skills

AI 辅助测试用例设计技能集：`skills/` 下 **49 个平级技能**（入口工作流 `qa-test-skills` + 48 个专家级子技能），入口将子技能编排为 12 步流水线，从需求文档自动生成结构化测试用例。

## 安装

```bash
# 推荐：一键安装（skills.sh，支持 cursor/codex/claude-code/windsurf/cline/gemini-cli/github-copilot/openclaw）
npx skills add Kokxi/qa-test-skills

# 指定 Agent 安装
npx skills add Kokxi/qa-test-skills -a claude-code -a cursor

# ClawHub 插件
openclaw plugins install clawhub:@kokxi/qa-test-skills
```

安装后技能落入各 Agent 的 skills 目录（Claude Code 为 `.claude/skills/`，Cursor/Codex 为 `.agents/skills/`）。

## 使用

对 Agent 说以下任一指令，入口工作流自动激活并执行 12 步：

- "生成测试用例"
- "帮我测试"
- "设计测试"
- "上传需求"

或显式调用入口技能：

```
/qa-test-skills 帮我测试这个项目：docs/prd.md
```

## 目录结构

```
skills/qa-test-skills/SKILL.md      ← 入口工作流（12 步编排，name: qa-test-skills）
skills/qa-*/SKILL.md                ← 48 个专家级子技能
references/                         ← 工作流详细展开（含每步执行格式）
examples/                           ← 示例项目（ecommerce / agent）
```

## 关键约束

- 每步产出独立文件到 `test-output/`
- 覆盖率必须标注口径（"基于现有需求文档的覆盖率"）
- 缺失模块不得编造用例，只标注"未覆盖+原因"
- 最终 `测试用例.csv`：标准 CSV（逗号分隔 / RFC 4180 引号转义 / UTF-8 含 BOM / 9 列 / 禁 `|` 竖线）

## 开发者说明

- 发布/优化前检查清单见 `docs/optimization-checklist.md`
- 12 步工作流详细执行指南见 `references/workflow-detail.md`
- Agent 执行指引见 `AGENTS.md`
