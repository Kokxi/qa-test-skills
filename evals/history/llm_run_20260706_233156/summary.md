# LLM E2E 评测报告

- **时间**: 20260706_233156
- **Provider**: deepseek
- **模型**: deepseek-chat
- **冒烟**: 否

## 汇总

| 指标 | 值 |
|------|----|
| Evals | 6 |
| 断言（总） | 41 |
| 通过 | 30 |
| 失败 | 11 |
| 跳过（requires_e2e） | 0 |
| 错误 | 0 |
| 通过率 | 73.2% |
| Worker tokens | 28128 |
| 总耗时 | 107s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
| eval-33 | 3/5 | 0 | 36.2s | 6884 |
| eval-34 | 4/5 | 0 | 19.5s | 5206 |
| eval-35 | 7/7 | 0 | 16.5s | 4408 |
| eval-36 | 10/10 | 0 | 14.6s | 4221 |
| eval-37 | 6/9 | 0 | 19.0s | 4721 |
| eval-38 | 0/5 | 0 | 1.3s | 2688 |

## 失败断言

- eval-33 **判定输入不完整**: any match: False in ['fail', 'need_more_info', '不通过', '信息不足']
- eval-33 **输出了追问问题**: any match: False in ['追问', '澄清', 'clarification', '请问']
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
