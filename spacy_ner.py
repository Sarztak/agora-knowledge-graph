import spacy
from spacy.pipeline import EntityRuler
import pandas as pd
import json

# === 1. Load your universal pattern dictionary ===
with open("/Users/blag/Documents/UChicago MS/2025 Fall/agora-knowledge-graph/output/unique_entities_first_label.json", "r", encoding="utf-8") as f:
    patterns = json.load(f)

# === 2. Initialize spaCy model ===
# You can start with a blank English pipeline or a pretrained model
nlp = spacy.blank("en")

# === 3. Add the EntityRuler ===
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(patterns)

# === 4. Load your documents.csv ===
df = pd.read_csv("/Users/blag/Documents/UChicago MS/2025 Fall/agora-knowledge-graph/data/documents.csv")

# Make sure your text column name matches
if "Long summary" not in df.columns:
    raise ValueError("Could not find column 'Long summary' in documents.csv")

# === 5. Apply NER to each document ===
results = []

for i, text in enumerate(df["Long summary"].fillna("")):
    doc = nlp(text)
    entities = [
        {"text": ent.text, "label": ent.label_}
        for ent in doc.ents
    ]
    results.append({
        "index": i,
        "text": text,
        "entities": entities
    })

# === 6. Optionally save results ===
output_path = "ner_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Finished processing {len(df)} documents.")
print(f"Results saved to {output_path}")
