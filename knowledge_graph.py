import spacy
import json
import networkx as nx

# Load English model (medium or large recommended)
nlp = spacy.load("en_core_web_md")

# Load NER results
with open("ner_results.json") as f:
    data = json.load(f)

G = nx.DiGraph()

counter = 0
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
                    if counter == 1:
                        print("token lemma:\n")
                        print(token.lemma_)
                        print("\n")
            counter += 1

nx.write_gexf(G, "ai_policy_kg_with_dependencies.gexf")
