---
name: qa-test-skills-catalog
description: QA Test Skills 技能集的目录入口，列出全部50个测试技能。安装完整插件：openclaw plugins install clawhub:@kokxi/qa-test-skills。GitHub：https://github.com/Kokxi/qa-test-skills
when_to_use: 用户想浏览技能集目录、了解QA Test Skills包含哪些技能、查看技能分类说明、获取完整安装指引时
allowed-tools: Read Grep Glob
related_skills:
  all_skills:
    - qa-agent-testing
    - qa-ai-blindspot-compensation
    - qa-ai-context-engineering
    - qa-ai-output-critique
    - qa-ai-prompt-strategy
    - qa-api-testing
    - qa-boundary-deep-dive
    - qa-bug-reporting
    - qa-bug-root-cause-analysis
    - qa-ci-cd-testing
    - qa-code-review-for-test
    - qa-combination-strategy
    - qa-critical-thinking
    - qa-bug-lifecycle
    - qa-domain-modeling
    - qa-execution-observation
    - qa-expert-review
    - qa-exploratory-testing
    - qa-heuristic-checklist
    - qa-input-validation
    - qa-mobile-testing
    - qa-output-validation
    - qa-quality-metrics
    - qa-question-framework
    - qa-release-risk-governance
    - qa-req-deconstruction
    - qa-requirement-review
    - qa-retrospective
    - qa-risk-intuition
    - qa-scenario-tree
    - qa-shift-left
    - qa-shift-right
    - qa-specialized-testing
    - qa-stakeholder-communication
    - qa-state-transition
    - qa-team-coaching
    - qa-tech-debt-management
    - qa-tech-selection
    - qa-test-automation-arch
    - qa-test-case-design
    - qa-test-data-engineering
    - qa-test-env-data
    - qa-test-estimation
    - qa-test-leadership
    - qa-test-reporting
    - qa-test-strategy-design
    - qa-test-workflow
    - qa-testability-advocacy
input_format: 无（目录页，展示技能清单和安装指引）
output_format: 技能分类清单 + 安装指引
---

# QA Test Skills - 技能集目录

## ⚠️ 本技能是技能集的目录页

执行 `openclaw skills install @kokxi/qa-test-skills-catalog` 后你只获得了当前目录文件，**并没有安装完整的 50 个技能**。请参考下方安装方式获取完整技能集。

---

## 技能集概述

**QA Test Skills** 是一个包含 50 个专家级测试技能的完整集合，覆盖从需求分析到测试设计、AI协作、执行监控、质量度量的完整测试生命周期。

### 核心价值

- **零学习成本**：用户无需改变现有习惯
- **专家级输出**：资深测试经验编码为可加载技能
- **完整追溯链**：需求→场景→用例→评审，全程可追溯
- **防止AI泛化**：限制AI读取代码，确保测试用例基于需求文档

---

## 50个技能分类清单

### AI协作（6个）
| 技能 | 说明 |
|------|------|
| **qa-input-validation** | 输入验证，确保用户输入包含有效需求描述和足够上下文 |
| **qa-ai-context-engineering** | 构建AI测试上下文，让AI生成专家级测试用例 |
| **qa-ai-prompt-strategy** | AI测试提示词策略，优化AI输出的质量和覆盖度 |
| **qa-ai-output-critique** | AI输出评审与补全，六维评审标准 |
| **qa-ai-blindspot-compensation** | AI盲区补偿，识别六大盲区 |
| **qa-output-validation** | 输出验证，事实核查、一致性检查和可执行性验证 |

### 需求分析（4个）
| 技能 | 说明 |
|------|------|
| **qa-requirement-review** | 需求评审，完整性/清晰性/一致性/可测试性评估 |
| **qa-req-deconstruction** | 需求解构与显隐式挖掘，将模糊需求转化为结构化测试模型 |
| **qa-scenario-tree** | 场景树构建，主路径+分支+异常+数据流 |
| **qa-domain-modeling** | 领域建模，构建业务领域模型指导测试 |

### 深度设计（4个）
| 技能 | 说明 |
|------|------|
| **qa-boundary-deep-dive** | 边界深度分析，识别各类边界条件 |
| **qa-combination-strategy** | 组合测试策略，多条件组合的测试设计 |
| **qa-state-transition** | 状态转换测试，系统状态变化覆盖 |
| **qa-heuristic-checklist** | 启发式检查清单，8大功能类型测试要点模板 |

### 执行洞察（4个）
| 技能 | 说明 |
|------|------|
| **qa-execution-observation** | 执行观察力，测试过程中的信息捕获 |
| **qa-bug-root-cause-analysis** | Bug根因分析，从现象追溯到根因 |
| **qa-bug-reporting** | Bug报告编写，高质量缺陷报告 |
| **qa-expert-review** | 专家评审与元学习，将校正反馈用于持续优化 |

