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

    elif atype == 'regex_match':
        # Full regex match (no auto-ignorecase); use re.MULTILINE for ^..$ per-line matching
        pattern = assertion.get('pattern', assertion.get('target', ''))
        flags = re.MULTILINE
        if assertion.get('ignore_case', False):
            flags |= re.IGNORECASE
        found = bool(re.search(pattern, output_text, flags))
        return {'text': name, 'passed': found, 'evidence': f'{"match" if found else "no match"}: /{pattern}/'}

    elif atype == 'json_valid':
        # Verify output contains a JSON block (```json ...``` or bare {..}) that parses
        # target (optional): dot-path key that must exist, e.g. "test_cases.0.id"
        target = assertion.get('target', '')
        # Try to extract a JSON block
        m = re.search(r'```json\s*(.*?)```', output_text, re.S) or re.search(r'(\{.*\})', output_text, re.S)
        if not m:
            return {'text': name, 'passed': False, 'evidence': 'no JSON block found'}
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            return {'text': name, 'passed': False, 'evidence': f'invalid JSON: {e}'}
        if not target:
            return {'text': name, 'passed': True, 'evidence': 'valid JSON parsed'}
        # Walk dot-path
        cur = obj
        ok = True
        for part in target.split('.'):
            if isinstance(cur, list) and part.isdigit():
                idx = int(part)
                ok = 0 <= idx < len(cur)
                cur = cur[idx] if ok else None
            elif isinstance(cur, dict):
                ok = part in cur
                cur = cur.get(part) if ok else None
            else:
                ok = False
                break
        return {'text': name, 'passed': ok, 'evidence': f'target={target}, {"present" if ok else "absent"}'}

    elif atype == 'id_consistency':
        # Verify that IDs referenced in a "reference block" all appear in a "declared block".
        # Two modes:
        #   (A) single-prefix: source_prefix only → check ≥1 declared and no duplicates
        #   (B) cross-prefix: source_prefix (declared namespace) + ref_prefix (referencing namespace),
        #       referenced ⊆ declared. Different prefixes distinguish the two namespaces.
        #   (C) same-prefix cross-ref: source_prefix == ref_prefix → split text into declared region
        #       (lines starting with the prefix) vs referenced region (prefix appearing after another
        #       token on the same line, e.g. "TC_001 REQ-AUTH-001" → REQ-AUTH-001 is a reference).
        #       Use 'declared_anchor' (regex) to identify declared lines; default: line starts with prefix.
        source_prefix = assertion.get('source_prefix', assertion.get('target', ''))
        ref_prefix = assertion.get('ref_prefix', '')
        if not source_prefix:
            return {'text': name, 'passed': False, 'evidence': 'source_prefix missing'}
        id_pat = re.escape(source_prefix) + r'[\w-]+'
        if not ref_prefix or ref_prefix == source_prefix:
            if ref_prefix == source_prefix:
                # Mode C: same-prefix cross-ref. Declared = prefix at line start; referenced = prefix elsewhere.
                declared = set()
                referenced = set()
                for line in output_text.split('\n'):
                    ids_in_line = re.findall(id_pat, line)
                    if not ids_in_line:
                        continue
                    # IDs at line start (after optional whitespace) are declarations
                    stripped = line.lstrip()
                    if stripped.startswith(source_prefix):
                        declared.add(ids_in_line[0])
                        referenced.update(ids_in_line[1:])
                    else:
                        referenced.update(ids_in_line)
                missing = referenced - declared
                ok = not missing and len(declared) >= 1
                return {'text': name, 'passed': ok,
                        'evidence': f'declared={len(declared)} referenced={len(referenced)} missing={len(missing)}'}
            # Mode A: single-prefix, just check ≥1 declared
            declared = set(re.findall(id_pat, output_text))
            return {'text': name, 'passed': len(declared) >= 1,
                    'evidence': f'declared {len(declared)} {source_prefix} IDs'}
        # Mode B: cross-prefix — referenced IDs are source_prefix IDs appearing on lines
        # that DON'T start with source_prefix (i.e. they're being referenced, not declared).
        # Example: declared block "REQ-001\nREQ-002", reference line "TC-001 REQ-001" →
        # referenced = {REQ-001}; missing = {} → pass.
        declared = set()
        referenced = set()
        for line in output_text.split('\n'):
            ids_in_line = re.findall(id_pat, line)
            if not ids_in_line:
                continue
            stripped = line.lstrip()
            if stripped.startswith(source_prefix):
                declared.update(ids_in_line)
            else:
                # On non-declaration lines, any source_prefix ID is a reference
                referenced.update(ids_in_line)
        missing = referenced - declared
        ok = not missing and len(declared) >= 1
        return {'text': name, 'passed': ok,
                'evidence': f'declared={len(declared)} referenced={len(referenced)} missing={len(missing)}'}

    elif atype == 'golden_compare':
        # Compare TC_IDs in output against a golden file (examples/.../test-cases.md).
        # target: relative path to golden file. min_overlap: required overlap ratio (0-1).
        golden_path = assertion.get('target', '')
        min_overlap = assertion.get('min_overlap', 0.5)
        if not golden_path:
            return {'text': name, 'passed': False, 'evidence': 'target (golden path) missing'}
        gp = Path(__file__).resolve().parent.parent / golden_path
        if not gp.exists():
            return {'text': name, 'passed': False, 'evidence': f'golden file not found: {gp}'}
        golden_ids = set(re.findall(r'TC_[A-Z_]+_\d+', gp.read_text(encoding='utf-8')))
        output_ids = set(re.findall(r'TC_[A-Z_]+_\d+', output_text))
        if not golden_ids:
            return {'text': name, 'passed': False, 'evidence': 'no TC_IDs in golden file'}
        overlap = len(golden_ids & output_ids) / len(golden_ids)
        passed = overlap >= min_overlap
        return {'text': name, 'passed': passed,
                'evidence': f'overlap={overlap:.0%} (≥{min_overlap:.0%}), matched={len(golden_ids & output_ids)}/{len(golden_ids)}'}

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
