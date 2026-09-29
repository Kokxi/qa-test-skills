---
name: qa-tech-selection
description: >-
  当团队要选测试工具（自动化框架/性能工具/管理平台）、现有工具不能满足需求需要替换、或者公司要求做技术评估时使用此技能。通过多维度对比评估（功能覆盖/学习成本/社区活跃度/维护成本/扩展性）输出推荐方案和迁移实施建议。不要只看 Gartner 象限或者技术网红推荐——工具好不好取决于你的团队能力、技术栈和实际场景。每个推荐方案附带 POC 验证计划和风险提示。 触发场景：技术选型、工具选择、框架选择、用什么工具、工具对比、现有工具不能满足需求需要替换时。 Use when the user asks about: evaluating and selecting QA tooling — automation frameworks, performance tools, and management platforms — and planning the migration.
license: MIT
allowed-tools: Read Grep Glob WebFetch
metadata:
  slug: "qa-tech-selection"
  display-name: "测试技术选型"
  version: "1.8.0"
  when-to-use: "用户说\"技术选型\"、\"工具选择\"、\"框架选择\"、\"用什么工具\"、\"工具对比\"、需要评估测试技术方案、现有工具不能满足需求需要替换时"
  related-skills: "{\"upstream\":[\"qa-test-strategy-design\"],\"downstream\":[\"qa-ci-cd-testing\",\"qa-test-automation-arch\"]}"
  references: "[\"references/selection-framework.md\"]"
  input-format: "{\"required\":[{\"name\":\"项目需求\",\"type\":\"string\",\"description\":\"项目技术需求和非功能需求\"},{\"name\":\"技术约束\",\"type\":\"string\",\"description\":\"技术栈限制和团队能力\"}],\"optional\":[{\"name\":\"预算限制\",\"type\":\"string\",\"description\":\"工具和资源预算\"}]}"
  output-format: "{\"traceability\":[\"每次选型评估带唯一ID（SEL-XXXX）\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"tech_evaluation\":\"技术评估报告\"},{\"comparison_matrix\":\"对比矩阵\"},{\"recommendation\":\"推荐方案\"},{\"risk_assessment\":\"技术风险评估\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"工具选型遗漏关键维度时回退到测试策略补充需求\",\"retry_behavior\":\"补充需求后重新评估候选工具\"}"
  categories: "[\"Development\",\"Testing\",\"DevOps\"]"
  depth-requirement: "{\"reference_value\":\"根据选型复杂度调整评估深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少对比3个候选工具的核心维度\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

# 测试技术选型

## 核心原则

工具替换快，思维不过时——选型要基于业务需求，不是技术偏好。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 做工具选型评估时 | [`references/selection-framework.md`](references/selection-framework.md) |

> `选型框架`的完整内容已下沉至 `references/selection-framework.md`，避免每次触发都占用上下文。

## 常见选型场景

### 场景1：自动化框架选型

```text
选项对比：
├─ Playwright
│   ├─ 优点：多浏览器、自动等待、调试友好
│   ├─ 缺点：社区相对较小
│   └─ 适用：现代Web应用、多浏览器测试
│
├─ Cypress
│   ├─ 优点：实时调试、自动重试、CI友好
│   ├─ 缺点：仅支持Chrome、iframe支持差
│   └─ 适用：单页应用、快速反馈
│
├─ Selenium
│   ├─ 优点：生态成熟、语言支持多、社区大
│   ├─ 缺点：配置复杂、调试困难
│   └─ 适用：传统Web应用、多语言团队
│
└─ 决策依据：
    ├─ 团队技术栈
    ├─ 应用架构
    ├─ 测试需求
    └─ 维护成本
```

### 场景2：性能测试工具选型

```text
选项对比：
├─ JMeter
│   ├─ 优点：功能全面、插件丰富、社区大
│   ├─ 缺点：界面复杂、资源消耗大
│   └─ 适用：复杂性能测试、协议测试
│
├─ Locust
│   ├─ 优点：代码化、分布式、轻量
│   ├─ 缺点：需要编程能力
│   └─ 适用：API性能测试、分布式测试
│
├─ k6
│   ├─ 优点：现代化、脚本化、CI友好
│   ├─ 缺点：社区相对较小
│   └─ 适用：现代应用、DevOps集成
│
└─ 决策依据：
    ├─ 测试类型
    ├─ 团队技能
    ├─ 集成需求
    └─ 性能要求
```

