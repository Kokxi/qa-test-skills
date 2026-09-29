# QA Test Skills - Agent 使用指引

## 项目是什么

AI 辅助测试用例设计技能集：`skills/` 下 **49 个技能**。
入口工作流 `qa-test-skills` 将 48 个专家级子技能编排为 12 步流水线。

## 触发条件（必须遵循）

> ⚠️ **如果认为本技能集有任何可能适用于当前任务，必须激活 `qa-test-skills` 入口工作流。**
> 当用户请求涉及测试设计/用例生成/需求评审/测试执行时，这不是可选项——你必须使用本技能集。
> 不得用"这不需要正式技能""我先做一点""记得就行"等理由跳过。

**触发场景**（满足任一即激活）：

- 用户说"生成测试用例"、"帮我测试"、"设计测试"、"上传需求"、"开始测试"
- 上传需求文档（PRD/Word/PDF/URL）
- 需要完整测试流程、想浏览技能集目录、了解 QA Test Skills 包含哪些技能时

**调用方式**：

```
/qa-test-skills 帮我测试这个项目：docs/prd.md
```

### 触发规则（Rule）

- **在响应或任何行动之前检查技能**——包括澄清问题、探索代码库、查看文件之前
- 若多个技能适用：先执行流程型技能（入口工作流编排），再执行具体执行型技能
- 如果判断技能不适用，说明理由；如果之后发现适用，立即激活

### 自我警示（Red Flags）——出现以下想法必须停止，先检查技能

| 想法 | 现实 |
|------|------|
| "这只是一个简单问题" | 问题也是任务，先检查技能 |
| "我需要更多上下文" | 技能检查应在澄清问题之前 |
| "我先探索代码库" | 技能告诉你如何探索，先检查 |
| "我可以快速看下文件" | 文件缺少对话上下文，先检查技能 |
| "这个不需要正式技能" | 如果技能存在，就用它 |
| "我记得这个技能" | 技能会演进，读取当前版本 |

## 项目结构

