---
name: qa-api-testing
description: >-
  当需要测试 RESTful/GraphQL/gRPC/WebSocket 等 API 时使用此技能。覆盖接口的功能验证、参数组合、鉴权绕过、超时重试、幂等性、接口契约和向后兼容性。不要只测 HTTP 状态码——真正的接口 Bug 往往在数据结构不一致、字段类型不匹配、空值处理和并发调用上。输出接口测试矩阵、契约断言清单和工具选型建议。
  触发场景：接口测试、API测试、接口自动化、RESTful测试、GraphQL测试、gRPC测试、契约测试、接口安全测试、需要测试API时。 Use when the user asks about: API testing for REST, GraphQL, gRPC, WebSocket, SOAP, and webhook endpoints — contract validation, auth bypass, idempotency, timeout and retry behavior, and backward compatibility.
license: MIT
allowed-tools: Read Grep Glob Bash WebFetch
metadata:
  slug: "qa-api-testing"
  display-name: "接口测试"
  version: "1.8.0"
  when-to-use: "用户说\"接口测试\"、\"API测试\"、\"接口自动化\"、\"RESTful测试\"、\"GraphQL测试\"、\"gRPC测试\"、\"契约测试\"、\"接口安全测试\"、需要测试API时"
  related-skills: "{\"upstream\":[\"qa-test-automation-arch\",\"qa-req-deconstruction\"],\"downstream\":[\"qa-ci-cd-testing\",\"qa-execution-observation\"]}"
  references: "[\"references/core-flows.md\",\"references/test-cases.md\",\"references/tooling.md\",\"references/scenarios.md\",\"assets/case-template.md\"]"
  input-format: "{\"required\":[{\"name\":\"接口文档\",\"type\":\"string\",\"description\":\"API接口文档或契约文件\"},{\"name\":\"自动化架构\",\"type\":\"object\",\"description\":\"来自qa-test-automation-arch的自动化架构设计\"}],\"optional\":[{\"name\":\"测试策略\",\"type\":\"object\",\"description\":\"来自qa-test-strategy-design的测试策略\"}]}"
  output-format: "{\"traceability\":[\"每个接口测试用例带唯一ID：TC_{接口模块缩写}_{功能缩写}_{序号}（如 TC_API_LOGIN_001）\",\"关联接口契约ID\"],\"structure\":[{\"test_cases\":\"接口测试用例（固定 9 列 Markdown 表格：用例编号|测试类型|功能模块|测试标题|用例级别|预置条件|测试步骤|预期结果|风险等级）\"},\"用例级别：P0≤20%（核心流程）/ P1≤40%（主要功能）/ P2≤30%（次要功能）/ P3≤10%（边缘场景）\",\"覆盖率：标注口径（基于现有接口文档/契约），禁止\\\"全覆盖/100%\\\"绝对化表述；未覆盖接口标注\\\"未覆盖+原因\\\"\",\"占比取整：每维允许偏差 ≤1 条；接口数 <5 时以每维至少 1 条兜底并注明实际分布\"],\"api_test_plan\":\"接口测试方案\",\"mock_strategy\":\"Mock策略\",\"automation_scripts\":\"自动化脚本设计\",\"security_checks\":\"安全测试清单\"}"
  error-recovery-guidance: "{\"on_failure\":\"接口异常时记录完整请求/响应信息，增加重试机制\",\"retry_behavior\":\"修复网络/环境问题后重新执行接口测试\"}"
  categories: "[\"Development\",\"Testing\"]"
  depth-requirement: "{\"reference_value\":\"见正文「深度要求」表：简单接口=接口数×5 / 中等=×10 / 复杂=×15\",\"minimum\":\"六维全覆盖（功能/安全/异常/性能/契约/兼容）；接口数 <5 时以每维至少 1 条兜底，替代不可行的百分比配额\"}"
---

# 接口测试专项

## 核心原则

接口 Bug 大多不在状态码，而在**数据结构不一致、字段类型错配、空值处理与并发副作用**。
200 只能证明"通路是通的"，证明不了"数据是对的"。

## 1. 先定位接口类型（决定重心）

| 接口类型 | 典型代表 | 测试重点 | 协议特点 |
|---------|---------|---------|---------|
| **RESTful** | CRUD API、微服务接口 | 状态码、HTTP方法语义、RESTful规范符合度 | 无状态、资源导向、Cache |
| **GraphQL** | 聚合查询、数据中台 | 查询复杂度、N+1问题、权限细粒度 | 单一端点、按需查询 |
| **gRPC** | 内部服务通信、高吞吐场景 | 消息格式、流处理、超时重试 | Protobuf、双向流、高性能 |
| **WebSocket** | 实时推送、消息通知 | 连接管理、心跳、消息顺序 | 长连接、全双工、有状态 |
| **SOAP** | 企业级系统、金融/医疗 | WSDL契约验证、XML报文结构、WS-Security | XML、强契约、RPC风格 |
| **Webhook** | 支付回调、事件通知 | 验签、幂等性、超时重试、回调顺序 | HTTP回调、被动触发、需主动Mock |

## 2. 深度要求

| 复杂度 | 用例数要求 | 说明 |
|--------|-----------|------|
| 简单接口 | 接口数×5 | 单一功能接口 |
| 中等接口 | 接口数×10 | 多参数接口 |
| 复杂接口 | 接口数×15 | 多依赖/多状态接口 |

**必须覆盖的6个维度**：

