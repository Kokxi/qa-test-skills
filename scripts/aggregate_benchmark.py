#!/usr/bin/env python3
"""
聚合 grading 结果生成 benchmark.json。
用法：python scripts/aggregate_benchmark.py <workspace/iteration-N> --skill-name <name>
"""
import json, sys, argparse
from pathlib import Path
from collections import defaultdict

def aggregate(workspace_path, skill_name):
    ws = Path(workspace_path)
    configs = ['with_skill', 'without_skill']
    per_config = defaultdict(list)
    per_eval = defaultdict(dict)
    
    # Collect all grading results
    for eid_dir in sorted(ws.iterdir()):
        if not eid_dir.is_dir() or not eid_dir.name.startswith('eval-'):
            continue
        eid = int(eid_dir.name.split('-')[1])
        
        for variant in configs:
            grading_file = eid_dir / variant / 'grading.json'
            if not grading_file.exists():
                continue
            with grading_file.open('r', encoding='utf-8') as f:
                grading = json.load(f)
            per_config[variant].append(grading)
            per_eval[eid][variant] = grading
    
    # Calculate per-config stats
    def calc_stats(items):
        if not items:
            return {'count': 0, 'pass_rate': 0, 'mean': 0, 'stddev': 0}
        rates = [i['passed'] / max(i['total'], 1) * 100 for i in items]
        mean = sum(rates) / len(rates)
        variance = sum((r - mean) ** 2 for r in rates) / len(rates) if len(rates) > 1 else 0
        return {
            'count': len(items),
            'pass_rate': round(mean, 1),
            'stddev': round(variance ** 0.5, 1),
            'total_passed': sum(i['passed'] for i in items),
            'total_failed': sum(i['failed'] for i in items),
        }
    
    stats = {}
    for cfg in configs:
        stats[cfg] = calc_stats(per_config[cfg])
    
    # Calculate delta
    if 'with_skill' in stats and 'without_skill' in stats:
        delta = round(stats['with_skill']['pass_rate'] - stats['without_skill']['pass_rate'], 1)
    else:
        delta = 0
    
    benchmark = {
        'skill_name': skill_name,
        'iteration': ws.name,
        'workspace': str(ws),
        'configurations': configs,
        'summary': {
            'with_skill': stats.get('with_skill', {}),
            'without_skill': stats.get('without_skill', {}),
            'delta_pass_rate': delta,
        },
        'per_eval': {str(k): v for k, v in sorted(per_eval.items())},
    }
    
    # Write benchmark.json
    bm_file = ws / 'benchmark.json'
    with bm_file.open('w', encoding='utf-8') as f:
        json.dump(benchmark, f, ensure_ascii=False, indent=2)
    print(f'Written: {bm_file}')
    
    # Write benchmark.md
    bm_md = ws / 'benchmark.md'
    lines = []
    lines.append(f'# Benchmark: {skill_name}')
    lines.append(f'- Iteration: {ws.name}')
    lines.append(f'- Configs: {", ".join(configs)}')
    lines.append('')
    lines.append('## Summary')
    lines.append('')
    lines.append('| Config | Pass Rate | StdDev | Passed | Failed |')
    lines.append('|--------|-----------|--------|--------|--------|')
    for cfg in configs:
        s = stats.get(cfg, {})
        lines.append(f'| {cfg} | {s.get("pass_rate", "N/A")}% | {s.get("stddev", "N/A")} | {s.get("total_passed", 0)} | {s.get("total_failed", 0)} |')
    lines.append(f'| **delta** | **{delta}%** | | | |')
    lines.append('')
    lines.append(f'With-skill pass rate: {stats.get("with_skill", {}).get("pass_rate", "N/A")}%')
    lines.append(f'Without-skill pass rate: {stats.get("without_skill", {}).get("pass_rate", "N/A")}%')
    lines.append(f'Delta: {delta}%')
    
    with bm_md.open('w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'Written: {bm_md}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace', type=str, help='Path to workspace/iteration-N')
    parser.add_argument('--skill-name', type=str, default='unknown', help='Skill name')
    args = parser.parse_args()
    aggregate(args.workspace, args.skill_name)
