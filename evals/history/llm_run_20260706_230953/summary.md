# LLM E2E 评测报告

- **时间**: 20260706_230953
- **Provider**: deepseek
- **模型**: deepseek-chat
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 10 |
| 断言（总） | 71 |
| 通过 | 53 |
| 失败 | 11 |
| 跳过（requires_e2e） | 7 |
| 错误 | 0 |
| 通过率 | 82.8% |
| Worker tokens | 61495 |
| 总耗时 | 320s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-1 | 1/10 | 7 | 1.8s | 2734 |
| eval-2 | 3/6 | 0 | 23.8s | 4906 |
| eval-3 | 6/9 | 0 | 33.7s | 6608 |
| eval-4 | 3/6 | 0 | 21.0s | 4535 |
| eval-5 | 8/8 | 0 | 65.6s | 10835 |
| eval-6 | 8/8 | 0 | 51.8s | 9191 |
| eval-7 | 8/8 | 0 | 18.6s | 4170 |
| eval-8 | 5/5 | 0 | 11.6s | 3776 |
| eval-9 | 6/6 | 0 | 25.3s | 4997 |
| eval-10 | 5/5 | 0 | 67.1s | 9743 |

## 失败断言

- eval-1 **用例包含TC唯一ID**: not found: TC_
- eval-1 **用例关联了需求ID**: not found: REQ-
- eval-2 **显性需求≥3条**: count=2, min=3
- eval-2 **隐性需求≥2条**: count=1, min=2
- eval-2 **衍生需求≥2条**: count=1, min=2
- eval-3 **用例编号符合TC规范**: not found: TC_
- eval-3 **包含预置条件**: not found: 预置条件
- eval-3 **用例总数≥5条**: count=0, min=5
- eval-4 **每个维度有评分**: not found: /10
- eval-4 **有改进建议**: not found: 改进
- eval-4 **使用规范标记格式**: any match: False in ['MISSING', 'WRONG', 'VAGUE']

## 跳过断言（requires_e2e）

- eval-1 需求评审报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 需求解构表已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 场景树已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 边界清单已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 AI提示词已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
- eval-1 评审或补盲已执行: requires_e2e: 无法在纯 LLM 模式下验证 file_exists_or
- eval-1 测试报告已生成: requires_e2e: 无法在纯 LLM 模式下验证 file_exists
