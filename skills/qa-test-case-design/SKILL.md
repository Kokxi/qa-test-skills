---
name: qa-test-case-design
description: >-
  当所有分析（需求解构、场景树、边界清单、组合矩阵）都已完成，需要把分析结果转化为结构化的测试用例时使用此技能。专注用例结构规范、分类体系、覆盖策略和优先级编排，产出全项目统一的 9 列标准格式用例。不要在分析还没做完时就跳到用例生成——没有充分的输入，用例一定是泛泛的。
  触发场景：设计测试用例、用例评审、用例覆盖、测试用例设计、用例模板、用例规范、用例格式、需要编写或规范测试用例时。 Use when the user asks about: designing structured test cases with P0-P3 prioritization, the canonical 9-column format, coverage strategy, and requirement traceability.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-test-case-design"
  display-name: "测试用例设计"
  version: "1.8.0"
  when-to-use: "用户说\"设计测试用例\"、\"用例评审\"、\"用例覆盖\"、\"测试用例设计\"、\"用例模板\"、\"用例规范\"、\"用例格式\"、需要测试用例结构指导、需要编写或规范测试用例时"
  related-skills: "{\"upstream\":[\"qa-req-deconstruction\",\"qa-boundary-deep-dive\",\"qa-scenario-tree\"],\"downstream\":[\"qa-test-skills\",\"qa-expert-review\",\"qa-regression-testing\"]}"
  references: "[\"assets/case-table.md\",\"references/output-template-full.md\",\"references/design-methods.md\",\"references/coverage-and-quality.md\",\"references/review-standards.md\"]"
  input-format: "{\"required\":[{\"name\":\"需求描述\",\"type\":\"string\",\"description\":\"功能需求的详细说明\"}],\"optional\":[{\"name\":\"场景分析\",\"type\":\"object\",\"description\":\"来自qa-scenario-tree的场景树\"},{\"name\":\"边界条件\",\"type\":\"object\",\"description\":\"来自qa-boundary-deep-dive的边界分析结果\"},{\"name\":\"业务背景\",\"type\":\"string\",\"description\":\"业务目标和用户角色\"}]}"
  output-format: "{\"traceability\":[\"每个用例带唯一ID：TC_{模块缩写}_{功能缩写}_{三位序号}（如 TC_API_LOGIN_001）——不使用场景后缀\",\"关联需求ID：REQ-{需求模块缩写}-{序号}\",\"关联场景ID：SC-{场景模块缩写}-{序号}\"],\"structure\":[{\"test_case_table\":\"测试用例表：固定 9 列（用例编号|测试类型|功能模块|测试标题|用例级别|预置条件|测试步骤|预期结果|风险等级）——全项目唯一标准，见 references/output-template-full.md\"},\"用例级别：P0≤20%（核心流程）/ P1≤40%（主要功能）/ P2≤30%（次要功能）/ P3≤10%（边缘场景）\",\"测试步骤：协议/接口/规则/计算类必填（含 method+path+关键参数）；UI/业务流程类可留空并标注「由执行人按实际系统补充」\",\"子功能并入「功能模块」用 模块/子功能 表示，不单设列；无「实际结果」列——那是 qa-execution-observation 的执行记录字段\",\"覆盖率：标注口径（基于现有需求/上游分析产出），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\"]}"
  error-recovery-guidance: "{\"on_failure\":\"用例设计遗漏维度时回退到边界分析和场景树补充\",\"retry_behavior\":\"补充上游后重新设计用例\"}"
  categories: "[\"Development\",\"Testing\"]"
  depth-requirement: "{\"reference_value\":\"见 references/output-template-full.md；用例总数不低于需求点的 3 倍\",\"minimum\":\"9 列齐全、编号唯一且合格式、P0-P3 占比达标、覆盖率标注口径\"}"
---

> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

# 测试用例设计专项

## 核心原则

测试用例设计的核心——明确"测什么"，而非"怎么测"。

> **重要限制**：禁止读取代码。测试用例必须基于需求文档，不得读取代码实现。
> 确保验证"系统应该做什么"，而非"系统如何实现"。

> **上游未完成就不要开始**：没有充分输入（需求解构 / 场景树 / 边界清单）时，
> 生成的用例一定是泛泛的。先补上游，再做本步。

## 1. 九列标准格式（本技能是全项目格式定义者）

| # | 列名 | 必填 | 要点 |
|---|------|------|------|
| 1 | 用例编号 | ✅ | `TC_{模块缩写}_{功能缩写}_{三位序号}`，同批不重号 |
| 2 | 测试类型 | ✅ | 按所属技能维度：功能/安全/异常/性能/契约/兼容性 |
| 3 | 功能模块 | ✅ | 必要时 `模块/子功能` 两级（子功能并入本列） |
| 4 | 测试标题 | ✅ | 动词开头，点明验证点 |
| 5 | 用例级别 | ✅ | P0/P1/P2/P3，占比见下 |
| 6 | 预置条件 | ✅ | 环境+数据+权限+状态，具体到可复现 |
| 7 | 测试步骤 | ⚠️ | **协议/规则/计算类必填**；UI/业务流程类可留空 |
| 8 | 预期结果 | ✅ | 可量化：状态码 / 返回结构 / 数据状态 / 副作用 |
| 9 | 风险等级 | ✅ | 高（资损/越权/数据错误/安全）/ 中 / 低 |

