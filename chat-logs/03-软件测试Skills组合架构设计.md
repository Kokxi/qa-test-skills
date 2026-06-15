# 03 - 软件测试 Skills 组合架构设计

## 设计原则

1. **全生命周期覆盖** — 从需求分析到上线后的线上监控，不遗漏阶段
2. **独立可组合** — 每个 skill 聚焦一个领域，可单独加载，也能按阶段组合
3. **从抽象到具体** — 上层偏策略/思维，下层偏工具/执行
4. **按使用频率分层** — 高频基础技能 vs 低频专项技能

---

## 总体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    第零层：测试基础                               │
│              test-basics（思维、术语、流程框架）                    │
└─────────────────────────────────────────────────────────────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│  第一层：分析设计  │ │  第二层：执行工具  │ │  第三层：测试管理     │
│                  │ │                  │ │                      │
│ test-req-analysis │ │ api-testing     │ │ test-planning        │
│ test-case-design  │ │ ui-automation   │ │ defect-management    │
│ test-data-mgmt    │ │ performance-test│ │ test-reporting       │
│ exploratory-test  │ │ security-test   │ │ test-ci-cd          │
│                   │ │ mobile-testing  │ │ agile-testing       │
│                   │ │ chaos-testing   │ │                     │
└─────────────────┘ └─────────────────┘ └──────────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  第四层：专项领域   │
                  │ game-testing      │
                  │ fintech-testing   │
                  │ embedded-testing  │
                  └──────────────────┘