| 维度 | 占比 | 说明 |
|------|------|------|
| 功能测试 | 40% | 正向/反向/边界/参数 |
| 安全测试 | 20% | 认证/授权/注入 |
| 异常测试 | 15% | 超时/重试/降级 |
| 性能测试 | 10% | 响应时间/并发 |
| 契约测试 | 10% | 接口契约验证 |
| 兼容性测试 | 5% | 版本兼容 |

> **偏差声明**：技能集通用六维标准为 功能/异常/边界/并发/安全/性能（见 `docs/standards.md`，装整套技能集时可得）。本技能针对 API 测试专项调整：将「边界」归入功能测试维（边界值验证是参数测试的子项）、将「并发」归入性能测试维（并发能力是 API 性能指标），新增「契约测试」与「兼容性测试」两维——这两者是接口测试的核心风险面（契约破裂与版本迁移），在通用功能测试中无独立维度。若与通用六维口径冲突，以本技能的六维为准，并在测试报告中说明。
>
> **小规模降级**：上表占比适用于接口数 ≥ 5 的项目。接口数 < 5 时配额在数学上无法成立（20% 安全测试不足 1 条），此时改为「每维至少 1 条 + 覆盖率标注实际口径」，不要为凑比例编造用例。占比取整规则（先保 P0 所属维 → 向下取整 → 偏差 ≤1 条）见 `references/core-flows.md`。

## 3. 加载时机

**需要时才读，不要一上来全读**：

| 什么时候读 | 读哪个 |
|-----------|--------|
| 展开某一维的测试范围，或交付前逐项自检（32 项） | [`references/core-flows.md`](references/core-flows.md)（六维详图 + Mock 策略 + 检查清单） |
| 生成具体测试用例；被测接口是 GraphQL/gRPC/WebSocket/SOAP/Webhook | [`references/test-cases.md`](references/test-cases.md)（39 条用例 + OWASP API Top 10 对照 + 协议专项） |
| 选工具，或要展开某工具能力边界 | [`references/tooling.md`](references/tooling.md)（默认选型 + 能力矩阵 + 性能工具） |
| 用户描述的情况命中特定风险场景 | [`references/scenarios.md`](references/scenarios.md)（5 个场景，校正测试重心） |
| 写用例表 | [`assets/case-template.md`](assets/case-template.md)（9 列模板 + 填写要求） |

## 4. 工具默认选型

没别的约束就用这套：

| 场景 | 默认工具 | 理由 |
|------|---------|------|
| 日常调试与文档 | Postman / Apifox | 上手最快，协作与文档一体 |
| 自动化执行 | **pytest + requests**（Python）/ REST Assured（Java） | 生态成熟、易接 CI |
| 契约测试 | **Pact**（消费者驱动）/ Schemathesis（OpenAPI 校验） | 前者管协作方破坏性变更，后者管实现偏离契约 |
| 第三方与异常 Mock | **WireMock** | 延迟/超时/脏数据开箱即用 |
| 性能 | **k6**（CI 友好）；需 GUI 分布式再选 JMeter | 压测按需引入，非默认动作 |

> 明确"单工具全栈"诉求用 **Karate**。gRPC 用 grpcurl 调试（WireMock 不覆盖流式语义）。
> 完整能力矩阵与选型避坑见 [`references/tooling.md`](references/tooling.md)。

## 5. 输出格式

**9 列标准表格**：

| 用例编号 | 测试类型 | 功能模块 | 测试标题 | 用例级别 | 预置条件 | 测试步骤 | 预期结果 | 风险等级 |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| TC_API_LOGIN_001 | 功能测试 | 登录接口 | 正确凭证登录成功 | P0 | 接口文档已提供，账号已就绪 | 发送POST /api/login，参数{user,pass} | 返回200，响应含token且有效 | 高 |
| TC_API_LOGIN_002 | 安全测试 | 登录接口 | Token伪造被拒绝 | P0 | 合法Token已知 | 修改Token签名后请求受保护接口 | 返回401，拒绝访问 | 高 |
| TC_API_LOGIN_003 | 异常测试 | 登录接口 | 超时重试幂等性 | P1 | 模拟网关超时 | 请求超时后自动重试2次 | 重试成功且无重复副作用 | 中 |

> 上面 3 行只用于展示**每列的写法**，不是完整用例集。P0≤20% 等占比约束作用于最终交付的整份用例集，
> 不要照抄这 3 行的级别分布。完整模板见 [`assets/case-template.md`](assets/case-template.md)。

**方案产出顺序**：接口类型定位 → 六维用例矩阵 → Mock 策略 → 自动化脚本设计 → 安全清单 → 风险提示。

## 6. 交付前自检

- [ ] 9 列齐全，无列错位、无单元格含 `|`（会破坏表格与 CSV）
- [ ] 用例编号唯一且符合 `TC_{模块}_{功能}_{序号}`
- [ ] P0-P3 占比符合；接口数 <5 时已注明实际分布口径
- [ ] 覆盖率已标注口径，无"全覆盖/100%"绝对化表述
- [ ] 未覆盖接口已写明"未覆盖 + 原因"
- [ ] 六维检查清单已逐项过（见 `references/core-flows.md` 第 8 节）

**机器校验**：

```bash
python scripts/validate_testcase_table.py <用例文件>
```

覆盖列数、编号唯一性、级别/风险取值、占比、覆盖率措辞。报错先修再交付。
