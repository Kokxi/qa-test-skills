#!/usr/bin/env python3
"""
根据 evals.json 中的结构化 assertions 评估测试输出。
用法：python scripts/grade_evals.py <workspace/iteration-N>
"""
import json, sys, re
from pathlib import Path

def check_assertion(assertion, output_text):
    """Check a single assertion against output text."""
    atype = assertion.get('type', '')
    name = assertion.get('name', '')
    
    if atype == 'file_exists':
        target = assertion.get('target', '')
        return {'text': name, 'passed': target in output_text, 'evidence': f'{"found" if target in output_text else "not found"}: {target}'}
    
    elif atype == 'file_exists_or':
        targets = assertion.get('targets', [])
        any_found = any(t in output_text for t in targets)
        found_list = [t for t in targets if t in output_text]
        return {'text': name, 'passed': any_found, 'evidence': f'found: {found_list} / all: {targets}'}
    
    elif atype == 'content_match':
        target = assertion.get('target', '')
        found = bool(re.search(target, output_text, re.IGNORECASE))
        return {'text': name, 'passed': found, 'evidence': f'{"found" if found else "not found"}: {target}'}
    
    elif atype == 'content_match_or':
        targets = assertion.get('targets', [])
        any_found = any(bool(re.search(t, output_text, re.IGNORECASE)) for t in targets)
        return {'text': name, 'passed': any_found, 'evidence': f'any match: {any_found} in {targets}'}
    
    elif atype == 'min_count':
        keyword = assertion.get('keyword', '')
        target = assertion.get('target', 0)
        count = len(re.findall(keyword, output_text, re.IGNORECASE)) if keyword else len(output_text.split())
        return {'text': name, 'passed': count >= target, 'evidence': f'count={count}, min={target}'}
    
    else:
        return {'text': name, 'passed': False, 'evidence': f'unknown type: {atype}'}

def grade_workspace(workspace_path):
    ws = Path(workspace_path)
    evals_file = Path(__file__).resolve().parent.parent / 'evals' / 'evals.json'
    with evals_file.open('r', encoding='utf-8') as f:
        evals_data = json.load(f)
    
    for idx, eval_item in enumerate(evals_data.get('evals', [])):
        eid = eval_item['id']
        assertions = eval_item.get('assertions', [])
        if not assertions:
            continue
        
        for variant in ['with_skill', 'without_skill']:
            output_dir = ws / f'eval-{idx}' / variant / 'outputs'
            grading_path = ws / f'eval-{idx}' / variant / 'grading.json'
            
            if not output_dir.exists():
                continue
            
            # Concatenate all output files
            all_text = ''
            for fpath in sorted(output_dir.iterdir()):
                if fpath.is_file():
                    try:
                        all_text += fpath.read_text(encoding='utf-8') + '\n'
                    except Exception:
                        all_text += fpath.name + '\n'
            
            # Grade each assertion
            results = [check_assertion(a, all_text) for a in assertions]
            passed = sum(1 for r in results if r['passed'])
            
            grading_path.parent.mkdir(parents=True, exist_ok=True)
            with grading_path.open('w', encoding='utf-8') as f:
                json.dump({
                    'eval_id': eid,
                    'variant': variant,
                    'total': len(results),
                    'passed': passed,
                    'failed': len(results) - passed,
                    'score': f'{passed}/{len(results)}',
                    'expectations': results
                }, f, ensure_ascii=False, indent=2)
            
            print(f'  eval-{eid}/{variant}: {passed}/{len(results)} passed')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/grade_evals.py <workspace/iteration-N>')
        sys.exit(1)
    grade_workspace(sys.argv[1])
