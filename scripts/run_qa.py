#!/usr/bin/env python3
"""
QA Test Skills 统一入口。用法：
  python scripts/run_qa.py validate        # 校验依赖图对称性
  python scripts/run_qa.py grade <ws>      # 评估打分（ws=workspace/iteration-N）
  python scripts/run_qa.py benchmark <ws>  # 聚合基准
  python scripts/run_qa.py smoke           # 烟雾测试（单 eval 跑通 grade 管线）
  python scripts/run_qa.py audit           # ClawHub security audit 本地预检
  python scripts/run_qa.py standards       # 校验工作流⚠️标注与 ID 规范一致性
"""
import subprocess, sys, pathlib, json, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'

def run(script, *args):
    cmd = ['python', str(SCRIPTS / script)] + list(args)
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8')

def smoke():
    """烟雾测试：构造临时 workspace 跑一条 eval 验证 grade 管线通."""
    import tempfile, shutil
    ws = pathlib.Path(tempfile.mkdtemp()) / 'iteration-smoke'
    # 构造 eval-0/with_skill/outputs/ 放一个假输出
    out = ws / 'eval-0' / 'with_skill' / 'outputs'
    out.mkdir(parents=True)
    (out / '测试报告.md').write_text('TC_AUTH_001 REQ-AUTH-001\n测试通过', encoding='utf-8')
    r = run('grade_evals.py', str(ws))
    ok = 'passed' in r.stdout or 'eval-' in r.stdout
    print(f"smoke grade_evals: {'✅' if ok else '❌'}")
    if r.stderr: print(f"  stderr: {r.stderr[:200]}")
    shutil.rmtree(ws.parent, ignore_errors=True)
    return ok

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'validate':
        r = run('validate_deps.py'); print(r.stdout)
    elif cmd == 'grade':
        r = run('grade_evals.py', sys.argv[2]); print(r.stdout)
    elif cmd == 'benchmark':
        r = run('aggregate_benchmark.py', sys.argv[2], '--skill-name', 'qa-test-skills'); print(r.stdout)
    elif cmd == 'smoke':
        smoke()
    elif cmd == 'audit':
        r = run('check_security_audit.py', *sys.argv[2:]); print(r.stdout)
    elif cmd == 'standards':
        r = run('validate_standards.py'); print(r.stdout)
    else:
        print(f"未知命令: {cmd}\n{__doc__}"); sys.exit(1)

if __name__ == '__main__':
    main()
