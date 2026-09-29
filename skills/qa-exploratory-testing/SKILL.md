---
name: qa-exploratory-testing
description: >-
  当脚本化测试覆盖得差不多了、但直觉告诉你"可能还有东西没测到"时使用此技能。用系统化的探索方法（场景漫游、角色扮演、失败路径、标杆对比）来发现预设测试用例覆盖不到的问题。探索式测试不是随便点——它是有明确 charter（任务书）和时长的有目的探索。每次探索需要记录 session 笔记和发现的问题列表。 触发场景：探索测试、自由测试、漫游测试、场景发现、到处点一点、随机测试、角色扮演、SBTM、新产品快速验证时。 Use when the user asks about: exploratory testing with a charter — scenario roaming, role play, failure-path probing, benchmark comparison, and session notes.
license: MIT
allowed-tools: Read Grep Glob Bash
metadata:
  slug: "qa-exploratory-testing"
  display-name: "Exploratory Testing"
  version: "1.8.0"
  when-to-use: "用户说\"探索测试\"、\"自由测试\"、\"漫游测试\"、\"场景发现\"、\"到处点一点\"、\"随机测试\"、\"角色扮演\"、\"SBTM\"、需要发现脚本化测试遗漏的问题、新产品快速验证时"
  related-skills: "{\"upstream\":[\"qa-scenario-tree\",\"qa-risk-intuition\"],\"downstream\":[\"qa-bug-reporting\",\"qa-retrospective\"]}"
  references: "[\"references/charter-methods.md\"]"
  input-format: "{\"required\":[{\"name\":\"测试目标\",\"type\":\"string\",\"description\":\"探索式测试的目标和范围\"},{\"name\":\"探索领域\",\"type\":\"string\",\"description\":\"待探索的功能领域和特性\"}],\"optional\":[{\"name\":\"启发式清单\",\"type\":\"array\",\"description\":\"来自qa-heuristic-checklist的启发式检查项\"},{\"name\":\"时间盒\",\"type\":\"string\",\"description\":\"探索时间限制\"}]}"
  output-format: "{\"traceability\":[\"每个探索session带唯一ID（EXP-XXXX）\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"exploration_charter\":\"探索章程\"},{\"session_notes\":\"探索笔记\"},{\"findings\":\"发现清单\"},{\"bug_reports\":\"发现缺陷报告\"},{\"coverage_notes\":\"覆盖记录\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"记录探索路径，切换测试策略或结束当前Session\",\"retry_behavior\":\"开启新Session，尝试不同的探索方向\"}"
  categories: "[\"Development\",\"Testing\"]"
  depth-requirement: "{\"reference_value\":\"根据探索目标调整session深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少完成1个charter的session笔记和发现清单\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

> **⚠️ 安全警告**：本技能的示例可能涉及订单号、支付金额、截图、身份证、手机号等敏感数据。
> 实际使用时请勿粘贴真实生产数据、客户信息或财务凭证；测试前应脱敏/掩码处理。
> 本技能仅在 workspace/ 输出评估文件，不持久化、不外传、不跨会话复用。

# 探索式测试

## 核心原则

探索式测试不是随意测试，而是有章程、有记录、有学习的系统化探索。
本技能基于SBTM框架（Session-Based Test Management）进行结构化探索。

## 深度要求（参考值）

**关键指标**：根据功能复杂度调整探索深度

| 复杂度 | Session要求 | Bug发现目标 | 说明 |
|--------|------------|------------|------|
| 简单功能 | 1-2个Session | 3-5个发现 | 单一功能/页面 |
| 中等功能 | 3-5个Session | 8-15个发现 | 多页面/流程功能 |
| 复杂功能 | 5-8个Session | 15-30个发现 | 跨模块/核心业务流 |

## Session-Based Test Management（SBTM）

### Charter（测试章程）

```text
Charter结构：
├─ 探索（Explore）
├─ 学习（Learn）
├─ 关于（About）
├─ 使用（Using）
├─ 发现（Discover）
└─ 信息（Information）

示例：
"探索用户登录功能，学习它如何处理异常输入，
使用边界值和特殊字符，发现潜在的安全漏洞和用户体验问题。"
```

### Session类型

