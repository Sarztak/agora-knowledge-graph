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

# === Preload document metadata for KG ===
# We assume df contains columns: doc_id, Official name, Normalized Long Summary
doc_meta = {}
for idx, row in df.iterrows():
    doc_index = idx + 1  # because source_doc starts at 1
    doc_meta[doc_index] = {
        "doc_id": row.get("doc_id", f"doc_{doc_index:03d}"),
        "doc_name": row.get("Official name", None),
        "text": row.get("Normalized Long Summary", "")
    }

# === Helper: extract evidence sentence ===
def find_sentence(text, ent1, ent2):
    """Return sentence containing both ent1 and ent2."""
    if not isinstance(text, str):
        return None
    sentences = text.replace("\n", " ").split(". ")
    for s in sentences:
        if ent1 in s and ent2 in s:
            return s.strip()
    return None

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
    """Return list of entity strings that appear in this sentence text."""
    return [ent for ent in entities if ent in sent_text]


# === Build graph ===
for item in tqdm(data, desc="Extracting relations"):
    text = item["text"]
    entities = {e["text"]: e["label"] for e in item["entities"]}
    doc = nlp(text)

    source_doc = item["index"]
    meta = doc_meta.get(source_doc, {})
    doc_id = meta.get("doc_id")
    doc_name = meta.get("doc_name")
    full_text = meta.get("text", "")

    # Add all entities as nodes
    for ent_text, ent_label in entities.items():
        G.add_node(ent_text, label=ent_label)

    # Verb-based relationships
    for sent in doc.sents:
        sent_entities = find_entities_in_sentence(entities.keys(), sent.text)

        for token in sent:
            if token.pos_ == "VERB":
                subj = [
                    ent for ent in sent_entities
                    if any(t.dep_ in ("nsubj", "nsubjpass") for t in token.children)
                ]
                obj = [
                    ent for ent in sent_entities
                    if any(t.dep_ in ("dobj", "pobj", "attr", "appos") for t in token.children)
                ]

                # Add edges with provenance + evidence
                for s in subj:
                    for o in obj:
                        if s != o:
                            evidence_sentence = find_sentence(full_text, s, o)

                            # Clean values so GEXF accepts them
                            safe_relation = token.lemma_ or ""
                            safe_doc_id = doc_id or ""
                            safe_doc_name = doc_name or ""
                            safe_evidence = evidence_sentence or ""

                            G.add_edge(
                                s, o,
                                relation=safe_relation,
                                relation_type="verb_dependency",
                                source_doc=int(source_doc),   
                                doc_id=safe_doc_id,
                                doc_name=safe_doc_name,
                                evidence=safe_evidence
                            )


# === 7. Save Graph ===
output_file_name = "ai_policy_kg_with_dependencies_4.gexf"
nx.write_gexf(G, output_file_name)

print(f"\nFinished building graph.")
print(f"Total nodes: {len(G.nodes)}, Total edges: {len(G.edges)}")
print(f"Saved graph as {output_file_name}")
print("You can view it at https://lite.gephi.org/v1.0.0/#/")

# === Print all node-edge-node triples with provenance ===
print("\n=== All Extracted Relations ===")
for u, v, data in G.edges(data=True):
    rel = data.get("relation", "")
    src = data.get("doc_id", "")
    title = data.get("doc_name", "")
    print(f"[{src} – {title}]  {u} --[{rel}]--> {v}")
