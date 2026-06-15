"""
Extract Red Flags table rows from all 40 SKILL.md files.
Captures the full table line and constructs old/new line with line numbers.
"""
import json, re
from pathlib import Path

skills_dir = Path(r"E:\opentest\skills")
output = []

for sf in sorted(skills_dir.glob("qa-*/SKILL.md")):
    content = sf.read_text(encoding="utf-8")
    name = sf.parent.name

    lines = content.split("\n")
    in_table = False
    table_header_line = None
    rows = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## 常见翻车点"):
            table_header_line = i
        if table_header_line is not None and stripped.startswith("| 想法 | 事实 |"):
            in_table = True
            continue
        if in_table:
            if stripped.startswith("|------"):
                continue
            if stripped.startswith("|"):
                # Check if this is a separator or end
                if stripped.startswith("| **"):
                    # Parse table row
                    inner = stripped.strip("|").strip()
                    parts = inner.split("|", 1)
                    if len(parts) == 2:
                        title = parts[0].strip().strip("**").strip('"')
                        explanation = parts[1].strip().strip('"')
                        rows.append({
                            "line": i + 1,
                            "old_line": lines[i],  # exact original line
                            "title": title,
                            "explanation": explanation,
                        })
                else:
                    # Not a valid row - table ended
                    if not stripped.startswith("| **"):
                        in_table = False
            elif not stripped.startswith("|"):
                in_table = False

    if rows:
        output.append({
            "skill": name,
            "file": str(sf),
            "rows": rows,
        })

with open(r"E:\opentest\redflags_data_v2.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total_rows = sum(len(o["rows"]) for o in output)
print(f"Extracted {total_rows} Red Flags rows from {len(output)} files")
for o in output:
    print(f"  {o['skill']}: {len(o['rows'])} rows")
