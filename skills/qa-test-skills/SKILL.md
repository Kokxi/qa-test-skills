---
name: qa-test-skills
description: 48个专家级测试技能集合，覆盖测试全生命周期。从需求分析到测试设计、AI协作、执行监控、质量度量，让初级测试人员输出专家级测试用例。
when_to_use: 用户说"软件测试"、"测试用例"、"测试设计"、"AI测试"、需要完整的测试设计能力时
allowed-tools: Read Grep Glob
related_skills:
  all_skills:
    - qa-test-workflow           # 主工作流编排
    - qa-requirement-review      # 需求评审
    - qa-req-deconstruction      # 需求解构
    - qa-scenario-tree           # 场景树构建
    - qa-boundary-deep-dive      # 边界深度分析
    - qa-test-case-design        # 测试用例设计
    - qa-ai-context-engineering  # 上下文工程
    - qa-ai-output-critique      # 输出评审
    - qa-api-testing             # 接口测试
    - qa-agent-testing           # Agent测试
    - qa-mobile-testing          # 移动端测试
    - qa-specialized-testing     # 专项测试
    - qa-test-strategy-design    # 测试策略
    - qa-quality-metrics         # 质量度量
    - qa-test-reporting          # 测试报告
input_format: 用户需求描述或需求文档
output_format: 完整的测试用例集 + 测试报告
---

# QA Test Skills - 软件测试技能集

## 技能集概述

这是一个包含48个专家级测试技能的完整集合，覆盖测试全生命周期。

## 核心价值

- **零学习成本**：用户无需改变现有习惯
- **专家级输出**：资深测试经验编码为可加载技能
- **完整追溯链**：需求→场景→用例→评审，全程可追溯
- **防止AI泛化**：限制AI读取代码，确保测试用例基于需求文档

## 技能分类

### AI协作（6个）
- **qa-ai-context-engineering**：构建AI测试上下文
- **qa-ai-prompt-strategy**：AI测试提示词策略
- **qa-ai-output-critique**：AI输出评审与补全
- **qa-ai-blindspot-compensation**：AI盲区补偿
- **qa-input-validation**：输入验证
- **qa-output-validation**：输出验证

### 需求分析（4个）
- **qa-requirement-review**：需求评审
- **qa-req-deconstruction**：需求解构与显隐式挖掘
- **qa-scenario-tree**：场景树构建
- **qa-domain-modeling**：领域建模

### 深度设计（4个）
- **qa-boundary-deep-dive**：边界深度分析
- **qa-combination-strategy**：组合测试策略
- **qa-state-transition**：状态转换测试
- **qa-heuristic-checklist**：启发式检查清单

### 执行洞察（4个）
- **qa-execution-observation**：执行观察力
- **qa-bug-root-cause-analysis**：Bug根因分析
- **qa-bug-reporting**：Bug报告编写
- **qa-expert-review**：专家评审与元学习

### 策略架构（13个）
- **qa-test-strategy-design**：测试策略制定
- **qa-release-risk-governance**：发布风险管理
- **qa-quality-metrics**：质量度量体系
- **qa-ci-cd-testing**：持续测试实践
- **qa-test-automation-arch**：测试自动化架构
- **qa-tech-selection**：测试技术选型
- **qa-test-env-data**：测试环境与数据管理
- **qa-test-data-engineering**：测试数据工程
- **qa-testability-advocacy**：可测试性推动
- **qa-shift-left**：测试左移实践
- **qa-shift-right**：测试右移实践
- **qa-test-leadership**：测试领导力
- **qa-test-reporting**：测试报告编写

### 沟通传承（4个）
- **qa-stakeholder-communication**：干系人沟通
- **qa-code-review-for-test**：测试视角的代码评审
- **qa-team-coaching**：团队赋能
- **qa-retrospective**：复盘与经验沉淀

### 专项测试（8个）
- **qa-api-testing**：接口测试专项
- **qa-mobile-testing**：移动端测试
- **qa-agent-testing**：AI Agent测试
- **qa-specialized-testing**：专项测试能力
- **qa-exploratory-testing**：探索式测试
- **qa-tech-debt-management**：技术债务管理
- **qa-test-estimation**：测试工作量估算
- **qa-defect-lifecycle**：缺陷生命周期管理

### 测试设计（4个）
- **qa-test-case-design**：测试用例设计
- **qa-critical-thinking**：测试批判性思维
- **qa-question-framework**：提问框架
- **qa-risk-intuition**：风险直觉与优先级判断

### 主工作流（1个）
- **qa-test-workflow**：测试工作流编排，自动串联所有技能

## 使用方式

### 方式1：使用主工作流（推荐）
```
请帮我测试这个项目：[需求文档路径]
```

### 方式2：单独使用技能
```
帮我分析这个场景的边界：[场景描述]
帮我设计测试用例：[需求描述]
```

### 方式3：批量安装所有技能
```bash
# 使用安装脚本
./install-skills.sh
```

## 安装说明

### 从GitHub安装
```bash
git clone https://github.com/Kokxi/qa-test-skills.git
/plugin dir ./qa-test-skills
```

### 从ClawHub安装
```bash
# 安装主工作流
clawhub install @kokxi/qa-test-workflow

# 安装其他技能
clawhub install @kokxi/qa-requirement-review
clawhub install @kokxi/qa-req-deconstruction
# ... 其他技能
```

### 一键安装所有技能
```bash
# 运行批量安装脚本
./install-all-skills.sh
```

## 技能协作关系

```
用户输入 → 输入验证 → 需求评审 → 需求解构 → 场景构建 → 深度设计 → 上下文工程 → 提示词生成 → AI生成 → 输出评审 → 盲区补盲 → 测试报告
```

## 示例项目

详见 `examples/ecommerce-project/` 目录下的完整示例。

## 联系方式

- **GitHub**: https://github.com/Kokxi/qa-test-skills
- **Issues**: https://github.com/Kokxi/qa-test-skills/issues
- **Email**: no19@foxmail.com