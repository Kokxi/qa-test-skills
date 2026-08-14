# 优化工作流 - 发布前检查清单

> 本文档记录每次优化/修改 skill、准备发布前的检查项。
> 由 CLAUDE.md / AGENTS.md 引用，作为开发 Agent 的执行指引。

## ClawHub 安全审计检查

1. 在 ClawHub 上找到对应技能的 security-audit 页面：
   - `https://clawhub.ai/kokxi/skills/{skill-slug}/security-audit`
2. 查看是否有未通过的审计发现（Vague Triggers、Missing User Warnings、Hidden Instructions 等）
3. 如有发现，先修复后再发布新版
4. 修复后通过 `clawhub skill verify {slug} --version {version}` 验证审计状态
5. 审计状态变为 pass 才算修复完成

## 常见修复方式

| 审计发现 | 修复方式 |
|----------|----------|
| **Vague Triggers** | 收窄 `when_to_use`，去掉过于泛化的关键词 |
| **Missing User Warnings** | 在技能内容开头添加 `> **⚠️ 安全警告**` 区块，说明操作前需确认的条件 |
| **Hidden Instructions** | 通常是 YAML folded scalar `>-` 的误报，可忽略 |

## 部署自包含性检查（分发视角，必查）

> ⚠️ 本项目面向最终用户/AI Agent 分发（npx skills add / openclaw 插件 / 拷贝 skills/ 目录）。
> 每次发布前必须站在**分发视角**验证——用户拿到的技能包必须是"自包含"的。

### 1. 模拟拷贝验证（核心）

```bash
# 模拟用户只拷贝 skills/ 目录（最常见的分发形态）
mkdir -p /tmp/skill-dist && cp -r skills/* /tmp/skill-dist/
# 检查所有 SKILL.md 的相对引用（references/、子目录、平台专项）在拷贝后是否仍有效
grep -rn "references/\|platform-" skills/ --include="SKILL.md" | grep -v "skills/.*/references/" > /dev/null
# 逐个确认：被引用的文件必须存在于同一技能目录内（或同目录的 references/ 下）
```

- [ ] 每个 SKILL.md 的 `references/xxx.md` 相对引用，指向的文件**是否在技能自身目录内**（非项目根/外部目录）
- [ ] 入口工作流的配套文件（references/ 等）是否与入口 SKILL.md 同目录或明确归属（不依赖项目根）
- [ ] 无跨目录"隐形依赖"：不引用项目根 `references/`、`docs/`、`examples/` 等用户可能拿不到的文件

### 2. 结构归属检查

- [ ] 入口技能 `skills/qa-test-skills/` 是否自包含（SKILL.md + 全部 references/ 在同目录）
- [ ] 48 个子技能各自目录内文件齐全（SKILL.md + 自身 references/，如有）
- [ ] 无"孤儿文件"：项目根不应有只被单个技能引用、却不随技能分发的文件

### 3. 安装形态验证（覆盖三条分发路径）

| 分发路径 | 验证点 |
|----------|--------|
| `npx skills add` | 装到 Agent skills 目录后，49 个技能是否全部被发现（含入口） |
| `openclaw plugins install` | plugin/index.js 扫描是否返回 49 个技能（含入口） |
| 手动拷贝 skills/ | 拷贝后所有相对引用是否仍有效（无断链） |

### 4. 变更后必查

> 任何结构变更（目录迁移/改名/新增目录/移动文件）后，**必须**重跑上述检查——
> 内容层"引用不悬空"不等于部署层"拷贝后仍有效"（典型案例：根 references/ 迁移前，入口
> 引用的 references/ 在仓库内有效，但用户只拷贝 skills/ 时断链）。
