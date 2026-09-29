# 需求输入校验与输出格式详解

> 本文是 `qa-input-validation` 的**需求输入校验与输出格式详解**。校验输入完整性或需要输出格式时读本文；
其余部分留在 SKILL.md，不必读本文。

---


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
