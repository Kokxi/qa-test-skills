# QA Test Skills — opencode 安装指南

## 一键安装（推荐）

```bash
npx skills add Kokxi/qa-test-skills -a opencode
```

或通过 ClawHub 插件市场：

```bash
openclaw plugins install clawhub:@kokxi/qa-test-skills
```

## 手动安装

将本仓库克隆后，把 `skills/` 目录（49 个技能，含入口工作流 `qa-test-skills`）链接到 opencode 的 skills 目录：

```bash
git clone https://github.com/Kokxi/qa-test-skills.git
# 全局（推荐）
ln -s "$(pwd)/qa-test-skills/skills" ~/.opencode/skills
# 或项目级
ln -s "$(pwd)/qa-test-skills/skills" .opencode/skills
```

## 结构说明

```
skills/                     ← 49 个技能目录
├── qa-test-skills/SKILL.md         ← 入口工作流（12步编排，name: qa-test-skills）
├── qa-requirement-review/SKILL.md  ← 48 个专家级子技能
├── qa-test-case-design/SKILL.md
└── ... (共 49 个，可被 / 直接调用)
```

## 使用

```
/qa-test-skills 帮我测试这个项目：docs/prd.md
```

或直接说"生成测试用例"，`qa-test-skills` 入口工作流会自动激活并编排 48 个子技能。
