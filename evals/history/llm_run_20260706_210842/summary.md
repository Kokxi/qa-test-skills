# LLM E2E 评测报告

- **时间**: 20260706_210842
- **模型**: kimi-for-coding
- **冒烟**: 是

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 1 |
| 断言（总） | 10 |
| 通过 | 0 |
| 失败 | 3 |
| 跳过（requires_e2e） | 7 |
| 错误 | 0 |
| 通过率 | 0.0% |
| Worker tokens | 2736 |
| 总耗时 | 7s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-1 | 0/10 | 7 | 7.4s | 2736 |

## 失败断言

- eval-1 **用例包含TC唯一ID**: not found: TC_
- eval-1 **用例关联了需求ID**: not found: REQ-
- eval-1 **覆盖至少5个步骤输出**: count=0, min=5

## 跳过断言（requires_e2e）

- eval-1 需求评审报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 需求解构表已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 场景树已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 边界清单已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 AI提示词已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 评审或补盲已执行: requires_e2e: 无法在纯 LLM 模式下验证 file_exists_or
- eval-1 测试报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