### 策略架构（14个）
| 技能 | 说明 |
|------|------|
| **qa-test-strategy-design** | 测试策略制定，基于风险和质量目标的策略设计 |
| **qa-release-risk-governance** | 发布风险管理，评估发布风险等级 |
| **qa-quality-metrics** | 质量度量体系，量化质量指标 |
| **qa-ci-cd-testing** | 持续测试实践，CI/CD中的测试集成 |
| **qa-test-automation-arch** | 测试自动化架构，自动化框架设计 |
| **qa-tech-selection** | 测试技术选型，工具和框架评估 |
| **qa-testability-advocacy** | 可测试性推动，提升系统可测试性 |
| **qa-test-data-engineering** | 测试数据工程，数据准备和管理 |
| **qa-test-env-data** | 测试环境与数据管理，环境配置与维护 |
| **qa-shift-left** | 测试左移实践，尽早介入测试 |
| **qa-shift-right** | 测试右移实践，生产环境验证 |
| **qa-test-leadership** | 测试领导力，团队管理和指导 |
| **qa-test-reporting** | 测试报告编写，结构化测试报告 |
| **qa-regression-testing** | 回归测试策略，变更驱动的精准回归方案 |

### 沟通传承（4个）
| 技能 | 说明 |
|------|------|
| **qa-stakeholder-communication** | 干系人沟通，测试信息有效传递 |
| **qa-code-review-for-test** | 测试视角的代码评审，代码变更分析 |
| **qa-team-coaching** | 团队赋能，提升团队测试能力 |
| **qa-retrospective** | 复盘与经验沉淀，持续改进 |

### 专项测试（8个）
| 技能 | 说明 |
|------|------|
| **qa-api-testing** | 接口测试专项，API接口全维度测试 |
| **qa-mobile-testing** | 移动端测试，App测试要点 |
| **qa-agent-testing** | AI Agent测试，智能体测试 |
| **qa-specialized-testing** | 专项测试能力，性能/安全/兼容性测试 |
| **qa-exploratory-testing** | 探索式测试，基于经验的探索 |
| **qa-tech-debt-management** | 技术债务管理，评估和跟踪技术债务 |
| **qa-test-estimation** | 测试工作量估算 |
| **qa-bug-lifecycle** | 缺陷生命周期管理 |

### 测试设计（4个）
| 技能 | 说明 |
|------|------|
| **qa-test-case-design** | 测试用例设计，用例结构/分类/覆盖策略 |
| **qa-critical-thinking** | 测试批判性思维，对每个"应该"都问"如果不呢" |
| **qa-question-framework** | 提问框架，不同场景下获取关键信息的提问模板 |
| **qa-risk-intuition** | 风险直觉与优先级判断，识别高风险区域 |

### 主工作流（1个）
| 技能 | 说明 |
|------|------|
| **qa-test-workflow** | 测试工作流编排，自动串联所有技能生成专家级测试用例 |

---

## 安装方式

执行以下任意一种方式获得完整的 50 个技能（含工作流）：

### 方式一：通过 ClawHub 安装 Plugin（推荐，一键获取全部技能）

```bash
openclaw plugins install clawhub:@kokxi/qa-test-skills
```

安装后启动新会话，直接输入测试需求即可使用。AI 会自动加载工作流和对应技能。

### 方式二：从 GitHub 克隆并本地加载

```bash
# 1. 克隆仓库
git clone https://github.com/Kokxi/qa-test-skills.git

# 2. 进入项目目录加载插件
cd qa-test-skills
/plugin dir ./qa-test-skills
```

### 方式三：单独安装某个技能（不推荐）

```bash
# 只安装需要的技能
openclaw skills install @kokxi/qa-test-workflow
openclaw skills install @kokxi/qa-requirement-review
# ... 按需安装其他技能
```

**注意**：方式三只安装单个技能，缺少完整的技能协作链路，建议使用方式一或方式二。

---

## 使用方式

### 使用主工作流（推荐）

直接输入测试需求，AI 会自动加载 `qa-test-workflow` 执行完整流程：
```
请帮我测试这个项目：examples/ecommerce-project/docs/prd.md
```

### 单独使用技能

```
帮我分析这个场景的边界：[场景描述]
帮我设计测试用例：[需求描述]
```

---

## 技能协作关系

```
用户输入 → 输入验证 → 需求评审 → 需求解构 → 场景构建 → 深度设计 →
上下文工程 → 提示词生成 → AI生成 → 输出评审 → 盲区补盲 → 测试报告
```

---

## 示例项目

详见 `examples/ecommerce-project/` 目录下的完整电商平台测试示例，包含需求文档和生成的测试用例。

---

## 联系方式

- **GitHub**: https://github.com/Kokxi/qa-test-skills
- **Issues**: https://github.com/Kokxi/qa-test-skills/issues
- **Email**: no19@foxmail.com
