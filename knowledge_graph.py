import spacy
import json
import networkx as nx
from tqdm import tqdm
import pandas as pd
import os
from collections import defaultdict

# === 1. Load your universal pattern dictionary ===
with open("./universal_pattern_output/unique_entities_first_label.json", "r", encoding="utf-8") as f:
    patterns = json.load(f)

# === 2. Initialize spaCy model with EntityRuler ===
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(patterns)

# === 3. Load normalized documents ===
df = pd.read_csv("./data/documents_normalized.csv")
if "Normalized Long Summary" not in df.columns:
    raise ValueError("Could not find column 'Normalized Long Summary' in documents_normalized.csv")

# === 4. Apply NER ===
results = []
for i, text in enumerate(df["Normalized Long Summary"].fillna("")):
    doc = nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    results.append({"index": i + 1, "text": text, "entities": entities})

# === 5. Save NER results ===
output_path = "ner_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Finished processing {len(df)} documents. Saved to {output_path}.")


# === 6. Knowledge Graph Construction ===
print("\n=== Building Knowledge Graph ===")
nlp = spacy.load("en_core_web_md", disable=["ner"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

with open("ner_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

G = nx.DiGraph()

# === Helper function (multi-word entity support) ===
def find_entities_in_sentence(entities, sent_text):
    """Return list of entity strings that appear in this sentence text (exact span match)."""
    return [ent for ent in entities if ent in sent_text]


# === Build graph ===
for item in tqdm(data, desc="Extracting relations"):
    text = item["text"]
    entities = {e["text"]: e["label"] for e in item["entities"]}
    doc = nlp(text)

    # Add all entities as nodes
    for ent_text, ent_label in entities.items():
        G.add_node(ent_text, label=ent_label)

    # Verb-based relationships (exact + multiword)
    for sent in doc.sents:
        sent_entities = find_entities_in_sentence(entities.keys(), sent.text)

        for token in sent:
            if token.pos_ == "VERB":
                subj = [
                    ent for ent in sent_entities
                    if any(t.dep_ in ("nsubj", "nsubjpass") for t in token.children)
                    and ent in sent.text
                ]
                obj = [
                    ent for ent in sent_entities
                    if any(t.dep_ in ("dobj", "pobj", "attr", "appos") for t in token.children)
                    and ent in sent.text
                ]

                for s in subj:
                    for o in obj:
                        if s != o:
                            G.add_edge(
                                s, o,
                                relation=token.lemma_,
                                relation_type="verb_dependency",
                                source_doc=item["index"]
                            )

# === 7. Save Graph ===
output_file_name = "ai_policy_kg_with_dependencies_3.gexf"
nx.write_gexf(G, output_file_name)

print(f"\nFinished building graph.")
print(f"Total nodes: {len(G.nodes)}, Total edges: {len(G.edges)}")
print(f"Saved graph as {output_file_name}")
print("You can view it at https://lite.gephi.org/v1.0.0/#/")

# === Print all node-edge-node triples ===
print("\n=== All Extracted Relations ===")
for u, v, data in G.edges(data=True):
    rel = data.get("relation", "")
    print(f"{u}  --[{rel}]-->  {v}")
