"""
Extract Red Flags table rows from all 40 SKILL.md files into a JSON.
Output: { "skill_name": [{"line_idx": N, "title": "...", "explanation": "..."}, ...] }
Also capture surrounding context for verification.
"""
import json, re
from pathlib import Path

skills_dir = Path(r"E:\opentest\skills")
output = []

for sf in sorted(skills_dir.glob("qa-*/SKILL.md")):
    content = sf.read_text(encoding="utf-8")
    name = sf.parent.name

    # Find Red Flags table section
    lines = content.split("\n")
    in_table = False
    rows = []
    table_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## 常见翻车点"):
            table_start = i
        if table_start is not None and stripped.startswith("| 想法 | 事实 |"):
            in_table = True
            continue
        if in_table:
            if stripped.startswith("|------"):
                continue
            if stripped.startswith("| **"):
                # Parse table row
                inner = stripped.strip("|").strip()
                parts = inner.split("|", 1)
                if len(parts) == 2:
                    title = parts[0].strip().strip('"').strip("**")
                    explanation = parts[1].strip().strip('"')
                    rows.append({
                        "line": i + 1,
                        "title": title,
                        "explanation": explanation,
                    })
            elif not stripped.startswith("|"):
                in_table = False

    if rows:
        output.append({
            "skill": name,
            "file": str(sf),
            "rows": rows,
        })

with open(r"E:\opentest\redflags_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total_rows = sum(len(o["rows"]) for o in output)
print(f"Extracted {total_rows} Red Flags rows from {len(output)} files")
for o in output:
    print(f"  {o['skill']}: {len(o['rows'])} rows")
