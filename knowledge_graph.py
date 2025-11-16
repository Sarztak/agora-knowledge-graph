import spacy
import json
import networkx as nx
from tqdm import tqdm
import pandas as pd
import os
from collections import defaultdict
from entity_remapping import * 

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

# preload metadata
doc_meta = {}
for idx, row in df.iterrows():
    doc_index = idx + 1
    doc_meta[doc_index] = {
        "doc_id": row.get("doc_id", f"doc_{doc_index:03d}"),
        "doc_name": row.get("Official name", None),
        "text": row.get("Normalized Long Summary", "")
    }


# Helper: extract evidence sentence
def find_sentence(text, ent1, ent2):
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

with open("ner_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Finished processing {len(df)} documents. Saved ner_results.json.")


# === 5. Knowledge Graph Construction ===

# APPLIED category/verb/entity COLLAPSE and normalization here

print("\n=== Building Knowledge Graph ===")
nlp = spacy.load("en_core_web_md", disable=["ner"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

with open("ner_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

G = nx.DiGraph()

# Helper
def find_entities_in_sentence(entities, sent_text):
    return [ent for ent in entities if ent in sent_text]


for item in tqdm(data, desc="Extracting relations"):
    text = item["text"]

    raw_entities = {e["text"]: e["label"] for e in item["entities"]}
    entities = {}

    for ent_text, ent_label in raw_entities.items():
        clean_text = entity_map.get(ent_text, ent_text)
        clean_label = label_map.get(ent_label, ent_label)
        entities[clean_text] = clean_label

    doc = nlp(text)

    source_doc = item["index"]
    meta = doc_meta.get(source_doc, {})
    doc_id = meta["doc_id"]
    doc_name = meta["doc_name"]
    full_text = meta["text"]

    # === Add nodes ===
    clean_doc_id = int(str(doc_id).replace("doc_", ""))

    for ent_text, ent_label in entities.items():
        G.add_node(
            ent_text,
            label=ent_label,
            source_doc_id=clean_doc_id
        )


    # === Add edges ===
    for sent in doc.sents:
        sent_entities = find_entities_in_sentence(entities.keys(), sent.text)

        for token in sent:
            if token.pos_ == "VERB":

                raw_lemma = token.lemma_
                collapsed_verb = verb_map.get(raw_lemma, raw_lemma)

                subj = [
                    ent for ent in sent_entities
                    if any(child.dep_ in ("nsubj", "nsubjpass") for child in token.children)
                ]

                obj = [
                    ent for ent in sent_entities
                    if any(child.dep_ in ("dobj", "pobj", "attr", "appos") for child in token.children)
                ]

                for s in subj:
                    for o in obj:
                        if s != o:
                            evidence = find_sentence(full_text, s, o)
                            G.add_edge(
                                s, o,
                                relation=collapsed_verb,
                                relation_type="verb_dependency",
                                source_doc=source_doc,
                                doc_id=doc_id,
                                doc_name=doc_name,
                                evidence=evidence or ""
                            )


# === 6. Save GEXF ===
output_file_name = "ai_policy_kg_with_dependencies_collapsed_5.gexf"
nx.write_gexf(G, output_file_name)

print("\nFinished building graph.")
print(f"Total nodes: {len(G.nodes)}, Total edges: {len(G.edges)}")
print(f"Graph saved as {output_file_name}")


# === 7. CSV EXPORTS===
print("\n=== Generating nodes_ug.csv and edges_ug.csv ===")

# Node IDs
node_list = list(G.nodes())
node_to_id = {node: idx for idx, node in enumerate(node_list)}

# NODES CSV 

nodes_rows = []
for node, idx in node_to_id.items():
    data = G.nodes[node]
    category = data.get("label", "")

    doc_final = data.get("source_doc_id", -1)

    nodes_rows.append({
        "name": node,
        "category": category,
        "doc_id": doc_final,
        "id": idx
    })

nodes_df = pd.DataFrame(nodes_rows)
nodes_df.to_csv("./output/nodes_ug.csv", index=False)
print("Saved ./output/nodes_ug.csv")

# EDGES CSV
edges_rows = []
for u, v, ed in G.edges(data=True):

    raw_doc_id = ed.get("doc_id", "")
    if isinstance(raw_doc_id, str):
        raw_doc_id = raw_doc_id.replace("doc_", "")

    try:
        doc_id_int = int(raw_doc_id)
    except (TypeError, ValueError):
        doc_id_int = -1

    edges_rows.append({
        "source": node_to_id[u],
        "target": node_to_id[v],
        "verb": ed.get("relation", ""),
        "name": ed.get("relation", "").upper(),
        "doc_id": doc_id_int
    })

edges_df = pd.DataFrame(edges_rows)
edges_df.to_csv("./output/edges_ug.csv", index=False)
print("Saved ./output/edges_ug.csv")


"""
# Print all node-edge-node triples with provenance
print("\n=== All Extracted Relations ===")
for u, v, data in G.edges(data=True):
    rel = data.get("relation", "")
    src = data.get("doc_id", "")
    title = data.get("doc_name", "")
    print(f"[{src} – {title}]  {u} --[{rel}]--> {v}")

"""