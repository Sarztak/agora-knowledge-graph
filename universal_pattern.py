import os
import json
from collections import defaultdict

# Import all remapping logic
from entity_remapping import (
    entity_map,            # pattern normalization (Secretary → Department)
    label_map,             # NER label collapse (ROLE → ACTOR)
    normalized_entity_label  # FINAL canonical pattern → correct label
)

# ================================================================
# 1. Setup
# ================================================================
INPUT_FOLDER = "./output_remade"
OUTPUT_FOLDER = "./universal_pattern_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pattern_to_labels = defaultdict(set)

# ================================================================
# 2. Scan all output/*.json for raw patterns
# ================================================================
for file_name in os.listdir(INPUT_FOLDER):
    if not file_name.endswith(".json"):
        continue

    path = os.path.join(INPUT_FOLDER, file_name)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Skipping invalid JSON: {file_name}")
        continue

    for doc in data:
        for ent in doc.get("entities", []):
            raw_pattern = ent.get("pattern")
            raw_label = ent.get("label")

            if not raw_pattern or not raw_label:
                continue

            # Canonicalize entity pattern
            canonical_pattern = entity_map.get(raw_pattern, raw_pattern)

            # Collapse raw NER label
            coarse_label = label_map.get(raw_label, raw_label)

            # Final override if canonical exists in normalized_entity_label
            final_label = normalized_entity_label.get(canonical_pattern, coarse_label)

            pattern_to_labels[canonical_pattern].add(final_label)

# ================================================================
# 3. ADD all canonical patterns from entity_map
# ================================================================
for raw, canonical in entity_map.items():

    canonical_label = normalized_entity_label.get(canonical, "ACTOR")
    pattern_to_labels[canonical].add(canonical_label)

    raw_label = normalized_entity_label.get(canonical, "ACTOR")
    pattern_to_labels[raw].add(raw_label)

# ================================================================
# 4. Identify multi-label collisions
# ================================================================
multi_label_patterns = {
    p: sorted(list(labels))
    for p, labels in pattern_to_labels.items()
    if len(labels) > 1
}

print(f"\nNumber of multi-label collisions: {len(multi_label_patterns)}")
for p, labels in list(multi_label_patterns.items())[:20]:
    print(f"  {p}: {labels}")

# ================================================================
# 5. Build unique_entities (collapsed)
# ================================================================
unique_entities = []
for pattern, labels in pattern_to_labels.items():
    chosen_label = sorted(list(labels))[0]
    unique_entities.append({
        "pattern": pattern,
        "label": chosen_label
    })

# ================================================================
# 6. PREPEND normalized_entity_label entries
# ================================================================
normalized_entries = [
    {"pattern": pattern, "label": label}
    for pattern, label in normalized_entity_label.items()
]

# Remove duplicates: keep normalized patterns as authoritative
final_patterns = {}
# 1. Insert normalized patterns first
for entry in normalized_entries:
    final_patterns[entry["pattern"]] = entry["label"]
# 2. Insert the rest only if not already overwritten
for entry in unique_entities:
    if entry["pattern"] not in final_patterns:
        final_patterns[entry["pattern"]] = entry["label"]

# Convert final dictionary back to list
final_unique_entities = [
    {"pattern": pattern, "label": label}
    for pattern, label in final_patterns.items()
]

# ================================================================
# 7. Save final dictionary
# ================================================================
output_path = os.path.join(OUTPUT_FOLDER, "unique_entities_first_label.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_unique_entities, f, indent=2, ensure_ascii=False)

print(f"\nSaved universal pattern dictionary:")
print(f"→ {output_path}")
print(f"Total unique patterns: {len(final_unique_entities)}\n")
