# QA Test Skills

AI 辅助测试用例设计技能集：`skills/` 下 **49 个技能**（入口工作流 `qa-test-skills` + 48 个专家级子技能），入口将子技能编排为 12 步流水线，从需求文档自动生成结构化测试用例。

## 触发条件

用户表达以下意图时，激活入口工作流 `qa-test-skills` 并执行 12 步：

- "生成测试用例" / "帮我测试" / "设计测试"
- "上传需求" / 上传需求文档（PRD/Word/PDF/URL）
- 需要完整测试流程时

也可显式调用入口技能：

```
/qa-test-skills 帮我测试这个项目：docs/prd.md
```

## 工作方式

1. 读取 `skills/qa-test-skills/SKILL.md`（入口工作流）
2. 按 12 步执行，每步读取对应子技能 `skills/qa-xxx/SKILL.md`
3. 每步产出独立文件到 `test-output/`
4. 最终产出 `测试用例.csv`

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
- 安装方式见 `README.md`
