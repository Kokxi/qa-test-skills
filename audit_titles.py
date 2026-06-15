"""Analyze Red Flags titles for quality, consistency, and improvement areas"""
import json, re
from collections import Counter

with open(r"E:\opentest\redflags_mapping_v2.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

all_titles = []
issues = []

for entry in mapping:
    skill = entry["skill"]
    for row in entry["rows"]:
        t = row["new_title"]
        # Check length
        clen = len(t)
        # End with punctuation
        has_q = t.endswith("？") or t.endswith("？") or t.endswith("。") or t.endswith("！") or t.endswith("？") or t.endswith("？")
        # Start with first-person cues
        is_first_person = any(t.startswith(w) for w in ["我", "我们", "咱", "这", "那", "凭", "让", "AI", "问", "写", "图", "追", "短", "一", "不", "代", "门", "质", "度", "偶", "先", "上", "果", "中", "组", "静", "都", "每", "效", "修", "描", "翻"])
        
        all_titles.append({
            "skill": skill,
            "title": t,
            "len": clen,
            "has_end_punct": has_q,
        })

# Length distribution
lengths = [t["len"] for t in all_titles]
print(f"=== Length Stats ===")
print(f"Total titles: {len(all_titles)}")
print(f"Shortest: {min(lengths)} ('{all_titles[lengths.index(min(lengths))]['title']}')")
print(f"Longest: {max(lengths)} ('{all_titles[lengths.index(max(lengths))]['title']}')")
print(f"Avg: {sum(lengths)/len(lengths):.1f}")

under_10 = [t for t in all_titles if t["len"] < 10]
over_30 = [t for t in all_titles if t["len"] > 30]
print(f"\nUnder 10 chars ({len(under_10)}):")
for t in under_10:
    print(f"  [{t['len']}] {t['title']} ({t['skill']})")
print(f"\nOver 30 chars ({len(over_30)}):")
for t in over_30:
    print(f"  [{t['len']}] {t['title']} ({t['skill']})")

# Punct check
no_end = [t for t in all_titles if not t["has_end_punct"]]
print(f"\n=== Punct Check ===")
print(f"Missing ending punct: {len(no_end)}")
for t in no_end:
    print(f"  [{t['len']}] {t['title']} ({t['skill']})")

# Duplicate titles
title_texts = [t["title"] for t in all_titles]
dupes = {t: c for t, c in Counter(title_texts).items() if c > 1}
print(f"\n=== Duplicates ({len(dupes)}) ===")
for t, c in dupes.items():
    skills = [x["skill"] for x in all_titles if x["title"] == t]
    print(f"  x{c} \"{t}\" in {skills}")

# Same pattern check
print(f"\n=== Pattern Analysis ===")
patterns = Counter()
for t in all_titles:
    # Classify the opening phrase
    first_2 = t[:3]
    patterns[first_2] += 1
for pattern, count in patterns.most_common(20):
    examples = [x["title"] for x in all_titles if x["title"][:3] == pattern][:2]
    print(f"  '{pattern}' x{count}: {examples}")
