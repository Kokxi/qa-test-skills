#!/usr/bin/env python3
"""
QA Test Skills 统一质量门禁
  python scripts/run_qa.py spec             # Agent Skills 规范合规（官方 skills-ref）
  python scripts/run_qa.py check            # 完整性一致性检查（15 项）
  python scripts/run_qa.py validate         # 依赖引用图校验
  python scripts/run_qa.py selftest         # 门禁自测：逐项验证「该报的报、不该报的不报」
  python scripts/run_qa.py all              # spec + check + validate（推荐，发布前跑这个）
  python scripts/run_qa.py cases <文件...>   # 9 列标准用例表校验
  python scripts/run_qa.py grade <ws>       # 分级跑 evals（ws=workspace/iteration-N）
  python scripts/run_qa.py benchmark <ws>   # 聚合基准测试
  python scripts/run_qa.py smoke            # 不需要真实模型，验证 eval→grade 链路
  python scripts/run_qa.py audit            # ClawHub security audit 本地预检
  python scripts/run_qa.py standards        # 校验全局标准、ID 规范一致性
"""
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / 'scripts'


def run(script, *args):
    cmd = [sys.executable, str(SCRIPTS / script)] + list(args)
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8')


def smoke():
    """不需要真实模型：造一个临时 workspace 验证 eval 抓取 → grade 链路是否通。"""
    import tempfile
    import shutil
    ws = pathlib.Path(tempfile.mkdtemp()) / 'iteration-smoke'
    out = ws / 'eval-0' / 'with_skill' / 'outputs'
    out.mkdir(parents=True)
    (out / '示例产物.md').write_text('TC_AUTH_001 REQ-AUTH-001\n示例通过', encoding='utf-8')
    r = run('grade_evals.py', str(ws))
    ok = 'passed' in r.stdout or 'eval-' in r.stdout
    print(f"smoke grade_evals: {'通过' if ok else '未通过'}")
    if r.stderr:
        print(f"  stderr: {r.stderr[:200]}")
    shutil.rmtree(ws.parent, ignore_errors=True)
    return ok


# 门禁编排：每一步都是独立脚本，退出码即结论
GATES = {
    'spec':      [('check_spec_compliance.py', [])],
    'check':     [('integrity_check.py', [])],
    'validate':  [('validate_deps.py', [])],
    'standards': [('validate_standards.py', [])],
    'selftest':  [('gate_selftest.py', [])],
    'all':       [('check_spec_compliance.py', []),
                  ('integrity_check.py', []),
                  ('validate_deps.py', [])],
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]

    if cmd in GATES:
        failed = []
        for script, args in GATES[cmd]:
            r = run(script, *args)
            if r.stdout:
                print(r.stdout)
            if r.returncode != 0:
                failed.append(script)
                if r.stderr:
                    print(r.stderr[:500])
        if failed:
            print(f"\n❌ 失败门禁: {', '.join(failed)}")
        else:
            print(f"\n✅ {len(GATES[cmd])} 道门禁全部通过")
        sys.exit(1 if failed else 0)

    if cmd == 'cases':
        if len(sys.argv) < 3:
            print('用法: run_qa.py cases <文件...>')
            sys.exit(1)
        r = run('validate_testcase_table.py', *sys.argv[2:])
        print(r.stdout)
        sys.exit(r.returncode)
    if cmd == 'grade':
        r = run('grade_evals.py', sys.argv[2])
        print(r.stdout)
        sys.exit(r.returncode)
    if cmd == 'benchmark':
        r = run('aggregate_benchmark.py', sys.argv[2], '--skill-name', 'qa-test-skills')
        print(r.stdout)
        sys.exit(r.returncode)
    if cmd == 'smoke':
        sys.exit(0 if smoke() else 1)
    if cmd == 'audit':
        r = run('check_security_audit.py', *sys.argv[2:])
        print(r.stdout)
        sys.exit(r.returncode)

    print(f'未知命令: {cmd}\n{__doc__}')
    sys.exit(1)


if __name__ == '__main__':
    main()
