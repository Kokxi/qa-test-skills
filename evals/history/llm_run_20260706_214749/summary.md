# LLM E2E 评测报告

- **时间**: 20260706_214749
- **模型**: kimi-for-coding
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 5 |
| 断言（总） | 39 |
| 通过 | 13 |
| 失败 | 19 |
| 跳过（requires_e2e） | 7 |
| 错误 | 2 |
| 通过率 | 40.6% |
| Worker tokens | 21580 |
| 总耗时 | 158s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-1 | 1/10 | 7 | 4.8s | 2699 |
| eval-2 | 6/6 | 0 | 24.6s | 4727 |
| eval-3 | 6/9 | 0 | 127.9s | 14154 |
| eval-4 | 0/6 | 0 | 0.2935802936553955s | 0 |
| eval-5 | 0/8 | 0 | 0.2032179832458496s | 0 |

## 失败断言

- eval-1 **用例包含TC唯一ID**: not found: TC_
- eval-1 **用例关联了需求ID**: not found: REQ-
- eval-3 **用例编号符合TC规范**: not found: TC_
- eval-3 **包含预置条件**: not found: 预置条件
- eval-3 **用例总数≥5条**: count=0, min=5
- eval-4 **评审维度≥4个**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-4 **每个维度有评分**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-4 **识别出用例问题**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-4 **有改进建议**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-4 **有结构化报告框架**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-4 **使用规范标记格式**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **覆盖POST接口**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **覆盖GET接口**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **覆盖DELETE接口**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **覆盖异常状态码**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **有参数组合测试**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **有安全测试**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **有结构化方案**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-5 **覆盖边界值**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}

## 跳过断言（requires_e2e）

- eval-1 需求评审报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 需求解构表已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 场景树已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 边界清单已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 AI提示词已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 评审或补盲已执行: requires_e2e: 无法在纯 LLM 模式下验证 file_exists_or
- eval-1 测试报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
