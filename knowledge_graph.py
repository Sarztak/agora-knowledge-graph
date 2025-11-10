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
df = pd.read_csv("/Users/blag/Documents/UChicago MS/2025 Fall/agora-knowledge-graph/data/documents_normalized.csv")
if "Normalized Long Summary" not in df.columns:
    raise ValueError("Could not find column 'Normalized Long Summary' in documents_normalized.csv")

# === 5. Apply NER to each document ===
results = []

# TODO: index error here
for i, text in enumerate(df["Normalized Long Summary"].fillna("")):
    doc = nlp(text)
    entities = [
        {"text": ent.text, "label": ent.label_}
        for ent in doc.ents
    ]
    results.append({
        "index": i+1,
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
import spacy
import json
import networkx as nx
from tqdm import tqdm

# disable NER to avoid interference
nlp = spacy.load("en_core_web_md", disable=["ner"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")

with open("ner_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

G = nx.DiGraph()

for item in tqdm(data, desc="Building graph"):
    text = item["text"]
    entities = {e["text"]: e["label"] for e in item["entities"]}
    doc = nlp(text)

    # Add all entities as nodes first
    for ent_text, ent_label in entities.items():
        G.add_node(ent_text, label=ent_label)

    # Verb-based relationships (exact match on entity)
    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":
                subj = [
                    desc.text for desc in token.subtree # instead of token.children
                    if desc.dep_ in ("nsubj", "nsubjpass")
                    and desc.text in entities
                ]
                obj = [
                    desc.text for desc in token.subtree # instead of token.children
                    if desc.dep_ in ("dobj", "pobj", "attr", "appos")
                    and desc.text in entities
                ]
                for s in subj:
                    for o in obj:
                        G.add_edge(
                            s, o,
                            relation=token.lemma_,
                            relation_type="verb_dependency",
                            source_doc=item["index"]
                        )

    # Adding co-occurence as another type of relationship
    # This is saved as output_file_name = "ai_policy_kg_with_dependencies_2.gexf"

    """
    for sent in doc.sents:
        sent_entities = [e for e in entities.keys() if e in sent.text]
        for i in range(len(sent_entities)):
            for j in range(i + 1, len(sent_entities)):
                s, o = sent_entities[i], sent_entities[j]
                if not G.has_edge(s, o):
                    G.add_edge(
                        s, o,
                        relation="cooccur",
                        relation_type="sentence_cooccurrence",
                        source_doc=item["index"]
                    )
    """

# === 5. Export graph ===
output_file_name = "ai_policy_kg_with_dependencies_3.gexf"
nx.write_gexf(G, output_file_name)
print(f"\nFinished building graph.")
print(f"Total nodes: {len(G.nodes)}, Total edges: {len(G.edges)}")
print(f"Saved graph as {output_file_name}")
print("You can view it at https://lite.gephi.org/v1.0.0/#/")
