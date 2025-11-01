import spacy
import json
import networkx as nx
import pandas as pd

# === 1. Load your universal pattern dictionary ===
with open("./universal_pattern_output/unique_entities_first_label.json", "r", encoding="utf-8") as f:
    patterns = json.load(f)

# === 2. Initialize spaCy model ===
# You can start with a blank English pipeline or a pretrained model
nlp = spacy.blank("en")

# === 3. Add the EntityRuler ===
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(patterns)

# === 4. Load documents.csv ===
df = pd.read_csv("/Users/blag/Documents/UChicago MS/2025 Fall/agora-knowledge-graph/data/documents.csv")
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

# === 6. Save results ===
output_path = "ner_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Finished processing {len(df)} documents.")
print(f"Results saved to {output_path}")


# === 7. Knowledge graph construction ===
# Load English model (medium or large recommended)
nlp = spacy.load("en_core_web_md")

# Load NER results
with open("ner_results.json") as f:
    data = json.load(f)

G = nx.DiGraph()

for item in data:

    doc = nlp(item["text"]) # doc sentence
    entities = {e["text"]: e["label"] for e in item["entities"]}


    for token in doc:
        # Look for verbs connecting two recognized entities
        if token.pos_ == "VERB":
            subj = [child.text for child in token.children if child.dep_ in ("nsubj", "nsubjpass") and child.text in entities]
            obj = [child.text for child in token.children if child.dep_ in ("dobj", "pobj") and child.text in entities]
            for s in subj:
                for o in obj:
                    #breakpoint()
                    G.add_node(s, label=entities[s])
                    G.add_node(o, label=entities[o])
                    G.add_edge(s, o, relation=token.lemma_, context=item["index"])

nx.write_gexf(G, "ai_policy_kg_with_dependencies.gexf")
# View graph at https://lite.gephi.org/v1.0.0/#/