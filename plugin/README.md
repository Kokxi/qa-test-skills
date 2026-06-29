# QA Test Skills Plugin

> Plugin package for [ClawHub](https://clawhub.ai/kokxi/qa-test-skills) | 完整说明见根目录 [README.md](../README.md)

![Version](https://img.shields.io/badge/version-1.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-48-orange)

## 安装

### 方式1：从 ClawHub（推荐）

```bash
openclaw plugins install clawhub:@kokxi/qa-test-skills
```

### 方式2：从 GitHub 手动安装

```bash
git clone https://github.com/Kokxi/qa-test-skills.git
cd qa-test-skills
/plugin dir ./qa-test-skills
```

## 使用

所有技能已加载为 OpenClaw 命令。入口工作流：

```
/qa-test-skills 请帮我测试这个项目：<需求文档路径>
```

也可单独调用各子技能命令：
- `/qa-requirement-review` — 需求评审
- `/qa-scenario-tree` — 场景树构建
- `/qa-ai-prompt-strategy` — AI 提示词策略
- 等（共 48 个命令）

## 元信息

| 字段 | 值 |
|------|-----|
| 包名 | `@kokxi/qa-test-skills` |
| 版本 | 1.5.0 |
| Plugin API | `>=2026.3.24-beta.2` |
| 技能数 | 48 |
| 许可证 | MIT |

## 文档

完整说明（设计初衷、工作流详解、技能清单、贡献指南等）请参阅根目录 [README.md](../README.md)。

## 许可证

MIT License — 详见 [LICENSE](../LICENSE)
