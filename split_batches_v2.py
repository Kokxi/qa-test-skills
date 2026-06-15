import json

with open(r"E:\opentest\redflags_data_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
half = total // 2
batch1 = data[:half]
batch2 = data[half:]

print(f"Batch 1: {len(batch1)} files, {sum(len(o['rows']) for o in batch1)} rows")
print(f"Batch 2: {len(batch2)} files, {sum(len(o['rows']) for o in batch2)} rows")

with open(r"E:\opentest\redflags_batch1_v2.json", "w", encoding="utf-8") as f:
    json.dump(batch1, f, ensure_ascii=False, indent=2)

with open(r"E:\opentest\redflags_batch2_v2.json", "w", encoding="utf-8") as f:
    json.dump(batch2, f, ensure_ascii=False, indent=2)

# Also show first entry structure
print("\nSample entry:")
print(json.dumps(data[0], ensure_ascii=False, indent=2)[:500])
