# QA Test Skills - Agent 使用指引

## 项目是什么

AI 辅助测试用例设计技能集：`skills/` 下 **49 个技能**。
入口工作流 `qa-test-skills` 将 48 个专家级子技能编排为 12 步流水线。

## 项目结构

```
skills/qa-test-skills/SKILL.md      ← 入口工作流（name: qa-test-skills，12 步编排）
skills/qa-*/SKILL.md                ← 48 个专家级子技能（每步一个）
references/                         ← 工作流详细展开（含每步执行格式）
examples/                           ← 示例项目（ecommerce / agent）
```

## 如何响应测试需求

用户说"生成测试用例 / 帮我测试 / 设计测试 / 上传需求"时：

1. 读取 `skills/qa-test-skills/SKILL.md`（入口工作流）
2. 按 12 步工作流执行，每步读取对应子技能 `skills/qa-xxx/SKILL.md`
3. 每步产出独立文件到 `test-output/`
4. 最终产出 `测试用例.csv`

## 关键约束

- **覆盖率必须标注口径**："基于现有需求文档的覆盖率"，不得用"全覆盖/100%"绝对化表述
- **缺口不得编造**：需求缺失模块只能标注"未覆盖+原因+建议补充"，不得编造需求或用例
- **测试用例.csv 格式**：标准 CSV（半角逗号分隔 / RFC 4180 引号转义 / UTF-8 含 BOM / 固定 9 列 / 禁 `|` 竖线与 Markdown 表格）
- **每步独立落盘**：第 0-11 步各产出独立文件，最后汇总为测试报告 + 测试用例.csv

## 参考

- `README.md` — 完整安装方式与技能目录
- `references/workflow-detail.md` — 12 步工作流详细执行指南
