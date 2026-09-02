# QA Test Skills 质量验证实战笔记（V1.7.7）

> 本文档由 qa-test-skills V1.7.7 发版实战提炼，记录本项目建立的分层验证金字塔、实际跑出的基线、踩过的坑。给 Agent 在本项目后续迭代或其他 skill 项目复用时直接照做。
>
> **本项目实测成果（V1.7.7 当前）**：49 技能（1 入口 + 48 子）+ 49 eval + 383 断言，18 轮 LLM E2E 已归档（`evals/history/`），ClawHub 安全审计本地预检 **49/49 pass**，静态层 `integrity_check` 0 硬问题。
> 历史基线：V1.6.3 的 38-eval 集全量实测 LLM 端到端通过率 **95.4%**（DeepSeek，排除 requires_e2e 项）。49-eval 集扩充后尚未跑全量对照基准，需按第 5 节 STEP 5 补跑。

## 0. 项目形态判定

```
项目形态 = 纯 Prompt AI 技能包（无 HTTP server，靠 LLM 按 SKILL.md 执行）
入口 = skills/qa-test-skills/SKILL.md（编排引擎 + 12 步工作流；V1.7.x 已从仓库根目录平级迁移到 skills/ 下）
子技能 = skills/qa-*/SKILL.md（48 个专家级子技能，含入口共 49 个 SKILL.md）
评估 = evals/evals.json（49 条 eval，383 条 assertion，2 条 requires_e2e）
归档 = evals/history/llm_run_*/（每轮 LLM 评测报告，目前 18 轮）
脚本 = scripts/（integrity_check / validate_deps / validate_standards / grade_evals /
       run_llm_eval / check_security_audit / aggregate_benchmark / gen_example_cases）
统一入口 = python scripts/run_qa.py {validate|grade|benchmark|smoke|audit|standards}
```

**版本号单一事实源**：入口 `skills/qa-test-skills/SKILL.md` 的 frontmatter `version` 字段（当前 1.7.7）。
所有配置/文档同步该值；任何脚本做版本一致性检查时**必须动态读入口值，禁止硬编码具体版本号**。
注意：`scripts/metadata.json` 里的 `self_update_manifest_url` 指向的是 SkillHub CLI 自更新清单（云端 version.json），
与本项目版本号无关，项目内不存放该文件。

## 1. 核心方法论：验证金字塔

**关键认知**：多数 skill 项目只有 demo 没有评测。验证不止于"跑几个 demo 看输出像不像"——要建分层脚本金字塔，每层过滤不同问题。

| 层 | 查什么 | 本项目实现 | 发现过什么 |
|----|--------|---------|---------|
| 1 静态结构 | 文件齐全/字段完整/版本一致/无 BOM | `scripts/integrity_check.py`（10 项） | frontmatter 残留 `hen_to_use:`、orphan required、入口迁移后 3 项 ❌ |
| 2 动态契约 | 依赖引用图/prompt 与 eval 期望一致 | `scripts/validate_deps.py` + `scripts/grade_evals.py` + `scripts/validate_standards.py` | 依赖不对称、YAML 解析错、⚠️标注与 enforcement.md 漂移 |
| 3 行为模拟 | 复杂模块规则实现是否偏离规范 | N/A（本项目无记忆/状态模块） | — |
| 4 长期压测 | 多轮迭代后性能退化 | N/A（本项目无记忆/状态模块） | — |
| 5 真·LLM 端到端 | 模型实际产出满足断言否 | `scripts/run_llm_eval.py`（DeepSeek/Kimi 双 provider） | **Mode C 只承诺不输出、Mode A 漏维度** |
| 6 人工双盲 | 维度分析对不对 | 流程级（发版前人工抽样，见 `docs/optimization-checklist.md`） | — |

**实测要点**：
- 层 1-2 是免费秒级脚本，每改一次必跑（`python scripts/run_qa.py validate && python scripts/run_qa.py standards`）
- 层 5 是关键——前 2 层查不出"模型真遵守否"，必接 LLM API
- 层 6 是人工流程，发版前执行

## 2. 各层脚本的实际实现

