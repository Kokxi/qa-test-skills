# LLM E2E 评测报告

- **时间**: 20260706_215353
- **模型**: kimi-for-coding
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 8 |
| 断言（总） | 52 |
| 通过 | 0 |
| 失败 | 52 |
| 跳过（requires_e2e） | 0 |
| 错误 | 8 |
| 通过率 | 0.0% |
| Worker tokens | 0 |
| 总耗时 | 321s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-6 | 0/8 | 0 | 45.881486892700195s | 0 |
| eval-7 | 0/8 | 0 | 45.790019035339355s | 0 |
| eval-8 | 0/5 | 0 | 45.84540915489197s | 0 |
| eval-9 | 0/6 | 0 | 45.747437953948975s | 0 |
| eval-10 | 0/5 | 0 | 45.74152064323425s | 0 |
| eval-11 | 0/6 | 0 | 45.76766562461853s | 0 |
| eval-12 | 0/8 | 0 | 45.73359489440918s | 0 |
| eval-13 | 0/6 | 0 | 0.2263321876525879s | 0 |

## 失败断言

- eval-6 **覆盖用户名边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖年龄边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖邮箱边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖密码边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **覆盖邀请码边界**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **有边界值分析**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **标注了风险等级**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-6 **有结构化输出**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有Bug标题**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有严重度**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有优先级**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有复现步骤**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有预期vs实际结果**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有影响范围**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有根因推测**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-7 **有附件建议**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-8 **有角色定义**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-8 **有输出格式**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-8 **有约束条件**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-8 **引用了输入**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-8 **有结构化输出**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **至少3个回归级别**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **有冒烟级别**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **有核心级别**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **有全量级别**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **有变更分析**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-9 **有执行建议**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-10 **有测试任务书**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-10 **有探索方法**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-10 **覆盖多个维度**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-10 **有会话模板**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-10 **关注边缘场景**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **有主路径**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **有分支路径**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **有异常路径**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **有业务规则**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **场景数≥6**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-11 **有层次结构**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖时序盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖并发盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖资源盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖状态盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖数据盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **覆盖第三方盲区**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **有风险标注**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-12 **统一补盲编号**: worker error: API error 403: {"error":{"message":"You've reached your usage limit for this billing cycle. Your quota will be refreshed in the next cycle. Upgrade to get more: https://www.kimi.com/code/console?from=quota-upgrade","type":"access_terminated_error"}}
- eval-13 **有测试范围**: worker error: [Errno 22] Invalid argument
- eval-13 **有分层策略**: worker error: [Errno 22] Invalid argument
- eval-13 **有资源分配**: worker error: [Errno 22] Invalid argument
- eval-13 **有质量门禁**: worker error: [Errno 22] Invalid argument
- eval-13 **有排期建议**: worker error: [Errno 22] Invalid argument
- eval-13 **结合了项目特点**: worker error: [Errno 22] Invalid argument

## 跳过断言（requires_e2e）

（无跳过）
