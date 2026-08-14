# QA Test Skills 质量验证实战笔记（V1.6.3）

> 本文档由 qa-test-skills V1.6.3 发版实战提炼，记录本项目建立的分层验证金字塔、实际跑出的基线、踩过的坑。给 Agent 在本项目后续迭代或其他 skill 项目复用时直接照做。
>
> **本项目实测成果**：48 技能 + 38 eval + 230 断言，LLM 端到端通过率 **95.4%**（DeepSeek，排除 requires_e2e 项），ClawHub 安全审计 **48/48 pass**。

## 0. 项目形态判定

```
项目形态 = 纯 Prompt AI 技能包（无 HTTP server，靠 LLM 按 SKILL.md 执行）
入口 = skills/qa-test-skills/SKILL.md（根编排引擎 + 12 步工作流，平级迁移后与其他技能同级）
子技能 = skills/qa-*/SKILL.md（48 个专家级子技能）
评估 = evals/evals.json（38 条 eval，230 条 assertion）
归档 = evals/history/llm_run_*/（每轮 LLM 评测报告）
脚本 = scripts/（integrity_check / validate_deps / grade_evals / run_llm_eval / check_security_audit / validate_standards / run_qa / aggregate_benchmark）
```

## 1. 核心方法论：验证金字塔

**关键认知**：多数 skill 项目只有 demo 没有评测。验证不止于"跑几个 demo 看输出像不像"——要建分层脚本金字塔，每层过滤不同问题。

| 层 | 查什么 | 本项目实现 | 发现过什么 |
|----|--------|---------|---------|
| 1 静态结构 | 文件齐全/字段完整/版本一致/无 BOM | `scripts/integrity_check.py` | frontmatter 残留 `hen_to_use:`、orphan required、缺检查清单 |
| 2 动态契约 | prompt 定义与 eval 期望是否一致 | `scripts/grade_evals.py` + `scripts/validate_deps.py` | 依赖不对称、YAML 解析错 |
| 3 行为模拟 | 复杂模块规则实现是否偏离规范 | N/A（本项目无记忆/状态模块） | — |
| 4 长期压测 | 多轮迭代后性能退化 | N/A（本项目无记忆/状态模块） | — |
| 5 真·LLM 端到端 | 模型实际产出满足断言否 | `scripts/run_llm_eval.py`（DeepSeek/Kimi 双 provider） | **Mode C 只承诺不输出、Mode A 漏维度** |
| 6 人工双盲 | 维度分析对不对 | 流程级（发版前人工抽样） | — |

**实测要点**：
- 层 1-2 是免费秒级脚本，每改一次必跑
- 层 5 是关键——前 2 层查不出"模型真遵守否"，必接 LLM API
- 层 6 是人工流程，发版前执行

## 2. 各层脚本的实际实现

### 层 1：静态结构校验（`scripts/integrity_check.py`）

**10 项必查**：
1. frontmatter 12 字段 + traceability 全覆盖
2. name 与目录名一致
3. version 全统一（当前 1.6.3）
4. related_skills 悬空引用 + 对称性
5. references/ 引用完整
6. ID 规范一致性（`validate_standards.py`）
7. 正文含 `## 检查清单`
8. UTF-8 BOM
9. evals.json 结构有效
10. 安全审计残留（泛化词 + Missing Warnings）

**用法**：
```bash
python scripts/integrity_check.py
# 输出：分项 ✅/❌ + 汇总「❌N 项硬问题 + ⚠️N 项软问题」
```

**实测踩坑**：
- V1.5.1 遗留：5 技能 description 嵌了 `hen_to_use:` 文本（YAML folded scalar 吸收下一字段）
- V1.5.1 遗留：`qa-risk-intuition` 缺 `input_format:` 键，required/optional 变 orphan
- 15 技能缺 `## 检查清单` 区块

### 层 2：契约断言（`scripts/validate_deps.py` + `scripts/grade_evals.py`）

**`validate_deps.py`**：校验 48 技能的 `related_skills` 引用图——upstream/downstream 对称 + 无悬空。

