# LLM E2E 评测报告

- **时间**: 20260706_235459
- **Provider**: deepseek
- **模型**: deepseek-chat
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 6 |
| 断言（总） | 41 |
| 通过 | 31 |
| 失败 | 10 |
| 跳过（requires_e2e） | 0 |
| 错误 | 0 |
| 通过率 | 75.6% |
| Worker tokens | 31045 |
| 总耗时 | 120s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-33 | 4/5 | 0 | 41.5s | 7831 |
| eval-34 | 4/5 | 0 | 22.0s | 5516 |
| eval-35 | 7/7 | 0 | 14.5s | 4351 |
| eval-36 | 10/10 | 0 | 16.2s | 4592 |
| eval-37 | 6/9 | 0 | 24.9s | 5902 |
| eval-38 | 0/5 | 0 | 1.4s | 2853 |

## 失败断言

- eval-33 **给出了输入质量评分**: any match: False in ['质量评分', 'quality_score', '评分']
- eval-34 **判定验证失败**: any match: False in ['fail', '不通过', '验证失败']
- eval-37 **总补盲数≥12**: count=0, min=12
- eval-37 **补盲用例带 BS- ID**: not found: BS-
- eval-37 **关联原始用例或需求**: any match: False in ['TC_', 'REQ-']
- eval-38 **golden 比对 ≥50%**: overlap=0% (≥50%), matched=0/12
- eval-38 **覆盖 AUTH 模块**: not found: TC_AUTH
- eval-38 **覆盖 ORDER 模块**: not found: TC_ORDER
- eval-38 **覆盖 PRODUCT 模块**: not found: TC_PRODUCT
- eval-38 **覆盖 USER 模块**: not found: TC_USER

## 跳过断言（requires_e2e）

（无跳过）
