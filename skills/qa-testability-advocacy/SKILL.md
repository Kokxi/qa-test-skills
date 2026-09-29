---
name: qa-testability-advocacy
description: >-
  当测试发现"这个功能测不了"、"加个日志就能定位"、"这个模块没法 Mock"时使用此技能。从可控性（能否控制测试条件）、可观察性（能否看到内部状态）、可隔离性（能否独立测试）、自动化性和可诊断性五个维度评估系统的可测试性水平，给出具体的系统改进建议和推动策略。可测试性差的系统一定质量差——不是因为系统本身不好，是因为你根本测不透它。输出可测试性评估报告和各维度的改造建议。 ⚠️ 本技能含废弃测试清理建议，执行前请确认非关键数据。 触发场景：可测试性、难测、不好测、测试推动、架构改进、可测性评审、需要推动架构改进可测试性时。 Use when the user asks about: assessing and improving system testability — controllability, observability, isolatability, automability, and diagnosability.
license: MIT
allowed-tools: Read Grep Glob
metadata:
  slug: "qa-testability-advocacy"
  display-name: "Testability Advocacy"
  version: "1.8.0"
  when-to-use: "用户说\"可测试性\"、\"难测\"、\"不好测\"、\"测试推动\"、\"架构改进\"、\"可测性评审\"、需要评估可测试性、需要推动架构改进可测试性时"
  related-skills: "{\"upstream\":[\"qa-quality-metrics\",\"qa-execution-observation\"],\"downstream\":[\"qa-test-env-data\",\"qa-shift-left\"]}"
  references: "[\"references/testability-dimensions.md\"]"
  input-format: "{\"required\":[{\"name\":\"测试策略\",\"type\":\"object\",\"description\":\"来自qa-test-strategy-design的测试策略\"},{\"name\":\"架构设计\",\"type\":\"string\",\"description\":\"系统架构设计文档\"}],\"optional\":[{\"name\":\"代码库访问\",\"type\":\"string\",\"description\":\"代码库路径和结构\"}]}"
  output-format: "{\"traceability\":[\"每项推动建议带唯一ID（ADV-XXXX）\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"testability_assessment\":\"可测试性评估报告\"},{\"improvement_suggestions\":\"改进建议\"},{\"refactoring_guide\":\"重构指南\"},{\"best_practices\":\"可测试性最佳实践\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"可测试性推动遗漏问题时回退到代码评审补充\",\"retry_behavior\":\"补充评审后重新推动改进\"}"
  categories: "[\"Development\",\"Testing\",\"DevOps\"]"
  depth-requirement: "{\"reference_value\":\"根据系统问题调整推动深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少识别3个可测试性问题并提出改进建议\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

# 可测试性推动

## 核心原则

在架构评审阶段就能识别可测试性问题，推动开发做可测试设计。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 逐维打分或找改进项时，取五维详表 | [`references/testability-dimensions.md`](references/testability-dimensions.md) |

> `可测试性检查维度`的完整内容已下沉至 `references/testability-dimensions.md`，避免每次触发都占用上下文。

## 可测试性评估表

| 维度 | 检查点 | 现状 | 目标 | 差距 | 改进措施 |
|------|--------|------|------|------|---------|
| 接口层 | Mock点 | 无 | 有 | 大 | 开发Mock接口 |
| 数据层 | 数据构造 | 手动 | 自动 | 中 | 开发数据工厂 |
| 日志层 | TraceId | 无 | 有 | 大 | 接入链路追踪 |
| 配置层 | 功能开关 | 无 | 有 | 中 | 开发开关平台 |
| 依赖层 | 服务Mock | 无 | 有 | 大 | 开发服务虚拟化 |

## 可测试性改进建议

### 短期改进（1-2周）
```text
├─ 接口层：添加测试接口
├─ 数据层：编写数据构造脚本
├─ 日志层：添加关键路径日志
├─ 配置层：添加测试配置项
└─ 依赖层：配置Mock数据
```

### 中期改进（1-2月）
```text
├─ 接口层：开发Mock平台
├─ 数据层：开发数据工厂
├─ 日志层：接入链路追踪
├─ 配置层：开发开关平台
└─ 依赖层：开发服务虚拟化
```

### 长期改进（3-6月）
```text
├─ 接口层：契约测试平台
├─ 数据层：测试数据管理平台
├─ 日志层：日志分析平台
├─ 配置层：配置中心
└─ 依赖层：服务治理平台
```

## 应用场景

**评审订单系统的架构设计**
→ 接口层可测试性：订单接口是否支持Mock？是否有测试桩？
→ 数据层可测试性：数据库是否支持事务回滚？测试数据隔离？
→ 日志层可测试性：关键操作是否打印日志？日志级别是否可配置？
→ 配置层可测试性：功能开关是否支持动态配置？第三方服务地址是否可配置？
→ 依赖层可测试性：依赖服务是否有Mock方案？是否支持降级？

**开发说"这个不好测"**
→ 启动可测试性评估，逐维度分析，给出具体改进建议和沟通话术

## 自检清单

可测试性评估完成后检查：
- [ ] 是否评估了五个维度？
- [ ] 是否识别了差距？
- [ ] 是否制定了改进计划？
- [ ] 改进措施是否可行？
- [ ] 是否有时间计划？


## 检查清单

- [ ] 可测试性问题是否识别？
- [ ] 影响面是否评估？
- [ ] 改进建议是否可行？
- [ ] 优先级是否标注？
- [ ] 推动策略是否制定？
