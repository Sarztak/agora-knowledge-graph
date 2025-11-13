import os
import json
import pandas as pd
import numpy as np

output_path = "./output"
new_output_path = "./output_remade"
data_path = "./data"

os.makedirs(new_output_path, exist_ok=True)

# === 1. Insert law name at the start of each line of long summary in the csv ===
doc_df = pd.read_csv("./data/documents.csv")

def prepend_official_name(row):
    name = row["Official name"].strip()
    summary = row["Long summary"]
    if not isinstance(summary, str) or not summary.strip():
        return np.nan
    paragraphs = [p.strip() for p in summary.split("\n") if p.strip()]
    normalized = "\n\n".join([f"{name} {p[0].lower() + p[1:] if p else ''}" for p in paragraphs])
    return normalized

doc_df["Normalized Long Summary"] = doc_df.apply(prepend_official_name, axis=1)
doc_df = doc_df.dropna(subset=['Long summary'])
doc_df = doc_df.drop_duplicates(subset=['Normalized Long Summary']).reset_index(drop=True)

# Create doc_id column using zero-padded numbering
doc_df["doc_id"] = doc_df.index.to_series().apply(lambda x: f"doc_{x+1:03d}")

doc_df.to_csv("./data/documents_normalized.csv", index=False)

# === 2. Add law name as entities in the json output ===
doc_lookup = dict(zip(doc_df["doc_id"], doc_df["Official name"]))

for file_name in os.listdir(output_path):
    if file_name.endswith(".json"):
        old_file_path = os.path.join(output_path, file_name)
        new_file_path = os.path.join(new_output_path, file_name)

        with open(old_file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipped invalid JSON file: {file_name}")
                continue

        modified = False

        for doc in data:
            doc_id = doc.get("document_id") or doc.get("doc_id")
            if not doc_id:
                continue

            official_name = doc_lookup.get(doc_id)
            if not official_name or not isinstance(official_name, str):
                continue

            entities = doc.get("entities", [])
            existing_patterns = {e.get("pattern") for e in entities}
            if official_name not in existing_patterns:
                entities.append({
                    "pattern": official_name,
                    "label": "BILL_NAME"
                })
                modified = True

            doc["entities"] = entities

        # Always save output in the new folder
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if modified:
            print(f"Updated entities in {file_name}")
        else:
            print(f"No updates needed for {file_name}")
