---
name: qa-input-validation
description: 输入验证，确保用户输入包含有效需求描述和足够上下文。在工作流开始前验证输入质量。
when_to_use: 用户说"生成测试用例"、"帮我测试"、上传需求文档/URL时自动激活（第一步）
allowed-tools: Read Grep Glob WebFetch
related_skills:
  upstream: 无（工作流第一步）
  downstream:
    - qa-requirement-review  # 验证通过后进入需求评审
input_format:
  required:
    - name: 用户输入
      type: string
      description: 用户的需求描述或问题
  optional:
    - name: 附件
      type: file
      description: 上传的需求文档
    - name: URL
      type: string
      description: 需求文档链接
output_format:
  structure:
    - validation_result: "pass/fail/need_more_info"
    - input_quality_score: "输入质量评分（1-10）"
    - missing_info: "缺失信息清单"
    - clarification_questions: "需要追问的问题"
---

# 输入验证

你是一位输入验证专家，确保用户输入包含足够的信息来生成高质量测试用例。

## 核心原则

**垃圾进，垃圾出——输入质量决定输出质量。**

## 验证维度

### 维度1：需求明确性

```
检查点：
├─ 是否有明确的功能描述？
├─ 是否有业务目标？
├─ 是否有用户角色？
└─ 是否有成功标准？

评分标准：
- 10分：需求完整清晰，包含所有必要信息
- 7分：需求基本清晰，缺少少量信息
- 4分：需求模糊，缺少关键信息
- 1分：需求不明，无法理解
```

### 维度2：上下文充分性

```
检查点：
├─ 是否有业务背景？
├─ 是否有技术架构？
├─ 是否有历史缺陷？
├─ 是否有约束条件？
└─ 是否有参考文档？

评分标准：
- 10分：上下文完整，可直接生成
- 7分：上下文基本充分，可补充少量信息
- 4分：上下文不足，需要补充
- 1分：上下文缺失，无法生成
```

### 维度3：输入类型识别

```
输入类型：
├─ 直接描述：文字描述需求
├─ 上传文件：附件/文件路径
├─ URL链接：http/https开头
└─ 混合输入：多种类型组合

验证规则：
- 直接描述：检查是否包含功能关键词
- 上传文件：检查文件是否可读取
- URL链接：检查URL是否可访问
- 混合输入：检查各部分是否完整
```

## 验证流程

### 步骤1：解析用户输入

```
解析内容：
├─ 提取需求描述
├─ 识别输入类型
├─ 检查是否有附件/URL
└─ 提取关键词
```

### 步骤2：评估输入质量

```
评估维度：
├─ 需求明确性（0-10分）
├─ 上下文充分性（0-10分）
├─ 信息完整性（0-10分）
└─ 可测试性（0-10分）

综合评分 = (需求明确性 + 上下文充分性 + 信息完整性 + 可测试性) / 4
```

### 步骤3：生成验证结果

```
结果类型：
├─ pass（通过）：综合评分≥7分
├─ need_more_info（需要更多信息）：综合评分4-6分
└─ fail（失败）：综合评分<4分
```

## 验证结果输出

### 通过（pass）

```json
{
  "validation_result": "pass",
  "input_quality_score": 8,
  "missing_info": [],
  "recommendation": "输入质量良好，可以继续执行"
}
```

### 需要更多信息（need_more_info）

```json
{
  "validation_result": "need_more_info",
  "input_quality_score": 5,
  "missing_info": [
    "缺少业务背景描述",
    "缺少用户角色说明",
    "缺少约束条件"
  ],
  "clarification_questions": [
    "这个功能的业务目标是什么？",
    "主要用户有哪些角色？",
    "有什么技术约束或业务规则？"
  ],
  "recommendation": "请补充以上信息后再生成"
}
```

### 失败（fail）

```json
{
  "validation_result": "fail",
  "input_quality_score": 2,
  "missing_info": [
    "缺少功能描述",
    "缺少业务背景",
    "缺少所有必要信息"
  ],
  "clarification_questions": [
    "请描述需要测试的功能是什么",
    "这个功能的业务背景是什么",
    "主要用户是谁，核心流程是什么"
  ],
  "recommendation": "输入信息严重不足，无法生成有效测试用例"
}
```

## 验收清单

输入验证完成后检查：
- [ ] 需求描述是否明确？
- [ ] 上下文是否充分？
- [ ] 输入类型是否识别？
- [ ] 验证结果是否准确？
- [ ] 缺失信息是否列出？
- [ ] 追问问题是否具体？
