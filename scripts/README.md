# QA Test Skills — Scripts

本项目工具脚本目录。

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check_spec_compliance.py` | **Agent Skills 规范门禁**（顶层字段白名单 / description≤1024 / 500 行 / 引用不出技能根 / 官方 `skills-ref validate`） | `python scripts/check_spec_compliance.py` |
| `integrity_check.py` | 内容与一致性检查（15 项）。`--json` 输出机器可读结果，供自测消费 | `python scripts/integrity_check.py [--json]` |
| `gate_selftest.py` | **门禁自测**：对 15 项检查逐项验证「该报的报、不该报的不报」 | `python scripts/gate_selftest.py [--check N] [-v] [--keep]` |
| `migrate_frontmatter.py` | frontmatter 规范迁移（历史脚本，重跑为幂等空操作） | `python scripts/migrate_frontmatter.py --check` |
| `validate_testcase_table.py` | 9 列标准用例表校验（列数/编号唯一性/P0-P3 占比/覆盖率口径） | `python scripts/validate_testcase_table.py <用例文件>` |
| `validate_deps.py` | 依赖引用图校验（upstream/downstream 对称 + 无悬空 + 无孤立） | `python scripts/validate_deps.py` |
| `validate_standards.py` | 全局标准一致性 | `python scripts/validate_standards.py` |
| `check_security_audit.py` | ClawHub security audit 本地预检 | `python scripts/check_security_audit.py [技能名]` |
| `stage_for_clawhub.py` | ClawHub 发布暂存：复制技能目录并剥掉 `metadata.slug`（SkillHub 独有字段） | `python scripts/stage_for_clawhub.py --all` |
| `grade_evals.py` | 按 evals.json 的结构化 assertions 评估输出 | `python scripts/grade_evals.py <workspace/iteration-N>` |
| `aggregate_benchmark.py` | 聚合 grading 结果生成 benchmark.json | `python scripts/aggregate_benchmark.py <workspace/iteration-N> --skill-name <name>` |
| `skillmeta.py` | 读取 SKILL.md 元数据的唯一入口（被上述脚本复用） | `python scripts/skillmeta.py qa-api-testing` |

## 规范合规

```bash
pip install skills-ref          # 官方参考实现
python scripts/check_spec_compliance.py
```

检查：
- frontmatter 顶层字段是否只含 `name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`
- `metadata` 是否为 string → string 映射
- `description` ≤ 1024 字符、`compatibility` ≤ 500 字符
- `name` 是否与目录名一致且符合命名规范
- `SKILL.md` 是否 ≤ 500 行（规范建议）
- 正文链接是否越出技能根目录或指向不存在的文件
- 官方 `skills-ref validate` 逐技能结果（未安装时自动跳过并提示）

> 历史教训：`integrity_check.py` 曾长期"0 硬问题"，但官方 validator 对 49 个技能全判失败。
> 根因是自定义 frontmatter 字段不在规范白名单内，且 `categories: ['a','b']` 属于
> flow-style 序列（官方 loader 判非法）。**两道门禁必须并存**：规范层零容忍，内容层可分期收敛。

## 门禁自测（改门禁必跑）

```bash
python scripts/run_qa.py selftest            # 或 python scripts/gate_selftest.py
python scripts/gate_selftest.py --check 14   # 只跑某一项
python scripts/gate_selftest.py -v           # 失败时打印 frontmatter 键位与 skillmeta 读到的原始值
python scripts/gate_selftest.py --keep       # 保留临时工作区供手工检查
```

**为什么需要它**：门禁的价值全在正则准不准。太松 → 缺陷漏过（46 个技能声明「固定 9 列
用例表」、其中 41 个根本不产用例表，就是这么活下来的）；太严 → 噪音淹没真问题（检查项 13
初版误报 29 条）。但只看「当前仓库是否通过」**无法区分这两种情况**——它同时也是
「检查本身坏了」的表现。

所以每项检查都要有两类用例：

| 方向 | 含义 | 数量 |
|------|------|------|
| `BASE` | 干净仓库硬问题必须为 0 | 1 |
| `INJECT` | 注入一个已知违规 → **必须报**（防漏） | 19 |
| `LEGAL` | 放一个形似但合规的内容 → **必须不报**（防误报） | 7 |

耗时约 95 秒（要跑 27 次完整检查），适合发布前 / CI，**不适合每次编辑都跑**。

**已经靠它抓出来的真缺陷**（都是门禁本身太严，不是内容问题）：

- 检查项 7 只认「检查/自检清单」，漏掉入口技能在用的 `## 验收清单` → 长期误报 1 项
- 检查项 14 只认 `（REQ-` 括号形式，漏掉仓库实际在用的 `：REQ-` 冒号形式
  → 写成 `关联需求ID：TC_XXX` 能绕过检测

