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
