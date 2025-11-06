import os
import json
import pandas as pd
import numpy as np

output_path = "./output_og"
data_path = "./data"

# === 1. Insert law name at the start of each line of long summary in the csv ===
doc_df = pd.read_csv("./data/documents.csv")
def prepend_official_name(row):
    name = row["Official name"].strip()
    summary = row["Long summary"]
    if not isinstance(summary, str) or not summary.strip():
        return np.nan
    # Split by line breaks
    paragraphs = [p.strip() for p in summary.split("\n") if p.strip()]
    # Prepend name to each paragraph
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

# Iterate through all JSON files in the output directory
for file_name in os.listdir(output_path):
    if file_name.endswith(".json"):
        file_path = os.path.join(output_path, file_name)  # <-- fixed from os.path.json

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipped invalid JSON file: {file_name}")
                continue

        modified = False  # track whether we changed anything

        # Iterate through each document entry in the JSON
        for doc in data:
            doc_id = doc.get("document_id") or doc.get("doc_id")
            if not doc_id:
                continue

            official_name = doc_lookup.get(doc_id)
            if not official_name or not isinstance(official_name, str):
                continue

            entities = doc.get("entities", [])

            # Check if the official name is already an entity pattern
            existing_patterns = {e.get("pattern") for e in entities}
            if official_name not in existing_patterns:
                entities.append({
                    "pattern": official_name,
                    "label": "BILL NAME"
                })
                modified = True

            # Write back updated entity list
            doc["entities"] = entities

        # Save changes only if modified
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated entities in {file_name}")
        else:
            print(f"No updates needed for {file_name}")

