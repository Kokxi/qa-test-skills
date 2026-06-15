"""
Transform 40 QA SKILL.md files to match skill-creator standard.

Transformations:
1. Description normalization - add trigger keywords, ensure quoted format
2. ALWAYS marker - add template usage reminder before prompt code blocks
3. Red Flags table conversion - bullet list to "想法 vs 事实" table
"""

import re
import os
from pathlib import Path

SKILLS_DIR = Path(r"E:\opentest\skills")

def parse_frontmatter(content):
    """Parse YAML frontmatter from SKILL.md content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    remaining = content[match.end():]
    
    # Manual YAML parsing (limited, enough for our structure)
    fm = {}
    current_key = None
    current_list = []
    in_list = False
    
    for line in fm_text.split('\n'):
        # Top-level key: value
        if not line.startswith(' ') and not line.startswith('-'):
            if in_list and current_key:
                fm[current_key] = current_list
                current_list = []
                in_list = False
            
            key_match = re.match(r'^(\w[\w-]*):\s*(.*)', line)
            if key_match:
                current_key = key_match.group(1)
                value = key_match.group(2).strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if value == '':
                    in_list = True
                else:
                    fm[current_key] = value
                    current_key = None
        
        # List items under a key
        elif line.startswith('- ') and current_key:
            item = line[2:].strip()
            if item.startswith('"') and item.endswith('"'):
                item = item[1:-1]
            if item.startswith("'") and item.endswith("'"):
                item = item[1:-1]
            current_list.append(item)
    
    if in_list and current_key and current_list:
        fm[current_key] = current_list
    
    return fm, remaining


def build_frontmatter(fm):
    """Rebuild YAML frontmatter from dict."""
    lines = ['---']
    for key, value in fm.items():
        if key in ('allowed-tools',):
            if isinstance(value, list):
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - {item}')
            else:
                lines.append(f'{key}:')
                for item in value.split(','):
                    item = item.strip()
                    if item:
                        lines.append(f'  - {item}')
        elif key == 'metadata':
            lines.append('metadata:')
            for mk, mv in value.items():
                if isinstance(mv, list):
                    lines.append(f'  {mk}: {", ".join(mv)}')
                else:
                    lines.append(f'  {mk}: {mv}')
        elif key in ('description',):
            # Keep description as a single-line quoted YAML string
            lines.append(f'{key}: "{value}"')
        elif key == 'name':
            lines.append(f'{key}: {value}')
        else:
            if isinstance(value, list):
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - {item}')
            else:
                lines.append(f'{key}: {value}')
    lines.append('---')
    return '\n'.join(lines)


def transform_description(fm):
    """Ensure description includes trigger keywords from metadata.trigger."""
    if 'description' not in fm:
        return False
    
    desc = fm['description']
    trigger_list = []
    if 'metadata' in fm and isinstance(fm['metadata'], dict) and 'trigger' in fm['metadata']:
        trigger_list = fm['metadata']['trigger']
        if isinstance(trigger_list, str):
            trigger_list = [t.strip() for t in trigger_list.split(',')]
    
    if not trigger_list:
        return False
    
    # Check if description already has trigger info
    if '触发：' in desc or '触发:' in desc:
        return False  # Already has trigger, skip
    
    # Add trigger to description
    trigger_str = ', '.join(trigger_list)
    new_desc = f"{desc}。触发：{trigger_str}"
    
    fm['description'] = new_desc
    return True


def add_always_marker(content):
    """Add ALWAYS marker before prompt template code blocks in AI协作模式 section."""
    # Find AI协作模式 section and add marker before each code block in it
    lines = content.split('\n')
    new_lines = []
    in_ai_section = False
    in_code_block = False
    code_block_start = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect AI协作模式 section
        if line.strip().startswith('## AI 协作模式') or line.strip().startswith('## AI协作模式'):
            in_ai_section = True
        
        # Detect end of AI section (next ## that's not deeper level)
        if in_ai_section and line.strip().startswith('## ') and 'AI' not in line and '协作' not in line:
            in_ai_section = False
        
        # In AI section, detect code blocks
        if in_ai_section and line.strip().startswith('```') and not in_code_block:
            # Check previous line - if it's a header or empty, this is a template block
            prev_stripped = lines[i-1].strip() if i > 0 else ''
            if prev_stripped == '' or prev_stripped.startswith('#'):
                # This is a template code block - add ALWAYS marker before it
                marker = '> **ALWAYS use this exact template** — 每次使用本技能时，必须使用此模板与 AI 协作。'
                # Only add if not already present
                if i < 1 or lines[i-1].strip() != marker:
                    new_lines.append(marker)
                in_code_block = True
                new_lines.append(line)
            else:
                in_code_block = True
                new_lines.append(line)
        elif in_ai_section and line.strip().startswith('```') and in_code_block:
            in_code_block = False
            new_lines.append(line)
        else:
            new_lines.append(line)
        
        i += 1
    
    return '\n'.join(new_lines)


def transform_red_flags_table(content):
    """Convert 常见翻车点 from bullet list to 想法vs事实 table."""
    lines = content.split('\n')
    
    # Find 常见翻车点 section
    section_start = None
    section_end = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '## 常见翻车点':
            section_start = i
        elif section_start is not None and stripped.startswith('## ') and i > section_start:
            section_end = i
            break
    
    if section_start is None:
        return content
    
    if section_end is None:
        section_end = len(lines)
    
    # Check if already in table format
    section_lines = lines[section_start:section_end]
    if any('| 想法' in l for l in section_lines):
        return content  # Already converted
    
    # Extract bullet items
    bullets = []
    for line in section_lines[1:]:  # Skip header
        stripped = line.strip()
        if stripped.startswith('- **') and '**：' in stripped:
            # Parse: - **标题**：说明
            match = re.match(r'- \*\*(.+?)\*\*[：:](.*)', stripped)
            if match:
                title = match.group(1).strip()
                explanation = match.group(2).strip()
                bullets.append((title, explanation))
        elif stripped.startswith('- **') and '**：' not in stripped and '**:' not in stripped:
            # Try with **： separated by newline or other format
            match = re.match(r'- \*\*(.+?)\*\*(.*)', stripped)
            if match:
                title = match.group(1).strip()
                rest = match.group(2).strip()
                if rest.startswith('：') or rest.startswith(':'):
                    bullets.append((title, rest[1:].strip()))
                else:
                    bullets.append((title, rest))
    
    if not bullets:
        return content
    
    # Build table
    table_lines = [
        '## 常见翻车点（想法 vs 事实）',
        '',
        '| 想法 | 事实 |',
        '|------|------|',
    ]
    
    for title, explanation in bullets:
        table_lines.append(f'| **"{title}"** | {explanation} |')
    
    # Replace section
    new_lines = lines[:section_start] + table_lines + lines[section_end:]
    return '\n'.join(new_lines)


def process_skill_file(filepath):
    """Process a single SKILL.md file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Step 1: Parse frontmatter
    fm, body = parse_frontmatter(content)
    if not fm:
        print(f"  ⚠️  No frontmatter found in {filepath.name}")
        return False
    
    # Step 2: Transform description
    if transform_description(fm):
        new_fm = build_frontmatter(fm)
        content = new_fm + '\n' + body.lstrip()
        changes.append('description')
    
    # Step 3: Add ALWAYS marker
    new_content = add_always_marker(content)
    if new_content != content:
        content = new_content
        changes.append('always_marker')
    
    # Step 4: Transform Red Flags table
    new_content = transform_red_flags_table(content)
    if new_content != content:
        content = new_content
        changes.append('red_flags_table')
    
    # Write back if changes made
    if changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] {filepath.parent.name}: {', '.join(changes)}")
        return True
    else:
        print(f"  [--] {filepath.parent.name}: no changes needed")
        return False


def main():
    skill_dirs = sorted(SKILLS_DIR.glob('qa-*/'))
    total = len(skill_dirs)
    changed = 0
    
    print(f"Found {total} skill directories\n")
    
    for skill_dir in skill_dirs:
        skill_file = skill_dir / 'SKILL.md'
        if not skill_file.exists():
            print(f"  [WARN] SKILL.md not found in {skill_dir.name}")
            continue
        if process_skill_file(skill_file):
            changed += 1
    
    print(f"\nDone: {changed}/{total} files modified")


if __name__ == '__main__':
    main()