### 层 1：静态结构校验（`scripts/integrity_check.py`）

**10 项必查**：
1. frontmatter 12 字段 + traceability 全覆盖（入口编排器豁免 3 个叶子技能专属字段：`categories` / `depth_requirement_quantification` / `error_recovery_guidance`）
2. name 与目录名一致
3. version 全统一（动态以入口 `skills/qa-test-skills/SKILL.md` 的 version 为基准，当前 1.7.7）
4. related_skills 悬空引用 + upstream/downstream 对称性
5. references/ 引用完整（技能目录内 + 入口 references/ 兜底）
6. ID 规范一致性（与 `docs/standards.md` 前缀定义对照）
7. 正文含 `## 检查清单`（软问题，⚠️ 不计硬问题）
8. UTF-8 BOM（SKILL.md / scripts/*.py / evals/*.json 不得带 BOM）
9. evals.json 结构有效（id 唯一、prompt/expected_output/assertions 齐全）
10. 安全审计残留（when_to_use 裸泛化词 + 涉险技能 Missing Warnings）

**用法**：
```bash
python scripts/integrity_check.py
# 输出：分项 ✅/❌ + 汇总「❌N 项硬问题 + ⚠️N 项软问题」
```

**实测踩坑**：
- V1.5.1 遗留：5 技能 description 嵌了 `hen_to_use:` 文本（YAML folded scalar 吸收下一字段）
- V1.5.1 遗留：`qa-risk-intuition` 缺 `input_format:` 键，required/optional 变 orphan
- **V1.7.7 命中**：入口从根目录迁到 `skills/` 后，脚本的 `skills/qa-*` glob 把入口扫进了 12 字段检查，
  报 3 项 ❌（入口是编排器，无叶子技能专属字段）→ 按迁移前语义为入口豁免这 3 项，而非给入口补凑字段

### 层 2：契约断言（`scripts/validate_deps.py` + `scripts/validate_standards.py` + `scripts/grade_evals.py`）

**`validate_deps.py`**：校验 49 个技能的 `related_skills` 引用图——upstream/downstream 对称 + 无悬空 + 无孤立技能 + 入口 all_skills 收录完整。

**`validate_standards.py`**：入口工作流表的 ⚠️不得跳过 标注与 `references/enforcement.md` 的强制步骤一致；`docs/standards.md` 的 ID 前缀定义与子技能 traceability 声明一致。

**`grade_evals.py`**：断言引擎，支持 8 种 assertion 类型：
- `file_exists` / `file_exists_or`：输出文本里含指定文件名
- `content_match` / `content_match_or`：正则匹配内容
- `min_count`：模式出现次数 ≥ N。**兼容两种 schema**：A) `target`=阈值(int) + `keyword`=模式；B) `target`=模式(str) + `min`=阈值(int)（V1.7.7 修复，见模式 F）
- `regex_match`：完整正则匹配（默认 MULTILINE，可选 IGNORECASE）
- `json_valid`：JSON 块可解析 + dot-path 键存在
- `id_consistency`：ID 命名空间一致性（单前缀/跨前缀/同前缀行内引用 3 种模式）
- `golden_compare`：与 golden 文件的 TC_ID 重叠率 ≥ 阈值

**用法**：
```bash
python scripts/validate_deps.py                              # 依赖图对称
python scripts/validate_standards.py                         # ⚠️标注 + ID 规范
python scripts/grade_evals.py <workspace/iteration-N>        # 静态打分
python scripts/run_qa.py smoke                                # 冒烟管线
```

### 层 5：真·LLM 端到端（`scripts/run_llm_eval.py`）★关键

**架构**：
```
读 evals/evals.json 每条 eval
  → 加载 skills/qa-test-skills/SKILL.md 作为 system prompt（入口已迁移，SKILL_FILE 必须指向 skills/ 下）
  → eval 的 prompt 字段作为 user message
  → 调 worker 模型（DeepSeek/Kimi）生成产出
  → 对每条 assertion 跑 grade_evals.check_assertion 判定 pass/fail
  → requires_e2e: true 的 eval 整条跳过并计入 skipped
  → 归档到 evals/history/llm_run_YYYYMMDD_HHMMSS/
    （逐条 eval-{id}.json + summary.json + 人可读 summary.md）
```

**双 provider 配置**：
```
deepseek: api.deepseek.com/v1, model=deepseek-chat, temp=0.3, max_tokens=8192
kimi:     api.kimi.com/coding/v1, model=kimi-for-coding, temp=1.0, max_tokens=16384
```

**模型选型决策树**（实测版）：
```
IF 项目预算 == 0
  THEN 用免费模型做基线（能力上限低，长 system prompt 下产出可能为空）
ELSE 用 deepseek-chat（非 reasoning、产出完整、¥0.001/k token）
     V1.6.3 全量 38 eval 实测约 218k token = ¥0.22；49 eval 集按同比例外推约 280k token ≈ ¥0.3
FI

IF 模型 == reasoning 模型（kimi-for-coding 等）
  THEN max_tokens 需 ≥ 16384（reasoning_content 占大量 token）
       temperature = 1（reasoning 模型常限定）
       兜底：content 为空时回退用 reasoning 尾部最后 20 行
ELSE max_tokens = 8192, temperature = 0.3（评测要稳定）
FI
```

**API key 安全纪律**（本项目踩过坑）：
- 仅从环境变量读（`os.environ.get("DS_KEY")` / `os.environ.get("KIMI_API_KEY")`）
- 绝不写入脚本或归档报告
- 每次 commit 前 `git log --all -p | grep -iE "真key前缀"` 检查历史
- 一旦泄露立即重写历史 + 控制台 rotate key
- 示例占位符 `sk-...` 不算泄露

**用法**：
```bash
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek --smoke   # 冒烟
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek            # 全量 49 条
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek --offset 13 --limit 10  # 分批
```

**requires_e2e 标注**：
若某条 eval 的断言依赖文件 I/O（如 `file_exists`），纯 LLM 评测器看不到文件内容，跑不过不是 prompt 缺陷。本项目在 `evals.json` 标注 `requires_e2e: true` 从基线排除。**不得为提分改评测器注入文件数据自欺**。

本项目标注的 2 条：
- eval-1：`file_exists` 断言依赖文件 I/O（12 步工作流产出文件）
- eval-38：`golden_compare` 依赖外部 golden 文件比对

## 3. 缺陷诊断决策树（实测版）

当 LLM 评测准确率低，按此树诊断：

```
准确率低
├─ eval 全部 error（无产出）
│   ├─ HTTP 403/429 → API 配额/限流，换模型或等重置
│   ├─ content 为空 + finish=length → max_tokens 太小，调到 16384+
│   └→ content 为空 + finish=stop → 模型能力上限，换更强模型
│
├─ eval 部分通过，失败项分散
│   ├─ 失败原因"漏维度" → prompt 加硬约束：逐编号输出+末尾覆盖统计+缺项即校验失败
│   ├─ 失败原因"误判XX" → prompt 指令模糊，明确判定标准（含X即视为Y）
│   ├─ 失败原因"只承诺不输出" → prompt 加硬约束：必须直接输出内容，询问确认不得替代
│   └→ 失败原因"维度命名不对齐" → 改 eval assertion 描述，硬编码具体维度名
│
└─ eval 部分通过，失败项集中在某指令
    ├─ 该指令 prompt 定义有缺 → 修 prompt
    └→ 该指令 eval assertion 描述有误 → 修 eval
```

**V1.7.7 新增分支——脚本自身报错（管线故障，不是 prompt 问题）**：
```
run_qa / grade_evals 直接 traceback
├─ FileNotFoundError: SKILL.md → 入口已迁移到 skills/ 下，脚本硬编码的根路径失效
├─ TypeError: '>=' not supported (int vs str) → min_count 断言两种 schema 不兼容
└→ 先修脚本/数据，再谈 prompt 质量——管线断时任何通过率数字都无意义
```

## 4. 实测缺陷模式与修复模板

### 模式 A：漏维度/漏类型（V1.6.3 实测命中）

**症状**：prompt 定义了 N 个维度/类型，模型实际输出 < N。

**命中 eval**：eval-2（显性需求 ≥3 只输出2条）、eval-3（缺 TC_ 格式）、eval-37（补盲用例 0 条）

**修复模板**（加到 skills/qa-test-skills/SKILL.md 核心原则）：
```
> ⚠️ **N 个维度全必输出硬约束**：必须按编号 1-N 逐条输出，未发现问题的也要输出占位行。
> 不适用的也要输出标注"不适用+原因"的占位项，而非省略。
> 末尾的"维度覆盖统计"必须确认 N/N 全覆盖，缺一项即格式校验失败。
```

**实测效果**：eval-2 从 3/6 → 6/6，eval-4 从 3/6 → 5/6。

### 模式 C：只承诺不输出（V1.6.3 实测命中）

**症状**：模型回"我将生成报告"但没真生成表格。

**命中 eval**：eval-1（只输出 228 chars "I'll help you test..."）、eval-38（只输出 180 chars）

**修复模板**（加到 skills/qa-test-skills/SKILL.md 核心原则）：
```
> ⚠️ **必须直接输出完整内容，不得只承诺生成**：
> 必须在本次响应中直接输出完整内容，不得只输出"我将生成"等承诺性表述。
> 询问确认不得替代直接输出——用户请求即默示授权，询问只能在输出末尾的"是否补充"环节。
> 若数据不足，先输出已有数据的分析，再标注缺什么。
```

**实测效果**：修复后整体通过率从 88.8% → 95.4%。

### 模式 F：管线脚本与数据 schema 漂移（V1.7.7 实测命中）

**症状**：`run_qa.py smoke` / `grade_evals.py` 直接 `TypeError: '>=' not supported between instances of 'int' and 'str'`，
smoke 由 ✅ 变 ❌，且**任何 eval 都跑不到判定**。

**根因**：evals.json 的 `min_count` 断言存在两种 schema 并存——
- 旧式：`target` = 阈值(int) + `keyword` = 模式
- 新式：`target` = 模式(str) + `min` = 阈值(int)（112 条 min_count 断言中多数为新式）
`check_assertion` 只认旧式，遇到新式 `target="TC-"` 直接拿字符串比大小崩溃。

**修复模板**（断言引擎必须做 schema 自适应，禁止改数据迁就旧引擎）：
```python
if isinstance(target, str):
    keyword = keyword or target
    target = assertion.get('min', 1)
```

**实测效果**：smoke 恢复 ✅；`run_llm_eval.py` 复用同一 `check_assertion`，一并修复。

### 模式 G：结构迁移后配套资产断链（V1.7.7 实测命中）

**症状**：入口 SKILL.md 从仓库根平级迁移到 `skills/qa-test-skills/` 后，
`validate_deps.py` / `integrity_check.py` / `validate_standards.py` / `gen_example_cases.py` 全部 `FileNotFoundError`，
`plugin/index.js` 的 frontmatter 解析 49 个 description 全为空。

**根因**：迁移只动了"被消费的文件"，没动"消费它的所有代码路径"——脚本硬编码路径、
插件解析器不认 `>-` 折叠标量（叠加 CRLF 行尾使正则 `$` 锚点失效）。

**修复模板**：
```
1. 迁移文件后，全仓 grep 旧路径（含脚本/docstring/README/JSON 配置），逐条改
2. 版本/基准值类检查一律动态读入口 frontmatter，禁止硬编码版本号
3. 文本解析器必须：CRLF 归一化（.replace('\r\n','\n')）+ 支持 >- / | 块标量
4. 迁移后立即跑全量自检（run_qa validate/standards/audit/smoke + node 加载插件），
   全过才算迁移完成——"文件引用不悬空" ≠ "所有消费方都还活着"
```

**实测效果**：4 脚本恢复 + 插件 49/49 description 解析正常 + integrity 0 硬问题。

### 模式 E：长期使用丢数据（本项目未命中）

本项目无记忆/状态模块，N/A。若后续加记忆模块需建层 3+4 压测。

## 5. 执行顺序（Agent 照做）

```
STEP 1: 探查项目结构
  - ls skills/ evals/ scripts/ docs/
  - 确认项目形态（纯 Prompt / 有 server）
  - 确认版本号单一事实源（入口 skills/qa-test-skills/SKILL.md frontmatter）

STEP 2: 跑层 1 静态校验
  - python scripts/integrity_check.py，修所有 ❌ 报错

STEP 3: 跑层 2 契约断言
  - python scripts/run_qa.py validate，修依赖不对称
  - python scripts/run_qa.py standards，修 ⚠️标注/ID 规范漂移
  - python scripts/run_qa.py smoke，确认 grade 管线通

STEP 4: 若项目含记忆/状态模块 → 建/跑层 3+4
  - 本项目 N/A

STEP 5: 接 LLM API 跑层 5
  - 选模型（按模型选型决策树）
  - DS_KEY=xxx python scripts/run_llm_eval.py --provider deepseek --smoke
  - 全量跑（分批：--offset N --limit M），记录基线准确率
  - 注意：eval 集扩容后（如 38 → 49）旧全量数字不能沿用，必须重跑新基线并标注口径

STEP 6: 按缺陷诊断决策树修 prompt / 修脚本
  - 准确率 < 70% → 按模式 A-G 修
  - 每修一处 → 重跑层 5 验证提升
  - 迭代直到准确率 ≥ 90% 或剩模型能力上限的随机波动

STEP 7: 标注 requires_e2e
  - 跑不过若是评测器架构限制（依赖文件 I/O）→ 标注排除
  - 不得为提分改评测器自欺

STEP 8: 安全审计对齐
  - python scripts/run_qa.py audit，修所有 ❌ Missing Warnings
  - 补 ⚠️ 安全警告块到涉险操作技能

STEP 9: 归档 + 报告 + 版本同步
  - evals/history/ 存每轮报告
  - README.md benchmark 表同步更新通过率/eval 数（数字必须可回溯到某轮实测，标注口径）
  - 版本号全统一：入口 SKILL.md + 48 子技能 + plugin/package.json +
    .claude-plugin/*.json + .agents/plugins/marketplace.json + README 徽章 + push 脚本默认值
```

## 6. 避坑清单（实测版）

| 坑 | 表现 | 解法 |
|----|------|------|
| YAML folded scalar 吸收下一字段 | description 嵌了 `hen_to_use:` 文本 | 补独立 `when_to_use:` 字段 + 清理 description |
| frontmatter 字段错位 | required/optional 被插到 related_skills 下 | 检查 YAML 缩进 + 跑 integrity_check |
| 手写 frontmatter 解析器不认块标量 | 插件加载后 49 个 description 全为空 | 支持 `>-`/`|` 块标量：收集缩进行折叠为单行；或直接用 YAML 库 |
| 解析器遇 CRLF 文件正则失配 | `$` 锚点前残留 `\r`，`match` 全部落空 | 解析前统一 `.replace('\r\n','\n')` |
| 文件迁移后只改"被引用"不查"消费者" | 迁移入口后 4 个自检脚本全 FileNotFoundError | 迁移后全仓 grep 旧路径 + 全量跑自检 + node 加载插件 |
| 质量脚本硬编码版本号 | 版本升级后脚本误报 N 项 ❌ | 动态读入口 frontmatter version 作基准 |
| 断言引擎与数据 schema 漂移 | smoke TypeError：int 与 str 比较 | 引擎做 schema 自适应（`isinstance(target, str)` 分支） |
| Kimi reasoning 模型 content 为空 | 跑出 0 chars 但 reasoning_content 占满 token | max_tokens 调到 16384+ + content 空→取 reasoning 尾部 |
| API key 硬编码 fallback | Kimi key 泄露进 git 历史 | 删 fallback + 重写历史 + 控制台 rotate |
| Windows CRLF | 字符串比较失败（值相同却判不等） | 脚本里统一 `.replace('\r\n','\n')` |
| python3 占位符 | Windows Store 的 python3 调用即挂 | 回退用 `python` |
| ClawHub audit 关键词误报 | "删除/发布"在被测对象描述里也报 | 补 ⚠️ 安全警告块对齐 |
| 为提分改评测器 | 注入文件数据让分数好看 | 诚实标注 requires_e2e |
| README 数字漂移 | eval 集扩容后 README 还写旧数字（38/230/8轮） | 发布前对照 evals.json 实际计数 + history 轮数，数字必须标注口径与版本 |

## 7. 成果基线参考

### V1.7.7 当前状态（2026-09-02 自检实测）

| 项 | 数据 | 来源 |
|----|------|------|
| 技能数 | 49（1 入口 + 48 子），name/version/字段 100% 一致 | `integrity_check.py` |
| Eval 集 | 49 条 eval / 383 断言，2 条 requires_e2e（eval-1、eval-38） | `evals/evals.json` |
| 专项覆盖 | 17 条 eval 显式指定被测 skill，覆盖 11 个子技能（6 条 golden 对比） | `evals/evals.json` `skill` 字段 |
| 静态自检 | integrity 0 硬问题、deps 0 错误 0 警告、standards 全过、audit 49/49 pass | `run_qa.py` 全子命令 |
| LLM E2E 归档 | 18 轮（`evals/history/llm_run_*`，均为分批/冒烟/全量混合轮次） | 目录实测 |
| 待办 | 49-eval 集全量 with/without 对照基准未跑（需 API key，见 STEP 5） | — |

### 历史基线（V1.6.3 全量 38-eval 实测，引用时须带口径）

| 模型 | 通过率 | 说明 |
|------|--------|------|
| Kimi 首轮 | 52%（3 eval） | reasoning 模型配额限制，跑 3 条就超限 |
| DeepSeek 基线 | 88.8%（38 eval） | 首轮基线，暴露 Mode A/C 缺陷 |
| DeepSeek 修复后 | **95.4%**（without 62.4%，Δ +33.0%） | 加硬约束后 +6.6%；48/48 审计 pass |

**38/38 eval 完整跑通**（排除 2 条 requires_e2e 项），integrity_check + validate_deps + audit 全过。
⚠️ 该组数字是 **V1.6.3 版本 38-eval 集**的实测值；eval 集扩容到 49 后未重跑全量对照，
引用时必须标注"V1.6.3 全量口径"，不得当作当前 49-eval 集的通过率。

对比 qa-team-skills v1.5.0 参考：

| 项目 | 模型 | 首轮 | 最终 |
|------|------|------|------|
| qa-team-skills v1.5.0 | DeepSeek | 89.7% | 94.3% |
| qa-test-skills V1.6.3 | DeepSeek | 88.8% | **95.4%**（38-eval 口径） |

## 8. 复用检查清单

Agent 在后续迭代或其他 skill 项目复用时，逐项确认：

- [ ] 跑了 `scripts/integrity_check.py`（层 1，0 硬问题）
- [ ] 跑了 `scripts/run_qa.py validate`（层 2 依赖对称）
- [ ] 跑了 `scripts/run_qa.py standards`（⚠️标注 + ID 规范）
- [ ] 跑了 `scripts/run_qa.py smoke`（grade 管线通）
- [ ] 若有记忆模块 → 建了层 3+4
- [ ] 接了 LLM API 跑 `scripts/run_llm_eval.py`（层 5）
- [ ] 先冒烟（--smoke）验证管线通
- [ ] 跑了全量拿基线准确率（eval 集变更后必须重跑，不得沿用旧数字）
- [ ] 按诊断决策树修 prompt / 修脚本
- [ ] 每修一处重跑验证
- [ ] 标注了 requires_e2e 项
- [ ] API key 未泄露（环境变量 + 历史扫描）
- [ ] 跑了 `scripts/run_qa.py audit`（安全审计 pass）
- [ ] 归档了每轮报告到 `evals/history/`
- [ ] README.md benchmark 表同步更新（数字可回溯到某轮实测 + 标注口径与版本）
- [ ] 版本号全统一（入口 SKILL.md + 子技能 + plugin.json + 两个 marketplace.json + README 徽章 + push 脚本默认值；检查脚本动态读入口版本，不硬编码）
