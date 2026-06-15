"""
Replace Red Flags "想法" column titles in SKILL.md files with new_title values.
The new_line is constructed from old_line by replacing the title (between **") and "**) 
with the new_title.
"""
import json, re
from pathlib import Path

with open(r"E:\opentest\redflags_mapping_v2.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

changed = 0
total_replacements = 0
warnings = 0

for entry in mapping:
    filepath = Path(entry["file"])
    if not filepath.exists():
        print(f"[WARN] {filepath} not found")
        warnings += 1
        continue
    
    content = filepath.read_text(encoding="utf-8")
    original = content
    
    for item in entry["rows"]:
        old_line = item["old_line"]
        new_title = item["new_title"]
        
        # Construct new_line: replace the title between **" and "** 
        # Pattern: | **"OLD_TITLE"** | explanation... |
        # Keep everything before first **" and after "**
        # old_line format: | **"title"** | explanation |
        idx1 = old_line.find('**"')
        idx2 = old_line.find('"**', idx1)
        if idx1 == -1 or idx2 == -1:
            print(f"[WARN] Cannot parse line pattern: {old_line[:60]}")
            warnings += 1
            continue
        
        prefix = old_line[:idx1 + 3]  # includes **"
        suffix = old_line[idx2:]      # includes "**
        new_line = f'{prefix}{new_title}{suffix}'
        
        if old_line in content:
            content = content.replace(old_line, new_line, 1)
            total_replacements += 1
        else:
            print(f"[WARN] Line not found in {filepath.parent.name}: {old_line[:60]}")
            warnings += 1
    
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        changed += 1
        print(f"[OK] {filepath.parent.name}: updated")

print(f"\nDone: {changed} files updated, {total_replacements} replacements, {warnings} warnings")
