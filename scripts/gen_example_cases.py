#!/usr/bin/env python3
"""
用 QA Test Skills 根 SKILL.md 完整执行工作流，为示例项目生成测试用例。
用法：
  ASXS_KEY=sk-xxx python scripts/gen_example_cases.py                     # 默认电商
  ASXS_KEY=sk-xxx python scripts/gen_example_cases.py --project agent     # Agent 案例
  DS_KEY=sk-xxx python scripts/gen_example_cases.py                       # DeepSeek
"""
import json, os, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = ROOT / 'skills' / 'qa-test-skills' / 'SKILL.md'  # 入口工作流（已从根目录平级迁移到 skills/ 下）

# 目标项目配置（--project 参数选择）
PROJECTS = {
    'ecommerce': {
        'dir': ROOT / 'examples' / 'ecommerce-project',
        'name': '电商项目',
        'has_requirements': True,
    },
    'agent': {
        'dir': ROOT / 'examples' / 'agent-project',
        'name': 'AI 客服 Agent',
        'has_requirements': False,
    },
}
DEFAULT_PROJECT = 'ecommerce'

# Provider 配置（优先中转站 ASXS，回退 DeepSeek/NVIDIA）
if os.environ.get('ASXS_KEY'):
    API_BASE = 'https://api.asxs.top/v1'
    API_KEY = os.environ.get('ASXS_KEY', '')
    MODEL = os.environ.get('ASXS_MODEL', 'deepseek-chat')
elif os.environ.get('NVIDIA_KEY'):
    API_BASE = 'https://integrate.api.nvidia.com/v1'
    API_KEY = os.environ.get('NVIDIA_KEY', '')
    MODEL = 'minimaxai/minimax-m3'
else:
    API_BASE = 'https://api.deepseek.com/v1'
    API_KEY = os.environ.get('DS_KEY', '')
    MODEL = 'deepseek-chat'

MAX_TOKENS = 3000   # 中转站慢，继续降 token 确保 300s 内完成单次调用
TEMPERATURE = 0.3


def call_llm(system_prompt, user_message, max_retries=3):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        # 中转站需浏览器 UA，否则 Cloudflare 403 拦截
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    }
    payload = json.dumps({
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ],
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE,
    }).encode('utf-8')

    for attempt in range(1, max_retries + 1):
        try:
            req = Request(f'{API_BASE}/chat/completions', data=payload, headers=headers)
            resp = urlopen(req, timeout=300)
            data = json.loads(resp.read().decode('utf-8'))
            content = data['choices'][0]['message'].get('content', '') or ''
            reasoning = data['choices'][0]['message'].get('reasoning_content', '') or ''
            if not content.strip() and reasoning.strip():
                content = '\n'.join(reasoning.strip().split('\n')[-30:])
            usage = data.get('usage', {})
            return content, usage
        except HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:200]
            print(f'  ⚠️ API error {e.code}: {body} (attempt {attempt})')
            if attempt < max_retries:
                time.sleep(10 * attempt)
        except Exception as e:
            print(f'  ⚠️ 连接异常: {e} (attempt {attempt})')
            if attempt < max_retries:
                time.sleep(15 * attempt)
    raise RuntimeError('max retries exceeded')


def build_user_message(proj):
    """拼接需求文档为输入。刻意不做任何人为约束——由 LLM 按 skill 自身要求自行决策。"""
    example_dir = proj['dir']
    parts = []
    parts.append(f"请帮我完整测试这个{proj['name']}：{example_dir / 'docs' / 'prd.md'}")
    parts.append("\n===== 主需求文档 prd.md =====")
    parts.append((example_dir / 'docs' / 'prd.md').read_text(encoding='utf-8'))
    if proj['has_requirements']:
        req_dir = example_dir / 'docs' / 'requirements'
        for f in sorted(req_dir.glob('*.md')):
            parts.append(f"\n===== {f.name} =====")
            parts.append(f.read_text(encoding='utf-8'))
    # 不加任何执行要求/模块数量/格式约束——按 SKILL.md 的工作流自行决策
    return '\n'.join(parts)


def main():
    if not API_KEY:
        print('❌ 请设置环境变量 ASXS_KEY / DS_KEY / NVIDIA_KEY')
        sys.exit(1)

    # 解析 --project 参数
    proj_key = DEFAULT_PROJECT
    for i, a in enumerate(sys.argv[1:]):
        if a == '--project' and i + 1 < len(sys.argv[1:]):
            proj_key = sys.argv[1:][i + 1]
    if proj_key not in PROJECTS:
        print(f'❌ 未知项目: {proj_key}，可选: {list(PROJECTS.keys())}')
        sys.exit(1)
    proj = PROJECTS[proj_key]

    system_prompt = SKILL_FILE.read_text(encoding='utf-8')
    user_message = build_user_message(proj)
    print(f'📄 项目: {proj["name"]} ({proj_key})')
    print(f'📄 System prompt: {SKILL_FILE.name} ({len(system_prompt)} chars)')
    print(f'📄 User message: {len(user_message)} chars')
    print(f'🤖 调用 {MODEL} 执行工作流...\n')

    output, usage = call_llm(system_prompt, user_message)
    print(f'✅ 生成完成：{len(output)} chars, {usage.get("total_tokens", 0)} tokens')

    out_file = proj['dir'] / 'docs' / 'workflow-output.md'
    out_file.write_text(output, encoding='utf-8')
    print(f'📁 已保存: {out_file}')


if __name__ == '__main__':
    main()