```text
├─ 探索Session：发现新问题
│   ├─ 时长：60-120分钟
│   ├─ 目标：发现新Bug、新风险
│   └─ 记录：发现、问题、疑问
│
├─ 评审Session：验证修复
│   ├─ 时长：30-60分钟
│   ├─ 目标：验证Bug修复、回归测试
│   └─ 记录：验证结果、遗留问题
│
└─ 调研Session：技术调研
    ├─ 时长：60-120分钟
    ├─ 目标：了解系统、评估可测试性
    └─ 记录：系统架构、技术细节
```

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 设计 charter、选漫游手法时 | [`references/charter-methods.md`](references/charter-methods.md) |

> `漫游测试方法`的完整内容已下沉至 `references/charter-methods.md`，避免每次触发都占用上下文。

## 角色扮演测试

### 用户角色

```text
角色类型：
├─ 新手用户：第一次使用
│   ├─ 关注：学习成本、引导设计
│   └─ 探索：误操作、困惑点
│
├─ 普通用户：日常使用
│   ├─ 关注：效率、稳定性
│   └─ 探索：常用路径、痛点
│
├─ 专家用户：高频使用
│   ├─ 关注：效率、高级功能
│   └─ 探索：快捷键、批量操作
│
└─ 恶意用户：异常使用
    ├─ 关注：安全、稳定性
    └─ 探索：注入、越权、破坏
```

### 角色卡片模板

```markdown
## 角色卡片

### 基本信息
- 角色名称：[名称]
- 使用频率：[每天/每周/偶尔]
- 技术水平：[新手/普通/专家]
- 核心诉求：[最关心什么]

### 使用场景
- 典型操作：[日常操作]
- 使用时间：[工作时间/随时随地]
- 使用设备：[PC/手机/平板]

### 痛点预期
- 常见问题：[可能遇到的问题]
- 不满点：[可能不满意的地方]
- 误操作：[可能的误操作]
```

## 探索记录模板

```markdown
## 探索式测试Session记录

### 基本信息
- Charter：[测试章程]
- 测试人员：[姓名]
- 开始时间：[时间]
- 持续时长：[时长]
- 测试环境：[环境信息]

### 探索笔记
| 时间 | 操作 | 观察 | 发现 |
|------|------|------|------|
| 10:00 | 打开登录页面 | 页面正常 | 无 |
| 10:05 | 输入特殊字符 | 提示格式错误 | 正常 |
| 10:10 | 并发点击登录 | 重复提交 | 潜在Bug |

### 发现汇总
- Bug：[数量]
- 风险：[数量]
- 疑问：[数量]
- 建议：[数量]

### 问题详情
| ID | 类型 | 描述 | 严重程度 |
|----|------|------|---------|
| EXP-001 | Bug | 并发点击导致重复订单 | 高 |
| EXP-002 | 风险 | 无登录超时机制 | 中 |

### 遗留事项
- [ ] 待验证：[事项]
- [ ] 待深入：[事项]
- [ ] 待确认：[事项]
```

## 输出示例

**探索"商品搜索"功能**
→ 创建Charter："探索商品搜索的边界和异常行为（30分钟）"
→ 漫游方法：卖点漫游（正常搜索）→地标漫游（空结果/特殊字符）→风险漫游（SQL注入）
→ 发现：搜索"%"导致数据库报错（SQL注入风险）
→ 记录Session笔记，将发现转化为脚本化测试用例

**探索"用户注册"流程**
→ 角色扮演：普通用户（正常注册）→恶意用户（批量注册）→忘记密码用户

## 异常处理引导

| 场景 | 表现 | 处理方式 |
|------|------|---------|
| Charter目标过大 | 30分钟无法完成Charter | 拆分为多个子Charter，每个聚焦一个维度 |
| 探索方向迷失 | 测试过程中偏离初始目标 | 暂停回顾Charter，必要时重新明确目标 |
| 发现过多但时间不够 | 大量发现来不及深入验证 | 按风险优先排序，高风险当场深挖，低风险记录待办 |
| 无法复现探索发现 | 探索时遇到的问题无法稳定复现 | 记录环境和操作序列，截图+日志辅助，降级为风险项 |

## 检查清单

探索式测试完成后检查：
- [ ] Charter是否清晰定义？
- [ ] 探索笔记是否完整记录？
- [ ] 发现是否分类整理？
- [ ] Bug报告是否规范？
- [ ] 遗留事项是否跟踪？
- [ ] 经验是否沉淀？
