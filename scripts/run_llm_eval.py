#!/usr/bin/env python3
"""
LLM 端到端评测（Layer 5）。
用 worker 模型生成产出，再用 grade_evals.py 的 check_assertion 做断言判定。

用法：
  python scripts/run_llm_eval.py                                    # 全量 38 条 eval（默认 deepseek）
  python scripts/run_llm_eval.py --smoke                            # 冒烟（只跑第 1 条）
  python scripts/run_llm_eval.py --provider deepseek                # 用 DeepSeek
  python scripts/run_llm_eval.py --provider kimi                    # 用 Kimi
  python scripts/run_llm_eval.py --limit 5 --offset 0               # 第 1-5 条

支持 provider：
  - deepseek:  model=deepseek-chat, temp=0.3, max_tokens=8192
  - kimi:      model=kimi-for-coding, temp=1.0, max_tokens=16384 (reasoning)

环境变量：
  DS_KEY          DeepSeek API key
  KIMI_API_KEY    Kimi API key
"""
import json, sys, os, time, re
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent.parent
EVALS_FILE = ROOT / 'evals' / 'evals.json'
HISTORY_DIR = ROOT / 'evals' / 'history'
SKILL_FILE = ROOT / 'SKILL.md'

# Provider 配置
PROVIDERS = {
    'deepseek': {
        'api_base': 'https://api.deepseek.com/v1',
        'api_key_env': 'DS_KEY',
        'model': 'deepseek-chat',
        'max_tokens': 8192,
        'temperature': 0.3,
    },
    'kimi': {
        'api_base': 'https://api.kimi.com/coding/v1',
        'api_key_env': 'KIMI_API_KEY',
        'model': 'kimi-for-coding',
        'max_tokens': 16384,
        'temperature': 1.0,   # reasoning 模型必须为 1
    },
}

DEFAULT_PROVIDER = 'deepseek'

# ── 导入 grade_evals 的 check_assertion ──────────────────────────────────
sys.path.insert(0, str(ROOT / 'scripts'))
from grade_evals import check_assertion


