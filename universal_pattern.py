import os
import json
from collections import defaultdict

# === 1. Folder path ===
folder_path = "./output"

# === 2. Containers ===
pattern_to_labels = defaultdict(set)  # collect all labels for each pattern

# === 3. Iterate through all JSON files ===
for file_name in os.listdir(folder_path):
    if file_name.endswith(".json"):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipped invalid JSON file: {file_name}")
                continue

            # Each file may contain multiple documents with "entities"
            for doc in data:
                for entity in doc.get("entities", []):
                    pattern = entity["pattern"]
                    label = entity["label"]
                    pattern_to_labels[pattern].add(label)

# === 4. Identify collisions ===
multi_label_patterns = {p: list(labels) for p, labels in pattern_to_labels.items() if len(labels) > 1}
num_collisions = len(multi_label_patterns)

# === 5. Convert to unique list using first label only ===
unique_entities = [
    {"pattern": pattern, "label": next(iter(labels))}
    for pattern, labels in pattern_to_labels.items()
]

# === 6. Save results ===
output_path = os.path.join(folder_path,'..','universal_pattern_output', "unique_entities_first_label.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(unique_entities, f, indent=2, ensure_ascii=False)

# === 7. Print results ===
print(f"Unique entities saved to: {output_path}")
print(f"Total unique patterns: {len(unique_entities)}")
print(f"Patterns with multiple labels: {num_collisions}")

# print examples of collisions
if num_collisions > 0:
    print("\nList of multi-label patterns:")
    for p, labels in list(multi_label_patterns.items()):
        print(f"  {p}: {labels}")

# TODO: Rewrite the correct labels for the patterns with multiple labels