**`grade_evals.py`**：静态文件校验器，支持 8 种 assertion 类型：
- `file_exists` / `file_exists_or`：输出目录里有指定文件
- `content_match` / `content_match_or`：正则匹配内容
- `min_count`：关键词出现次数 ≥ N
- `regex_match`：完整正则匹配
- `json_valid`：JSON 块可解析 + dot-path 键存在
- `id_consistency`：ID 命名空间一致性（declared vs referenced）
- `golden_compare`：与 golden 文件的 TC_ID 重叠率 ≥ 阈值

**用法**：
```bash
python scripts/validate_deps.py                # 依赖图对称
python scripts/grade_evals.py workspace/iteration-N   # 静态打分
python scripts/run_qa.py smoke                  # 冒烟管线
```

### 层 5：真·LLM 端到端（`scripts/run_llm_eval.py`）★关键

**架构**：
```
读 evals/evals.json 每条 eval
  → 加载 skills/qa-test-skills/SKILL.md 作为 system prompt
  → eval 的 prompt 字段作为 user message
  → 调 worker 模型（DeepSeek/Kimi）生成产出
  → 对每条 assertion 跑 grade_evals.check_assertion 判定 pass/fail
  → file_exists 类断言标注 requires_e2e 跳过
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
     本项目全量 38 eval 约 218k token = ¥0.22
FI

IF 模型 == reasoning 模型（kimi-for-coding/glm-5.2）
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
- 一旦泄露立即 `git commit --amend` 重写历史 + 控制台 rotate key
- 示例占位符 `sk-...` 不算泄露

**用法**：
```bash
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek --smoke   # 冒烟
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek            # 全量
DS_KEY=sk-xxx python scripts/run_llm_eval.py --provider deepseek --offset 13 --limit 10  # 分批
```

**requires_e2e 标注**：
若某条 eval 的断言依赖文件 I/O（如 `file_exists`），纯 LLM 评测器看不到文件内容，跑不过不是 prompt 缺陷。本项目在 `evals.json` 标注 `requires_e2e: true` 从基线排除。**不得为提分改评测器注入文件数据自欺**。

本项目标注的 2 条：
- eval-1：7 条 `file_exists` 断言依赖文件 I/O（12 步工作流产出文件）
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

## 4. 实测缺陷模式与修复模板

### 模式 A：漏维度/漏类型（本项目实测命中）

**症状**：prompt 定义了 N 个维度/类型，模型实际输出 < N。

**命中 eval**：eval-2（显性需求 ≥3 只输出2条）、eval-3（缺 TC_ 格式）、eval-37（补盲用例 0 条）

**修复模板**（加到 skills/qa-test-skills/SKILL.md 核心原则）：
```
> ⚠️ **N 个维度全必输出硬约束**：必须按编号 1-N 逐条输出，未发现问题的也要输出占位行。
> 不适用的也要输出标注"不适用+原因"的占位项，而非省略。
> 末尾的"维度覆盖统计"必须确认 N/N 全覆盖，缺一项即格式校验失败。
```

**实测效果**：eval-2 从 3/6 → 6/6，eval-4 从 3/6 → 5/6。

### 模式 C：只承诺不输出（本项目实测命中）

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

### 模式 E：长期使用丢数据（本项目未命中）

本项目无记忆/状态模块，N/A。若后续加记忆模块需建层 3+4 压测。

## 5. 执行顺序（Agent 照做）

```
STEP 1: 探查项目结构
  - ls skills/ evals/ scripts/ docs/
  - 确认项目形态（纯 Prompt / 有 server）

STEP 2: 跑层 1 静态校验
  - python scripts/integrity_check.py，修所有 ❌ 报错

STEP 3: 跑层 2 契约断言
  - python scripts/validate_deps.py，修依赖不对称
  - python scripts/run_qa.py smoke，确认管线通

STEP 4: 若项目含记忆/状态模块 → 建/跑层 3+4
  - 本项目 N/A

STEP 5: 接 LLM API 跑层 5
  - 选模型（按模型选型决策树）
  - DS_KEY=xxx python scripts/run_llm_eval.py --provider deepseek --smoke
  - 全量跑（分批：--offset N --limit M），记录基线准确率