def call_llm(system_prompt, user_message, api_base, api_key, model, max_tokens, temperature, max_retries=3):
    """调用 LLM API（OpenAI 兼容），返回 (content, reasoning, usage)"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ],
        'max_tokens': max_tokens,
        'temperature': temperature,
    }).encode('utf-8')

    last_error = None
    for attempt in range(1, max_retries + 1):
        req = Request(f'{api_base}/chat/completions', data=payload, headers=headers)
        try:
            resp = urlopen(req, timeout=180)
            data = json.loads(resp.read().decode('utf-8'))
            content = data['choices'][0]['message'].get('content', '') or ''
            reasoning = data['choices'][0]['message'].get('reasoning_content', '') or ''
            # 兜底：content 为空时回退用 reasoning 尾部
            if not content.strip() and reasoning.strip():
                lines = reasoning.strip().split('\n')
                content = '\n'.join(lines[-20:])
            usage = data.get('usage', {})
            return content, reasoning, usage
        except HTTPError as e:
            code = e.code
            body = e.read().decode('utf-8', errors='replace')[:300]
            if code == 403 and 'usage limit' in body:
                last_error = f'API quota exhausted: {body}'
                if attempt < max_retries:
                    wait = 15 * attempt
                    print(f'\n  ⏳ quota limit, retry in {wait}s ({attempt}/{max_retries})...', end=' ', flush=True)
                    time.sleep(wait)
                    continue
            elif code == 429:
                last_error = f'API rate limited: {body}'
                if attempt < max_retries:
                    wait = 10 * (2 ** attempt)
                    print(f'\n  ⏳ rate limited, retry in {wait}s ({attempt}/{max_retries})...', end=' ', flush=True)
                    time.sleep(wait)
                    continue
            raise RuntimeError(f'API error {code}: {body}')
    raise RuntimeError(last_error or 'max retries exceeded')


def run_single_eval(eval_item, system_prompt, provider_cfg, smoke=False):
    """跑单条 eval，返回结果 dict"""
    eid = eval_item['id']
    user_prompt = eval_item['prompt']
    assertions = eval_item.get('assertions', [])

    print(f'  eval-{eid}: calling worker model...', end=' ', flush=True)

    # 调用 worker 模型生成产出
    t0 = time.time()
    try:
        output, reasoning, usage = call_llm(
            system_prompt, user_prompt,
            api_base=provider_cfg['api_base'],
            api_key=provider_cfg['api_key'],
            model=provider_cfg['model'],
            max_tokens=provider_cfg['max_tokens'],
            temperature=provider_cfg['temperature'],
        )
        elapsed = time.time() - t0
    except Exception as e:
        print(f'❌ {e}')
        return {
            'eval_id': eid,
            'error': str(e),
            'total': len(assertions),
            'passed': 0,
            'failed': len(assertions),
            'skipped': 0,
            'e2e_skipped': 0,
            'expectations': [
                {'text': a['name'], 'passed': False, 'evidence': f'worker error: {e}'}
                for a in assertions
            ],
            'worker_tokens': 0,
            'elapsed_sec': time.time() - t0,
        }

    # 截断输出（冒烟模式只用前 2000 字符）
    if smoke and len(output) > 2000:
        output = output[:2000] + '\n... [truncated for smoke]'

    print(f'✅ {len(output)} chars, {usage.get("total_tokens",0)} tokens, {elapsed:.1f}s')

    # 对每条 assertion 做判定
    results = []
    e2e_skipped = 0
    for a in assertions:
        atype = a.get('type', '')
        # file_exists 类断言纯 LLM 跑不了 → 标注 requires_e2e 跳过
        if atype in ('file_exists', 'file_exists_or'):
            results.append({
                'text': a['name'],
                'passed': None,
                'evidence': f'requires_e2e: 无法在纯 LLM 模式下验证 {atype}',
                'requires_e2e': True,
            })
            e2e_skipped += 1
        else:
            r = check_assertion(a, output)
            results.append(r)

    passed = sum(1 for r in results if r.get('passed') is True)
    failed = sum(1 for r in results if r.get('passed') is False)
    skipped = sum(1 for r in results if r.get('passed') is None)

    return {
        'eval_id': eid,
        'prompt_preview': user_prompt[:100],
        'output_preview': output[:200],
        'worker_tokens': usage.get('total_tokens', 0),
        'worker_tokens_cached': usage.get('cached_tokens', 0),
        'elapsed_sec': round(elapsed, 1),
        'total': len(results),
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'e2e_skipped': e2e_skipped,
        'expectations': results,
    }


def main():
    # 解析参数
    args = sys.argv[1:]
    smoke = '--smoke' in args
    provider_name = DEFAULT_PROVIDER
    custom_model = None
    limit = None
    offset = 0
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--model' and i + 1 < len(args):
            custom_model = args[i + 1]; i += 1
        elif a == '--provider' and i + 1 < len(args):
            provider_name = args[i + 1]; i += 1
        elif a == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1]); i += 1
        elif a == '--offset' and i + 1 < len(args):
            offset = int(args[i + 1]); i += 1
        i += 1

    # 解析 provider 配置
    if provider_name not in PROVIDERS:
        print(f'❌ 未知 provider: {provider_name}，可选: {list(PROVIDERS.keys())}')
        sys.exit(1)
    pcfg = dict(PROVIDERS[provider_name])
    pcfg['api_key'] = os.environ.get(pcfg['api_key_env']) or pcfg.get('api_key_fallback', '')
    if not pcfg['api_key']:
        print(f'❌ 缺少 API key: 请设置环境变量 {pcfg["api_key_env"]}')
        sys.exit(1)
    if custom_model:
        pcfg['model'] = custom_model

    # 加载 evals.json
    with open(EVALS_FILE, encoding='utf-8') as f:
        evals_data = json.load(f)

    all_evals = evals_data['evals']
    if smoke:
        all_evals = [all_evals[0]]
        print(f'🔬 SMOKE mode: 1 eval\n')
    else:
        if offset > 0:
            all_evals = all_evals[offset:]
        if limit is not None:
            all_evals = all_evals[:limit]
        print(f'📊 Evals: {len(all_evals)} (offset={offset}, limit={limit or "all"})\n')

    # 加载系统 prompt（根 SKILL.md）
    system_prompt = SKILL_FILE.read_text(encoding='utf-8')
    print(f'📄 Provider: {provider_name}')
    print(f'🤖 Model: {pcfg["model"]} (max_tokens={pcfg["max_tokens"]}, temp={pcfg["temperature"]})')
    print(f'📄 System prompt: {SKILL_FILE.name} ({len(system_prompt)} chars)')
    print()

    # 逐条执行
    all_results = []
    total_worker_tokens = 0
    total_elapsed = 0.0
    for e in all_evals:
        r = run_single_eval(e, system_prompt, pcfg, smoke=smoke)
        all_results.append(r)
        total_worker_tokens += r.get('worker_tokens', 0)
        total_elapsed += r.get('elapsed_sec', 0)

        if smoke:
            break  # 冒烟只跑一条

    # 汇总
    total_assertions = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_skipped = sum(r['skipped'] for r in all_results)
    total_errors = sum(1 for r in all_results if 'error' in r)
    total_e2e = sum(r['e2e_skipped'] for r in all_results)

    pass_rate = total_passed / (total_assertions - total_skipped) * 100 if (total_assertions - total_skipped) > 0 else 0

    print(f'\n{"="*50}')
    print(f'📊 汇总')
    print(f'{"="*50}')
    print(f'  Evals:     {len(all_results)}')
    print(f'  断言:      {total_assertions} 总 / {total_passed} ✅ / {total_failed} ❌ / {total_skipped} ⏭️  skipped')
    print(f'  需 e2e:    {total_e2e}（file_exists 类，LLM 模式下跳过）')
    print(f'  错误:      {total_errors}')
    print(f'  通过率:    {pass_rate:.1f}%（排除 skipped）')
    print(f'  总 token:  {total_worker_tokens}')
    print(f'  总耗时:    {total_elapsed:.0f}s')

    # 归档
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = HISTORY_DIR / f'llm_run_{timestamp}'
    run_dir.mkdir(parents=True, exist_ok=True)

    # 逐条存档
    for r in all_results:
        eid = r['eval_id']
        (run_dir / f'eval-{eid}.json').write_text(
            json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')

    # 汇总
    summary = {
        'timestamp': timestamp,
        'provider': provider_name,
        'model': pcfg['model'],
        'smoke': smoke,
        'total_evals': len(all_results),
        'total_assertions': total_assertions,
        'passed': total_passed,
        'failed': total_failed,
        'skipped': total_skipped,
        'e2e_skipped': total_e2e,
        'errors': total_errors,
        'pass_rate_pct': round(pass_rate, 1),
        'total_worker_tokens': total_worker_tokens,
        'total_elapsed_sec': round(total_elapsed, 1),
    }
    (run_dir / 'summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    # 人可读总结
    md = f"""# LLM E2E 评测报告