```
skills/qa-test-skills/SKILL.md      ← 入口工作流（name: qa-test-skills，12 步编排）
skills/qa-test-skills/references/   ← 工作流详细展开（含每步执行格式）
skills/qa-*/SKILL.md                ← 48 个专家级子技能（每步一个）
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
- **交付前自检**：跑 `python scripts/validate_testcase_table.py test-output/测试用例.csv`，报错先修再交付

## 维护本仓库时（改 skill 不是改测试用例）

- **frontmatter 遵循 [Agent Skills 开放规范](https://agentskills.io/specification)**：顶层只允许
  `name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`；
  自定义字段收在 `metadata` 下（string → string，复杂值用紧凑 JSON 字符串）
- **触发词必须写进 `description`**：规范规定它是技能唯一的触发依据，`metadata.when-to-use` 仅作备份。
  英文触发词表在 `scripts/i18n_triggers.json`
- **发布前必跑三道门禁**：`python scripts/run_qa.py all`（规范合规 + 一致性 + 依赖图）
- **改 frontmatter 字段名时**，所有读元数据的脚本都要跟着走 —— 统一用 `scripts/skillmeta.py`，
  不要在脚本里另写一套正则
- **正文体量**：`SKILL.md` 只放"每次运行都要的决策逻辑"（核心原则 / 路由表 / 硬约束 /
  加载时机地图 / 输出骨架 / 交付自检），控制在 500 行内；可查的清单、维度展开、场景示例、
  工具矩阵下沉 `references/`，会被抄进产出的模板放 `assets/`。
  **拆分必须配"加载时机地图"，否则等于把内容藏起来；也不得跨边界重复同一件事**
- **引用不越技能根目录**：正文链接只能是 `references/xxx.md`，不得用 `../../docs/...`
  （单装某个技能时这类链接直接失效）；需引用全局规范时把结论内联
- **改门禁必须配双向回归**：`python scripts/gate_selftest.py` 对 15 项检查逐项验证
  「注入违规必须报 / 合规内容必须不报」。只看「当前仓库仍然通过」证明不了检查是对的——
  检查坏了的时候它同样显示通过。**禁止在没跑自测的情况下改 `integrity_check.py` 的检查逻辑**
- **发布前必跑三道门禁**：`python scripts/run_qa.py all`（规范合规 + 一致性 + 依赖图）；
  改了 `integrity_check.py` 再加跑 `python scripts/gate_selftest.py`
- **发布脚本默认版本必须同步**：`publish-all.bat` / `push-clawhub.bat` / `push-skillhub.bat`
  的默认版本要与入口技能 `metadata.version` 一致（检查项 12 会拦），否则发布会降版本
- **调 Python CLI 前设 `PYTHONIOENCODING=utf-8`**：控制台是 GBK 时，CLI 打印 `✓`
  会抛 `UnicodeEncodeError` 并以非 0 退出——**操作其实成功了，批处理却记成 FAILED**。
  判断发布是否真失败要看平台后台，不要只看 `push-skillhub-failed.txt`
- **改 `.bat` 必须保持 GBK + CRLF**：`cmd.exe` 在中文 Windows 上按系统 ANSI 码页
  （GBK/936）读 `.bat`；编码写成 UTF-8 或行尾写成 LF，症状都是
  「'xxx' 不是内部或外部命令」且指错位置。另外 `for /f ('...')` 里不能有双引号。
  改完必须跑 `python scripts/gate_selftest.py --check 12`
- **发布暂存是平台适配层，不要在源文件里迁就平台**：
  `scripts/stage_for_publish.py --platform {skillhub,clawhub}` 在副本上改 frontmatter
  （SkillHub 补顶层 `displayName`；ClawHub 剥 `metadata.slug`）。
  源文件始终保持规范形态。**不要为此维护双分支**，会漂移
- **产出测试用例必须用全项目统一的 9 列格式**，唯一真源是
  `skills/qa-test-case-design/references/output-template-full.md`：
  `用例编号|测试类型|功能模块|测试标题|用例级别|预置条件|测试步骤|预期结果|风险等级`
  - **不得自行复制或改动模板**，也不得增删列（9 列是 `validate_testcase_table.py`
    与 `测试用例.csv` 的硬约束）
  - 编号一律 3 段式 `TC_{模块缩写}_{功能缩写}_{三位序号}`，**不用场景后缀**
  - 「子功能」并入「功能模块」用 `模块/子功能`；**无「实际结果」列**（属
    `qa-execution-observation` 的执行记录）
  - 「测试步骤」按类型定：协议/接口/规则/计算类**必填**；UI/业务流程类可留空并标注
    「由执行人按实际系统补充」
  - 各技能的 `assets/case-table.md` 只是本技能侧的模板副本，**冲突时以
    `qa-test-case-design` 的真源为准**
- **ID 前缀不得混用**：`TC_` 用例 / `REQ-` 需求 / `SC-` 场景 / `BD-` 边界 /
  `RULE-` 业务规则 / `RISK-` 风险点。前缀以 `docs/standards.md` 为准。
  「关联需求ID」写 `REQ-`、「关联场景ID」写 `SC-`，历史上曾 9 处误写成 `TC_`（已修）
- **分支同步约定（dev-zh ↔ master）**：master 用 dev-zh 的规范形态 frontmatter，
  唯一分叉点是**展示名**——dev-zh 的 `metadata.display-name` 是中文（供 SkillHub 中文平台），
  master 必须保持**英文**（如 `Api Testing`，供 GitHub/ClawHub）。
  同步方式：merge dev-zh 后，把 master 上 49 个 SKILL.md 的 `display-name` 改回英文再提交；
  `name` 字段两侧都是英文 slug，不要动。
- **新增 references/ 或 assets/ 文件必须登记进 `metadata.references`**，
  否则加载时机地图指向了客户端看不到的文件（检查项 15 会拦）
- 详见 `docs/optimization-checklist.md` 与 `docs/skill-content-layout.md`

## 参考

- `README.md` — 完整安装方式与技能目录
- `docs/optimization-checklist.md` — 发布前检查清单（含规范合规门禁）
- `docs/skill-content-layout.md` — **SKILL.md / references / assets / scripts 拆分约定**
- `docs/skill-migration-plan.md` — **剩余 47 个技能的内容层改造计划（分 7 批）**
- `skills/qa-test-skills/references/workflow-detail.md` — 12 步工作流详细执行指南
