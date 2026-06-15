# QA Test Skills - 软件测试技能集

> 42个专家级测试技能，覆盖测试全生命周期

## 简介

QA Test Skills 是一套完整的软件测试技能集合，旨在将资深测试专家的经验编码为可加载的技能，让初级测试人员也能输出专家级测试用例。

## 核心价值

- **用户提问方式不变**，技能集在后台自动完成专家级测试设计
- **覆盖测试全生命周期**：需求分析 → 测试设计 → AI协作 → 执行监控 → 质量度量
- **标准化工作流**：8步串接，自动调用42个技能

## 技能清单（42个）

### 主入口（1个）
| 技能 | 功能 |
|------|------|
| `qa-test-workflow` | 工作流编排（主入口） |

### AI协作（6个）
| 技能 | 功能 |
|------|------|
| `qa-ai-context-engineering` | 构建AI测试上下文 |
| `qa-ai-prompt-strategy` | 提示词策略 |
| `qa-ai-output-critique` | 输出评判 |
| `qa-ai-blindspot-compensation` | 盲区补偿 |
| `qa-heuristic-checklist` | 启发式清单 |
| `qa-question-framework` | 提问框架 |

### 思维+需求+设计（8个）
| 技能 | 功能 |
|------|------|
| `qa-critical-thinking` | 批判性思维 |
| `qa-risk-intuition` | 风险直觉 |
| `qa-req-deconstruction` | 需求解构 |
| `qa-scenario-tree` | 场景树构建 |
| `qa-domain-modeling` | 领域建模 |
| `qa-boundary-deep-dive` | 边界分析 |
| `qa-combination-strategy` | 组合策略 |
| `qa-state-transition` | 状态转换 |

### 执行洞察（3个）
| 技能 | 功能 |
|------|------|
| `qa-execution-observation` | 执行观察 |
| `qa-bug-root-cause-analysis` | Bug根因分析 |
| `qa-bug-reporting` | Bug报告 |

### 策略架构（12个）
| 技能 | 功能 |
|------|------|
| `qa-test-strategy-design` | 测试策略 |
| `qa-release-risk-governance` | 发布风险 |
| `qa-quality-metrics` | 质量度量 |
| `qa-testability-advocacy` | 可测试性推动 |
| `qa-tech-selection` | 技术选型 |
| `qa-test-env-data` | 环境数据管理 |
| `qa-defect-lifecycle` | 缺陷生命周期 |
| `qa-ci-cd-testing` | CI/CD测试 |
| `qa-shift-left` | 测试左移 |
| `qa-shift-right` | 测试右移 |
| `qa-test-reporting` | 测试报告 |
| `qa-test-estimation` | 工作量估算 |

### 沟通传承（4个）
| 技能 | 功能 |
|------|------|
| `qa-stakeholder-communication` | 干系人沟通 |
| `qa-code-review-for-test` | 代码评审 |
| `qa-team-coaching` | 团队赋能 |
| `qa-retrospective` | 复盘沉淀 |

### 专项测试（5个）
| 技能 | 功能 |
|------|------|
| `qa-specialized-testing` | 性能/安全/兼容性 |
| `qa-api-testing` | 接口测试 |
| `qa-exploratory-testing` | 探索式测试 |
| `qa-mobile-testing` | 移动端测试 |
| `qa-test-data-engineering` | 测试数据工程 |

### 管理能力（3个）
| 技能 | 功能 |
|------|------|
| `qa-test-automation-arch` | 自动化架构 |
| `qa-test-leadership` | 测试领导力 |
| `qa-tech-debt-management` | 技术债务管理 |

### 需求评审（1个）
| 技能 | 功能 |
|------|------|
| `qa-requirement-review` | 需求评审专项 |

## 安装

### 方式1：从 ClawHub 安装
```bash
/plugin install qa-test-skills
```

### 方式2：从 SkillHub 安装
```bash
/plugin marketplace add your-org/qa-test-skills-marketplace
/plugin install qa-test-skills
```

### 方式3：本地安装
```bash
/plugin dir /path/to/qa-test-skills
```

## 使用

### 快速开始

1. 安装插件后，输入：
```
/sa-test-workflow 帮我生成登录模块的测试用例
```

2. 技能集自动执行8步工作流：
   - 需求评审 → 需求解构 → 场景构建 → 深度设计 → 上下文工程 → 提示词生成 → 输出评审 → 测试报告

3. 输出专家级测试用例

### 单独使用技能

```bash
# 需求解构
/qa-test-skills:qa-req-deconstruction [需求描述]

# 边界分析
/qa-test-skills:qa-boundary-deep-dive [场景描述]

# Bug报告
/qa-test-skills:qa-bug-reporting [Bug描述]
```

## 工作流

```
用户输入（需求/文件/URL）
    │
    ▼
qa-requirement-review（需求评审）
    │
    ▼
qa-req-deconstruction（需求解构）
    │
    ▼
qa-risk-intuition + qa-heuristic-checklist + qa-scenario-tree（并行）
    │
    ▼
qa-boundary-deep-dive + qa-combination-strategy + qa-state-transition + qa-domain-modeling（并行）
    │
    ▼
qa-ai-context-engineering（上下文工程）
    │
    ▼
qa-ai-prompt-strategy（提示词生成）
    │
    ▼
[AI生成测试用例]
    │
    ▼
qa-ai-output-critique + qa-ai-blindspot-compensation（输出评审+补盲）
    │
    ▼
qa-test-reporting（测试报告）
    │
    ▼
最终输出：专家级测试用例
```

## 适用人群

| 角色 | 价值 |
|------|------|
| 初级测试 | 通过技能加载达到中级水平 |
| 中级测试 | 通过AI协作达到高级水平 |
| 高级测试 | 通过系统化达到资深水平 |
| 资深测试 | 通过赋能提升团队能力 |

## 贡献

欢迎贡献新技能！请参考：
1. Fork 本项目
2. 在 `skills/` 目录下创建新技能
3. 确保符合 Claude Code skills 规范
4. 提交 PR

## 许可证

MIT License

## 联系方式

- Issues: https://github.com/your-org/qa-test-skills/issues
- Email: your-email@example.com