- **时间**: {timestamp}
- **Provider**: {provider_name}
- **模型**: {pcfg['model']}
- **冒烟**: {'是' if smoke else '否'}

## 汇总

| 指标 | 值 |
|------|----|
| Evals | {len(all_results)} |
| 断言（总） | {total_assertions} |
| 通过 | {total_passed} |
| 失败 | {total_failed} |
| 跳过（requires_e2e） | {total_skipped} |
| 错误 | {total_errors} |
| 通过率 | {pass_rate:.1f}% |
| Worker tokens | {total_worker_tokens} |
| 总耗时 | {total_elapsed:.0f}s |

## 逐条明细

| Eval | 通过/总 | 跳过 | 耗时 | Worker tokens |
|------|---------|------|------|--------------|
"""
    for r in all_results:
        md += f"| eval-{r['eval_id']} | {r['passed']}/{r['total']} | {r.get('skipped',0)} | {r.get('elapsed_sec',0)}s | {r.get('worker_tokens',0)} |\n"

    md += '\n## 失败断言\n\n'
    for r in all_results:
        eid = r['eval_id']
        for exp in r.get('expectations', []):
            if exp.get('passed') is False:
                md += f"- eval-{eid} **{exp['text']}**: {exp.get('evidence', '')}\n"
    if not any(exp.get('passed') is False for r in all_results for exp in r.get('expectations', [])):
        md += '（无失败断言）\n'

    md += '\n## 跳过断言（requires_e2e）\n\n'
    for r in all_results:
        eid = r['eval_id']
        for exp in r.get('expectations', []):
            if exp.get('passed') is None:
                md += f"- eval-{eid} {exp['text']}: {exp.get('evidence', '')}\n"
    if not any(exp.get('passed') is None for r in all_results for exp in r.get('expectations', [])):
        md += '（无跳过）\n'

    (run_dir / 'summary.md').write_text(md, encoding='utf-8')

    print(f'\n📁 报告归档: {run_dir}')
    print(f'   summary.json / summary.md / eval-*.json')
    print(f'   人可读: {run_dir / "summary.md"}')
    print(f'✅ 完成')


if __name__ == '__main__':
    main()
