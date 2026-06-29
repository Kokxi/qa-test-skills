# QA Test Skills — Scripts

本项目工具脚本目录。

| 脚本 | 用途 | 用法 |
|------|------|------|
| `validate_deps.py` | 验证所有 48 个子 Skill 的依赖引用完整性 | `python scripts/validate_deps.py` |
| `grade_evals.py` | 根据 evals.json 中的结构化 assertions 评估输出 | `python scripts/grade_evals.py <workspace/iteration-N>` |
| `aggregate_benchmark.py` | 聚合 grading 结果生成 benchmark.json | `python scripts/aggregate_benchmark.py <workspace/iteration-N> --skill-name <name>` |

## 依赖引用验证

```bash
python scripts/validate_deps.py
```

检查：
- `related_skills` 中引用的技能是否都存在
- `upstream/downstream` 引用的技能是否都存在
- 孤立技能（没有被任何其他技能引用的技能）
- 依赖不对称（A 声明 upstream=B，但 B 的 downstream 不含 A）

## Eval 分级

```bash
python scripts/grade_evals.py workspace/iteration-1
```

根据 `evals/evals.json` 中的结构化 assertions，逐条验证 with_skill 和 without_skill 的输出。输出 grading.json 到每个 eval 目录：

```
workspace/iteration-N/eval-0/with_skill/grading.json
workspace/iteration-N/eval-0/without_skill/grading.json
```

## Benchmark 聚合

```bash
python scripts/aggregate_benchmark.py workspace/iteration-1 --skill-name "qa-test-skills"
```

聚合所有 grading.json 生成 benchmark.json 和 benchmark.md，包含通过率、Token 用量和时间统计。

## 注意事项

- 所有路径使用 `pathlib.Path` 计算，兼容 Windows/Linux/macOS
- 工作台目录结构：`workspace/iteration-N/eval-ID/{with_skill,without_skill}/outputs/`
