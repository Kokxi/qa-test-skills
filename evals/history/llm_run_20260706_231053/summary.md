# LLM E2E 评测报告

- **时间**: 20260706_231053
- **Provider**: deepseek
- **模型**: deepseek-chat
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 3 |
| 断言（总） | 25 |
| 通过 | 10 |
| 失败 | 8 |
| 跳过（requires_e2e） | 7 |
| 错误 | 0 |
| 通过率 | 55.6% |
| Worker tokens | 17291 |
| 总耗时 | 74s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-1 | 1/10 | 7 | 1.3s | 2690 |
| eval-2 | 3/6 | 0 | 15.0s | 4132 |
| eval-3 | 6/9 | 0 | 57.9s | 10469 |

## 失败断言

- eval-1 **用例包含TC唯一ID**: not found: TC_
- eval-1 **用例关联了需求ID**: not found: REQ-
- eval-2 **显性需求≥3条**: count=1, min=3
- eval-2 **隐性需求≥2条**: count=1, min=2
- eval-2 **衍生需求≥2条**: count=1, min=2
- eval-3 **用例编号符合TC规范**: not found: TC_
- eval-3 **包含预置条件**: not found: 预置条件
- eval-3 **用例总数≥5条**: count=0, min=5

## 跳过断言（requires_e2e）

- eval-1 需求评审报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 需求解构表已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 场景树已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 边界清单已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 AI提示词已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 评审或补盲已执行: requires_e2e: 无法在纯 LLM 模式下验证 file_exists_or
- eval-1 测试报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
