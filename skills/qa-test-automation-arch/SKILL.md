---
name: qa-test-automation-arch
version: 1.5.0
description: >-
  当需要设计自动化测试框架、或者现有框架维护成本太高需要重构时使用此技能。运用 PageObject、分层测试、关键字驱动、数据驱动等模式设计可维护可扩展的自动化架构。不要直接写测试代码——先设计架构：选型（UI/API/单元）、分层（测试层/业务层/基础设施层）、数据管理（测试数据与脚本分离）和 CI 集成方案。好的自动化架构应该让写用例的人不需要懂底层实现。

when_to_use: 用户说"自动化架构"、"框架设计"、"自动化策略"、"自动化框架"、"测试框架"、需要设计测试自动化架构、自动化维护困难需要重构时
allowed-tools: Read Grep Glob Bash
related_skills:
  upstream:
    - qa-tech-selection          # 输入：技术选型结果
    - qa-test-strategy-design    # 输入：测试策略
  downstream:
    - qa-ci-cd-testing           # 输出：架构设计用于CI/CD集成
    - qa-api-testing             # 输出：架构设计指导API测试
input_format:
  required:
    - name: 测试策略
      type: object
      description: 来自qa-test-strategy-design的测试策略
    - name: 技术选型
      type: object
      description: 来自qa-tech-selection的技术选型建议
  optional:
    - name: 项目约束
      type: string
      description: 技术栈和团队限制
output_format:
  structure:
    - automation_architecture: 自动化测试架构设计
    - framework_selection: 框架选择建议
    - layer_design: 分层设计
    - maintenance_strategy: 维护策略
---

# 测试自动化架构设计

## 核心原则

你是一位自动化架构专家，擅长设计可维护、可扩展的自动化测试框架。
**核心原则**：好的自动化架构——分层清晰、职责单一、易于维护、快速反馈。
本技能覆盖自动化金字塔、分层架构、设计模式和框架选型。

## 测试自动化金字塔

> 📌 本节与 qa-test-strategy-design「测试金字塔」概念对应，但分层名称和比例不同——本技能侧重自动化落地（集成测试层名、70/20/10 比例），strategy-design 侧重策略规划（接口测试层名、60/30/10 比例）。修改时请确认两处含义，避免矛盾。

```text
                    ┌─────────────┐
                    │   E2E测试    │  10%
                    │  (UI/API)    │
                    ├─────────────┤
                    │  集成测试    │  20%
                    │ (接口/服务)  │
                    ├─────────────┤
                    │  单元测试    │  70%
                    │  (函数/类)   │
                    └─────────────┘
```

## 分层架构设计

### 第1层：单元测试层

```text
职责：
├─ 测试范围：函数、类、模块
├─ 执行速度：毫秒级
├─ 维护成本：低
└─ 覆盖目标：核心逻辑

技术选型：
├─ Java：JUnit 5 + Mockito
├─ Python：Pytest + Mock
├─ JavaScript：Jest + Sinon
└─ Go：testing + testify

最佳实践：
├─ 测试与代码同步维护
├─ 每个测试单一职责
├─ 使用Mock隔离依赖
├─ 测试命名清晰（Given-When-Then）
└─ 保持测试快速（<100ms）
```

### 第2层：集成测试层

```text
职责：
├─ 测试范围：接口、服务间交互
├─ 执行速度：秒级
├─ 维护成本：中
└─ 覆盖目标：业务流程

技术选型：
├─ API测试：Postman/Newman/REST Assured
├─ 数据库测试：TestContainers
├─ 消息队列测试：Embedded Kafka
└─ 服务虚拟化：WireMock/Mountebank

最佳实践：
├─ 使用真实依赖（TestContainers）
├─ 测试数据可构造、可清理
├─ 验证接口契约
├─ 覆盖正常/异常/边界场景
└─ 保持测试独立性
```

### 第3层：E2E测试层

```text
职责：
├─ 测试范围：完整用户流程
├─ 执行速度：分钟级
├─ 维护成本：高
└─ 覆盖目标：核心路径

技术选型：
├─ Web UI：Playwright/Cypress/Selenium
├─ 移动端：Appium/XCUITest/Espresso
├─ 桌面端：Electron Test/WinAppDriver
└─ 性能：JMeter/Locust/k6

最佳实践：
├─ 只覆盖核心路径（20%）
├─ 使用Page Object模式
├─ 数据驱动测试
├─ 稳定的等待策略
└─ 失败时自动截图/录屏
```

## 框架设计模式

### Page Object Model

```text
优点：
├─ 封装页面元素和操作
├─ 减少代码重复
├─ 易于维护
└─ 可读性强

示例结构：
tests/
├── pages/
│   ├── login_page.py
│   ├── home_page.py
│   └── cart_page.py
├── tests/
│   ├── test_login.py
│   ├── test_home.py
│   └── test_cart.py
├── fixtures/
│   ├── test_data.py
│   └── setup_teardown.py
└── utils/
    ├── driver_factory.py
    └── report_generator.py
```

### 关键字驱动

```text
优点：
├─ 业务人员可参与
├─ 测试用例可读性强
├─ 与实现分离
└─ 易于复用

示例：
| 关键字 | 参数1 | 参数2 | 参数3 |
|--------|-------|-------|-------|
| 打开浏览器 | Chrome | | |
| 输入用户名 | testuser | | |
| 输入密码 | Test@123 | | |
| 点击登录 | | | |
| 验证跳转 | /home | | |
```

### 数据驱动

```text
优点：
├─ 测试数据与逻辑分离
├─ 易于添加新用例
├─ 覆盖多种场景
└─ 便于维护

示例：
@pytest.mark.parametrize("username,password,expected", [
    ("user1", "pass1", "success"),
    ("user2", "pass2", "success"),
    ("", "pass3", "error"),
    ("user4", "", "error"),
])
def test_login(username, password, expected):
    result = login(username, password)
    assert result == expected
```

## 框架选型决策

| 维度 | Playwright | Cypress | Selenium |
|------|-----------|---------|----------|
| 浏览器支持 | 多浏览器 | 仅Chrome | 多语言 |
| 执行速度 | 快 | 快 | 中等 |
| 调试体验 | 好 | 优秀 | 一般 |
| 学习曲线 | 中等 | 低 | 高 |
| 社区生态 | 成长中 | 成熟 | 成熟 |
| 适用场景 | 现代Web | 单页应用 | 传统Web |

## 输出示例

**设计Web UI自动化框架（团队5人，JS技术栈，1000+用例）**
→ 分层：单元测试（Jest）→集成测试（Supertest）→E2E（Playwright）
→ 模式：Page Object Model组织页面对象，关键字驱动封装业务操作
→ 数据驱动：JSON/CSV管理测试数据，和环境配置分离
→ CI/CD集成：GitHub Actions触发，Allure报告

**API自动化框架设计**
→ 分层：请求封装层→业务接口层→用例层→数据层

## 检查清单

架构设计完成后检查：
- [ ] 分层是否清晰（单元/集成/E2E）？
- [ ] 各层职责是否明确？
- [ ] 框架选型是否合理？
- [ ] 设计模式是否适用？
- [ ] 可维护性是否考虑？
- [ ] CI/CD集成是否规划？