**为什么是 9 列**：这是 `validate_testcase_table.py` 与最终 `测试用例.csv` 的硬约束，
**不可增减列**。历史上曾有 10 列版本（含"子功能""实际结果"），已废止：
- 「子功能」并入「功能模块」用 `模块/子功能` 表示，信息不丢
- 「实际结果」是**执行阶段**字段，由 `qa-execution-observation` 承载，
  放进设计模板会导致执行时回填污染设计产物

**编号规则**：
```
TC_{模块缩写}_{功能缩写}_{三位序号}
TC_API_LOGIN_001   TC_CART_ADD_007   TC_ORDER_REFUND_003
```
> **不使用场景后缀**（如 `_NORMAL`）。场景类别写进「测试类型」与「测试标题」。
> 旧格式 `TC_USER_LOGIN_001_NORMAL` 已废止。

**级别占比**：P0 ≤ 20% / P1 ≤ 40% / P2 ≤ 30% / P3 ≤ 10%

**小规模例外**：用例总数 < 10 条时配额数学上不成立（20% 不足 1 条）。
加 `--no-quota` 跳过校验并在报告注明口径。**不要为凑比例编造用例或随意改级别。**

## 2. 「测试步骤」留空还是填（历史分歧的裁决）

| 用例类型 | 步骤 | 理由 |
|---------|------|------|
| **协议 / 接口类**（API、gRPC、WebSocket、Webhook、数据库） | **必填**，含 method + path + 关键参数 | 步骤由协议契约决定，不依赖实现，AI 能准确写出 |
| **配置 / 规则 / 计算类** | **必填** | 同上，规则本身确定 |
| **UI / 业务流程类** | **可留空**，标注「由执行人按实际系统补充」 | 同一"登录"不同系统实现完全不同，AI 强写必然与实际不符 |

> 历史版本一刀切要求"留空"，导致 API 类用例丢掉可执行性——而 API 的 method/path
> 恰恰是**规格的一部分**、不是实现细节。现按类型区分。

## 3. 加载时机

**需要时才读，不要一上来全读**：

| 什么时候读 | 读哪个 |
|-----------|--------|
| 拿 9 列模板来填 | [`assets/case-table.md`](assets/case-table.md)（表格 + 展开块两形态 + 逐列填写要求） |
| 查编号规则、级别定义、两处历史格式变更的来龙去脉 | [`references/output-template-full.md`](references/output-template-full.md)（**格式唯一真源**） |
| 选设计方法（等价类、判定表、正交、状态迁移、错误推测…） | [`references/design-methods.md`](references/design-methods.md) |
| 评估覆盖是否够、算覆盖率 | [`references/coverage-and-quality.md`](references/coverage-and-quality.md) |
| 做用例评审 | [`references/review-standards.md`](references/review-standards.md) |

## 4. 产出

```markdown
| 用例编号 | 测试类型 | 功能模块 | 测试标题 | 用例级别 | 预置条件 | 测试步骤 | 预期结果 | 风险等级 |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| TC_API_LOGIN_001 | 功能测试 | 认证/登录 | 正确凭证登录成功 | P0 | 账号 u1 已就绪，接口文档已提供 | POST /api/login，body {"user":"u1","pass":"***"} | 返回 200，响应含 token；调 /api/profile 有效；无堆栈泄露 | 高 |
| TC_API_LOGIN_002 | 安全测试 | 认证/登录 | 伪造 Token 被拒 | P0 | 已知合法 token 与签名算法 | 改 1 个字符后请求 /api/profile | 返回 401；响应不含内部信息与用户数据 | 高 |
| TC_API_LOGIN_003 | 异常测试 | 认证/登录 | 写操作超时重试不产生重复副作用 | P1 | 网关可注入延迟；写接口有幂等键 | 令首次请求延迟至超时，按服务端策略重放 2 次 | 重试成功且最终仅 1 次登录成功记录 | 中 |
```

> 上面 3 行只展示每列写法，完整模板见 `assets/case-table.md`。
> **任何技能产出用例都必须用这套 9 列**，有冲突以 `references/output-template-full.md` 为准。

## 5. 用例设计原则

**DO**
- 每个用例只验证一个明确目标
- 预期结果使用"应该/必须/会"等确定性词汇
- 同时包含正向与反向验证
- 标注敏感信息的脱敏处理方式
- 协议类填写具体 method/path/参数

**DON'T**
- 模糊描述如"检查是否可以正常工作"
- 一个用例混合多个验证点
- 忽略前置条件与环境配置
- 用主观判断代替客观测量
- 忽略异常处理流程
- 强制生成与实际系统不符的 UI 操作步骤

## 6. 交付前自检

- [ ] **9 列齐全**，无列错位、无单元格含 `|`
- [ ] 用例编号唯一、3 段式 `TC_{模块}_{功能}_{三位序号}`、无场景后缀
- [ ] 「功能模块」含子功能时用 `模块/子功能` 表达，未单设列
- [ ] 未出现「实际结果」列（属执行阶段）
- [ ] 测试步骤：协议/规则/计算类已填写；UI 类已标注"由执行人补充"
- [ ] 每条用例只验证一个目标
- [ ] 预期结果可客观验证（不是"正确""正常"）
- [ ] P0-P3 占比达标；<10 条时已注明实际分布口径
- [ ] 风险等级已填，非全高
- [ ] 覆盖率已标注口径，无"全覆盖/100%"绝对化表述
- [ ] 缺失模块已标"未覆盖 + 原因"

**机器校验**（列数、编号唯一性、级别/风险取值、占比、覆盖率措辞）：

```bash
python scripts/validate_testcase_table.py <用例文件>
```