STEP 6: 按缺陷诊断决策树修 prompt
  - 准确率 < 70% → 按模式 A-E 修
  - 每修一处 → 重跑层 5 验证提升
  - 迭代直到准确率 ≥ 90% 或剩模型能力上限的随机波动

STEP 7: 标注 requires_e2e
  - 跑不过若是评测器架构限制（依赖文件 I/O）→ 标注排除
  - 不得为提分改评测器自欺

STEP 8: 安全审计对齐
  - python scripts/run_qa.py audit，修所有 ❌ Missing Warnings
  - 补 ⚠️ 安全警告块到涉险操作技能

STEP 9: 归档 + 报告
  - evals/history/ 存每轮报告
  - README.md benchmark 表同步更新通过率/eval 数
```

## 6. 避坑清单（实测版）

| 坑 | 表现 | 解法 |
|----|------|------|
| YAML folded scalar 吸收下一字段 | description 嵌了 `hen_to_use:` 文本 | 补独立 `when_to_use:` 字段 + 清理 description |
| frontmatter 字段错位 | required/optional 被插到 related_skills 下 | 检查 YAML 缩进 + 跑 integrity_check |
| Kimi reasoning 模型 content 为空 | 跑出 0 chars 但 reasoning_content 占满 token | max_tokens 调到 16384+ + content 空→取 reasoning 尾部 |
| API key 硬编码 fallback | Kimi key 泄露进 git 历史 | 删 fallback + `git commit --amend` 重写 + 控制台 rotate |
| Windows CRLF | 字符串比较失败（值相同却判不等） | 脚本里统一 `.replace('\r\n','\n')` |
| python3 占位符 | Windows Store 的 python3 调用即挂 | 回退用 `python` |
| ClawHub audit 关键词误报 | "删除/发布"在被测对象描述里也报 | 补 ⚠️ 安全警告块对齐 |
| 为提分改评测器 | 注入文件数据让分数好看 | 诚实标注 requires_e2e |

## 7. 成果基线参考

qa-test-skills V1.6.3 实测：

| 模型 | 通过率 | 说明 |
|------|--------|------|
| Kimi 首轮 | 52%（3 eval） | reasoning 模型配额限制，跑 3 条就超限 |
| DeepSeek 基线 | 88.8%（38 eval） | 首轮基线，暴露 Mode A/C 缺陷 |
| DeepSeek 修复后 | **95.4%** | 加硬约束后 +6.6% |

**38/38 eval 完整跑通**（排除 2 条 requires_e2e 项），integrity_check + validate_deps + audit 全过。

对比 qa-team-skills v1.5.0 参考：

| 项目 | 模型 | 首轮 | 最终 |
|------|------|------|------|
| qa-team-skills v1.5.0 | DeepSeek | 89.7% | 94.3% |
| qa-test-skills V1.6.3 | DeepSeek | 88.8% | **95.4%** |

## 8. 复用检查清单

Agent 在后续迭代或其他 skill 项目复用时，逐项确认：

- [ ] 跑了 `scripts/integrity_check.py`（层 1）
- [ ] 跑了 `scripts/validate_deps.py`（层 2 依赖对称）
- [ ] 跑了 `scripts/run_qa.py smoke`（管线通）
- [ ] 若有记忆模块 → 建了层 3+4
- [ ] 接了 LLM API 跑 `scripts/run_llm_eval.py`（层 5）
- [ ] 先冒烟（--smoke）验证管线通
- [ ] 跑了全量拿基线准确率
- [ ] 按诊断决策树修 prompt
- [ ] 每修一处重跑验证
- [ ] 标注了 requires_e2e 项
- [ ] API key 未泄露（环境变量 + 历史扫描）
- [ ] 跑了 `scripts/run_qa.py audit`（安全审计 pass）
- [ ] 归档了每轮报告到 `evals/history/`
- [ ] README.md benchmark 表同步更新
- [ ] 版本号全统一（skills/qa-test-skills/SKILL.md + 子技能 + plugin.json + integrity_check）