```

---

## 技能清单（共 13 个 Skill）

---

### 第零层：基础通识

#### 1. `test-basics` — 软件测试基础

| 维度 | 内容 |
|------|------|
| 核心概念 | 测试目的、验证 vs 确认、质量模型（ISO 25010） |
| 测试分类 | 功能/非功能、白盒/黑盒/灰盒、静态/动态、手动/自动 |
| 测试流程 | 需求→计划→设计→执行→报告→复盘 |
| 开发模型 | 瀑布/V模型/W模型/敏捷/DevOps下测试的差异 |
| 核心思维 | 批判性思维、探索思维、不可能穷尽原则、杀虫剂悖论 |
| **触发词** | 测试基础、测试入门、测试理论、质量模型 |

---

### 第一层：分析设计（测试左移）

#### 2. `test-req-analysis` — 需求分析与测试策略

| 维度 | 内容 |
|------|------|
| 需求分析 | 显性需求 vs 隐性需求、正向/反向/边界场景推导 |
| 风险评估 | 基于风险的测试策略（RBT）、优先级矩阵、影响范围评估 |
| 测试策略 | 什么阶段测什么、自动化 vs 手动的分界线、深度 vs 广度取舍 |
| 可测试性 | 推动需求阶段明确验收条件、埋点、日志 |
| **触发词** | 测试策略、需求分析、风险评估、测试范围、测试准入准出 |

#### 3. `test-case-design` — 用例设计方法

| 维度 | 内容 |
|------|------|
| 黑盒方法 | 等价类划分、边界值分析、因果图/判定表、正交实验、场景法 |
| 白盒方法 | 语句覆盖、判定覆盖、条件覆盖、路径覆盖、MC/DC |
| 经验方法 | 错误推测法、基于 checkist 的覆盖 |
| 用例组织 | 用例层次结构、优先级标注、可维护性、复用性 |
| **触发词** | 用例设计、测试用例、等价类、边界值、覆盖、正交、判定表 |

#### 4. `test-data-mgmt` — 测试数据管理

| 维度 | 内容 |
|------|------|
| 数据准备 | SQL 构造、API 造数、工具（Faker、Mockaroo） |
| 数据策略 | 静态数据集、按需生成、数据工厂模式 |
| 敏感数据 | 数据脱敏、合规（GDPR/个保法）、生产数据脱敏复用 |
| 数据清理 | 测试前后的数据状态管理、隔离策略 |
| **触发词** | 测试数据、造数、数据脱敏、数据工厂、test data |

#### 5. `exploratory-testing` — 探索式测试

| 维度 | 内容 |
|------|------|
| 核心思维 | Session-based test management、charter 编写 |
| 测试编排 | 漫游测试（卖点/地标/旅伴）、角色扮演 |
| 记录方法 | 思维导图、笔记模板、Bug 描述 |
| 落地时机 | 什么时候做探索式测试、和脚本化测试的配合 |
| **触发词** | 探索式测试、漫游测试、session-based、ad-hoc、自由测试 |

---

### 第二层：执行工具

#### 6. `api-testing` — 接口测试

| 维度 | 内容 |
|------|------|
| 理论基础 | HTTP 协议、RESTful/GraphQL/gRPC、状态码、请求/响应结构 |
| 工具使用 | Postman / Apifox — 集合管理、环境变量、断言、预请求脚本 |
| 自动化框架 | Requests + Pytest / REST Assured / supertest |
| 进阶 | 鉴权机制、签名校验、Mock 服务、契约测试 |
| **触发词** | 接口测试、API测试、Postman、Apifox、REST Assured、HTTP |

#### 7. `ui-automation` — UI 自动化测试

| 维度 | 内容 |
|------|------|
| 工具选择 | Selenium / Playwright / Cypress — 对比、适用场景 |
| 框架设计 | Page Object Model、数据驱动、关键字驱动 |
| 稳定性 | 等待策略（显式/隐式/流畅等待）、重试机制、截图/视频 |
| CI 集成 | 无头模式、并行执行、Docker 化、报告输出 |
| **触发词** | UI自动化、Selenium、Playwright、Cypress、Page Object、E2E |

#### 8. `performance-testing` — 性能测试

| 维度 | 内容 |
|------|------|
| 概念体系 | TPS/QPS、RT（P50/P95/P99）、并发用户、吞吐量、瓶颈 |
| 工具 | JMeter（线程组/监听器/断言）、Locust（Python脚本化）、wrk |
| 测试类型 | 负载测试、压力测试、稳定性测试、尖峰测试、容量规划 |
| 分析方法 | CPU/内存/IO/网络指标、DB 慢查询、GC 分析、链路追踪 |
| **触发词** | 性能测试、JMeter、Locust、压力测试、负载测试、TPS、P99 |

#### 9. `security-testing` — 安全测试

| 维度 | 内容 |
|------|------|
| 基础知识 | OWASP Top 10、CIA 三元组、常见攻击面 |
| 核心场景 | SQL 注入、XSS、CSRF、越权、认证绕过、敏感信息泄露 |
| 工具 | Burp Suite、OWASP ZAP、SQLMap、Nmap |
| 方法 | 威胁建模（STRIDE）、渗透测试流程、安全 code review |
| **触发词** | 安全测试、渗透测试、OWASP、SQL注入、XSS、越权、Burp Suite |

#### 10. `mobile-testing` — 移动端测试

| 维度 | 内容 |
|------|------|
| 专项测试 | 安装/卸载/升级、中断测试（电话/短信/通知）、耗电/流量 |
| 自动化 | Appium / XCTest / Espresso / Airtest |
| 兼容性 | 真机 vs 模拟器、屏幕适配、系统版本覆盖 |
| 弱网 | 弱网模拟（Charles / Network Link Conditioner）、离线场景 |
| **触发词** | 移动测试、Appium、Android测试、iOS测试、兼容性、弱网 |

#### 11. `chaos-testing` — 混沌工程

| 维度 | 内容 |
|------|------|
| 核心理念 | 稳态假设、爆炸半径、最小化影响 |
| 实验设计 | 基础设施故障（网络延迟/丢包/节点宕机）、服务故障 |
| 工具 | Chaos Monkey、Chaos Mesh、Litmus |
| 落地 | 从哪开始、怎么逐步扩大、如何度量系统韧性 |
| **触发词** | 混沌工程、Chaos Monkey、Chaos Mesh、韧性测试、故障注入 |

---

### 第三层：管理度量

#### 12. `test-ci-cd` — CI/CD 与质量门禁

| 维度 | 内容 |
|------|------|
| 流水线阶段 | 代码检查 → 单元测试 → 接口测试 → UI 测试 → 性能门禁 |
| 质量门禁 | 覆盖率阈值、测试通过率、性能基线、安全扫描准入 |
| 环境管理 | 测试环境搭建、Docker/K8s 容器化、环境一致性 |
| 策略选择 | 全量 vs 增量、每日 vs 每次提交、并行策略 |
| **触发词** | CI/CD、流水线、质量门禁、Jenkins、GitLab CI、GitHub Actions |

#### 13. `test-management` — 测试管理与度量

| 维度 | 内容 |
|------|------|
| 测试计划 | 工作量估算（功能点/经验法）、资源排期、交付物定义 |
| 缺陷管理 | Bug 生命周期、根因分析（5 Whys / Fishbone）、缺陷度量 |
| 质量度量 | 漏测率、逃逸率、缺陷密度、RCA 分析、覆盖率趋势 |
| 流程改进 | 测试复盘、过程资产沉淀、团队能力建设 |
| **触发词** | 测试管理、测试计划、缺陷管理、质量度量、漏测分析、复盘 |

---

### 第四层：专项领域（按需扩展）

```
game-testing       — 游戏测试（数值平衡、手感、兼容性）
fintech-testing    — 金融测试（资金安全、合规、账务一致性）
embedded-testing   — 嵌入式/硬件测试（稳定性、实时性）
bigdata-testing    — 大数据测试（数据准确性、ETL、性能）
ai-testing         — AI/ML 测试（模型评估、偏见检测、鲁棒性）
```

---

## 技能依赖关系图

```
test-basics（必须最先掌握）
    │
    ├──→ test-req-analysis
    │         │
    │         ├──→ test-case-design
    │         │         │
    │         │         ├──→ api-testing（接口用例设计依赖用例设计方法）
    │         │         ├──→ ui-automation（UI用例设计同理）
    │         │         └──→ exploratory-testing（补充方法）
    │         │
    │         └──→ test-data-mgmt（需求分析驱动数据策略）
    │
    ├──→ 执行层（api/ui/performance/security/mobile/chaos）
    │         各执行技能可并行学习，依赖 test-basics 和 test-case-design
    │
    └──→ 管理层（test-planning + test-ci-cd + defect-mgmt）
              依赖执行层实践经验的积累
```

---

## 推荐实施路线

按团队或个人实际情况选择切入路线：

### 路线 A：从 0 开始
```
test-basics →  test-req-analysis →  test-case-design →  api-testing
        →  defect-management →  test-ci-cd →  ui-automation
        →  performance-testing →  test-management
```

### 路线 B：手工转自动化
```
api-testing →  test-ci-cd →  ui-automation →  test-data-mgmt
        →  performance-testing →  剩余选学
```

### 路线 C：转管理岗
```
test-req-analysis →  test-planning →  defect-management
        →  test-reporting →  test-management →  剩余了解即可
```

---

## 预期产出物

每个 skill 创建后包含：
- `SKILL.md` — 完整技能指南（概念 + 方法 + 最佳实践 + 工具 + checklist）
- 可选附带模板（用例模板、Bug 模板、计划模板、报告模板）
