"""
Verify all 40 SKILL.md files after transformation.
Checks: frontmatter integrity, ALWAYS marker, Red Flags table, description triggers.
"""
from pathlib import Path
import re

skills_dir = Path(r"E:\opentest\skills")
skill_files = sorted(skills_dir.glob("qa-*/SKILL.md"))

issues = 0
warnings = []

for sf in skill_files:
    name = sf.parent.name
    content = sf.read_text(encoding="utf-8")

    # Check 1: frontmatter integrity
    if not content.startswith("---"):
        warnings.append(f"[BROKEN] {name}: missing opening ---")
        issues += 1
        continue

    second_marker = content.find("\n---", 3)
    if second_marker == -1:
        warnings.append(f"[BROKEN] {name}: missing closing ---")
        issues += 1
        continue

    # Check 2: ALWAYS marker present
    has_always = "ALWAYS use this exact template" in content
    if not has_always:
        warnings.append(f"[MISSING] {name}: no ALWAYS marker")
        issues += 1

    # Check 3: Red Flags format
    if "| 想法 | 事实 |" in content:
        table_rows = [l for l in content.split("\n") if l.strip().startswith('| **"')]
        if not table_rows:
            warnings.append(f"[EMPTY] {name}: table header but no data rows")
            issues += 1
    else:
        if "## 常见翻车点" in content or "## 常见翻车点（想法 vs 事实）" in content:
            if "- **" in content:
                warnings.append(f"[LEGACY] {name}: section exists but still bullet format")
                issues += 1
            else:
                pass  # No red flags section at all = OK
    # Check 4: description has trigger keywords if metadata.trigger exists
    fm_text = content[4:second_marker]
    if "trigger:" in fm_text:
        tg_match = re.search(r"trigger:\s*(.+)", fm_text)
        if tg_match:
            tg_val = tg_match.group(1).strip()
            desc_match = re.search(r'description:\s*"(.+?)"', fm_text)
            if desc_match:
                desc_val = desc_match.group(1)
                if "\u89e6\u53d1" not in desc_val:
                    warnings.append(f"[WARN] {name}: has trigger ({tg_val[:30]}...) but desc lacks '\u89e6\u53d1'")
                    issues += 1

print(f"Total files: {len(skill_files)}")
if warnings:
    for w in warnings:
        print(w)
    print(f"\nIssues found: {issues}")
else:
    print("All 40 files passed integrity checks!")
