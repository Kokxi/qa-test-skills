# LLM E2E 评测报告

- **时间**: 20260706_215425
- **模型**: kimi-for-coding
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 1 |
| 断言（总） | 8 |
| 通过 | 0 |
| 失败 | 8 |
| 跳过（requires_e2e） | 0 |
| 错误 | 1 |
| 通过率 | 0.0% |
| Worker tokens | 0 |
| 总耗时 | 46s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-6 | 0/8 | 0 | 45.83338809013367s | 0 |

## 失败断言

- eval-6 **覆盖用户名边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖年龄边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖邮箱边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖密码边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖邀请码边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **有边界值分析**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **标注了风险等级**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **有结构化输出**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}

## 跳过断言（requires_e2e）

（无跳过）