### 场景3：测试管理平台选型

```text
选项对比：
├─ 开源方案
│   ├─ TestLink：功能简单、免费
│   ├─ 飞书/钉钉：协作方便、集成度高
│   └─ 自研：完全定制、成本高
│
├─ 商业方案
│   ├─ 禅道：功能全面、中文友好
│   ├─ JIRA：生态丰富、扩展性强
│   └─ Zephyr：JIRA集成、测试专业
│
└─ 决策依据：
    ├─ 团队规模
    ├─ 功能需求
    ├─ 预算限制
    └─ 集成需求
```

## 选型报告模板

```markdown
# 技术选型报告

## 1. 背景和目标
- 选型背景：[为什么要做选型]
- 选型目标：[要解决什么问题]
- 约束条件：[时间/预算/资源]

## 2. 需求分析
- 业务需求：[需求列表]
- 技术需求：[需求列表]
- 优先级：[需求优先级]

## 3. 方案对比
- 候选方案：[方案列表]
- 评估维度：[维度列表]
- 对比结果：[对比表格]

## 4. 推荐方案
- 推荐方案：[方案名称]
- 推荐理由：[为什么推荐]
- 风险提示：[风险和应对]

## 5. 实施计划
- 实施步骤：[步骤列表]
- 时间计划：[时间节点]
- 资源需求：[人力/预算]
```

## Examples

**需要选择Web UI自动化框架（Selenium vs Playwright vs Cypress）**
→ 需求分析：团队技术栈（Java/JS）、测试规模（100/1000/10000用例）、维护能力
→ 方案评估：社区活跃度、跨浏览器支持、稳定性、学习曲线
→ 决策矩阵：按权重打分，推荐Playwright（社区活跃+跨浏览器+速度快）

**团队想引入性能测试工具（JMeter vs Locust vs k6）**
→ 按技术栈（Python/Javascript）、协议支持、分布式能力、报告输出综合评估

## 输出示例

**场景：Python 项目的接口自动化框架选型**

**1. 需求分析**：Python 技术栈、需要 REST 接口自动化、需 CI 集成、团队 3 人、预算无（开源优先）

**2. 候选方案**：pytest+requests、Robot Framework、Karate、HttpRunner

**3. 决策矩阵（加权评分）**：

| 维度 | 权重 | pytest+requests | Robot Framework | Karate | HttpRunner |
|------|:---:|:---:|:---:|:---:|:---:|
| 技术栈匹配 | 25% | 5 | 4 | 3 | 5 |
| 自动化能力 | 20% | 5 | 4 | 4 | 4 |
| CI 集成 | 15% | 5 | 4 | 4 | 5 |
| 团队上手成本 | 20% | 4 | 3 | 3 | 5 |
| 维护成本 | 10% | 4 | 3 | 4 | 4 |
| 生态/社区 | 10% | 5 | 4 | 4 | 4 |
| **加权总分** | | **4.75** | **3.70** | **3.60** | **4.55** |

**4. 推荐结论**：**pytest+requests**（总分 4.75 最高）——技术栈匹配 + CI 生态成熟；HttpRunner 作为备选（国内社区友好、用例 YAML 化、团队上手快）。

**5. 实施计划**：第1周搭建框架+公共封装 → 第2周接入 CI → 第3周首批 50 条用例 → 第4周推广。

**场景：性能测试工具选型**
→ 需求（JMeter 全协议 / Locust Python 原生 / k6 云原生）→ 决策矩阵（协议支持/分布式/报告/团队熟悉度）→ 推荐结论（中小团队选 Locust，大规模压测选 JMeter，云原生选 k6）

## Guidelines

技术选型完成后检查：
- [ ] 需求分析是否完整？
- [ ] 候选方案是否全面？
- [ ] 评估维度是否合理？
- [ ] 对比结果是否客观？
- [ ] 推荐理由是否充分？
- [ ] 实施计划是否可行？


## 检查清单

- [ ] 候选工具是否≥3个？
- [ ] 核心维度是否对比？
- [ ] 维护成本是否评估？
- [ ] 团队适配是否考虑？
- [ ] 选型报告是否生成？