**踩过的坑（写自测用例时）**：

- YAML 双引号标量里注入引号必须转义，否则 YAML 解析失败、症状变成「另一项检查报错」
- `list.insert()` / `dict.update()` 返回 `None`，用它当变换函数的返回值会把字段写成 `"null"`
- 改写 `metadata` 下的键必须**保留缩进**，否则变成顶层字段，被判成非规范字段
- `skillmeta.split_doc` 在 `yaml.safe_load` 失败时会**静默回退**到扁平正则，
  此时 `metadata` 变成 `{}`，所有键都读不到——看到这个症状先怀疑 YAML 解析

## 发布

| 渠道 | 脚本 | 说明 |
|------|------|------|
| SkillHub | `scripts/push-skillhub.bat [版本] [延迟]` | 49 个技能逐个推送，保留 `metadata.slug` |
| ClawHub | `scripts/push-clawhub.bat [版本] [延迟]` | 先经 `stage_for_clawhub.py` 剥离 `metadata.slug` 再推 |
| 两者 | `publish-all.bat [版本]` | 依次调上面两个 |

```bash
# 推之前先单独验证剥离结果，不碰任何源文件
python scripts/stage_for_clawhub.py --all --out .publish-staging/clawhub
grep -r "^\s*slug:" .publish-staging/clawhub --include=SKILL.md   # 应无输出
```

`metadata.slug` 是 SkillHub 独有的字段，代码里只维护一份（带 slug），
发 ClawHub 时在暂存副本上剥离——不维护双分支，避免两边内容漂移。
`.publish-staging/` 是构建产物，已在 `.gitignore` 里。

> 三个发布脚本的**默认版本**必须与入口技能 `metadata.version` 一致，
> 否则不带参数运行会把已发布版本覆盖成更低的版本号。
> `integrity_check.py` 检查项 12 会校验（包含注释里的版本号）。

## 依赖引用验证

```bash
python scripts/validate_deps.py
```

检查：
- `metadata.related-skills` 中引用的技能是否都存在
- `upstream/downstream` 引用的技能是否都存在（规范形态，JSON 字符串）
- 孤立技能（没有被任何其他技能引用的技能）
- 依赖不对称（A 声明 upstream=B，但 B 的 downstream 不含 A）
- 入口工作流 `all_skills` 是否收录全部子技能

## 用例表校验

```bash
python scripts/validate_testcase_table.py test-output/测试用例.md
python scripts/validate_testcase_table.py <文件> --no-quota   # 小规模集跳过 P0-P3 占比
python scripts/validate_testcase_table.py <文件> --json
```

校验 9 列齐全、用例编号唯一且符合 `TC_{模块}_{功能}_{序号}`、P0-P3 占比上限、
覆盖率口径措辞、绝对化措辞禁令。小规模用例集数学上无法满足 P0≤20% 等配额，
用 `--no-quota` 跳过并在报告中说明口径。

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
- 读取 SKILL.md 元数据统一走 `skillmeta.py`，不要在脚本里另写一套 frontmatter 正则
- **改 `integrity_check.py` 的检查逻辑后必须跑 `gate_selftest.py`**，并为改动的检查补上
  INJECT/LEGAL 用例——只验证「当前仓库仍然通过」证明不了检查是对的
- 工作台目录结构：`workspace/iteration-N/eval-ID/{with_skill,without_skill}/outputs/`
