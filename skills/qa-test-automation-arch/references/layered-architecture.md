# 测试分层架构设计详解

> 本文是 `qa-test-automation-arch` 的**测试分层架构设计详解**。设计自动化框架分层时读本文；
其余部分留在 SKILL.md，不必读本文。

---


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
