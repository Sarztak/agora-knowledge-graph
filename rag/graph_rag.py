import networkx as nx
import spacy
from rapidfuzz import fuzz
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
from dotenv import load_dotenv
import pandas as pd

# ================================================================
# Load credentials
# ================================================================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("DEBUG: Loaded API key =", api_key)
client = OpenAI(api_key=api_key)


# ================================================================
# 1. Load graph
# ================================================================
def load_graph(gexf_path: str):
    print(f"[GraphRAG] Loading graph from {gexf_path}")
    return nx.read_gexf(gexf_path)


# ================================================================
# 2. Load embedding model & attach embeddings to nodes
# ================================================================
def build_node_embeddings(graph: nx.DiGraph, model_name="all-mpnet-base-v2"):
    print(f"[GraphRAG] Encoding {len(graph.nodes())} graph nodes using {model_name} ...")
    model = SentenceTransformer(model_name)

    node_texts = list(graph.nodes())
    embeddings = model.encode(node_texts, show_progress_bar=True)

    for node, emb in zip(node_texts, embeddings):
        graph.nodes[node]["embedding"] = emb.astype(np.float32)

    print("[GraphRAG] Embeddings attached to graph nodes.")
    return model


# ================================================================
# 3. Query Entity Extraction (EntityRuler patterns)
# ================================================================
def load_query_ner(pattern_json="./universal_pattern_output/unique_entities_first_label.json"):
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")

    import json
    with open(pattern_json, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    ruler.add_patterns(patterns)
    return nlp


def extract_query_entities(query: str, nlp):
    doc = nlp(query)
    return list({ent.text for ent in doc.ents})


# ================================================================
# 4. Fuzzy Graph Node Retrieval
# ================================================================
def fuzzy_match_nodes(entity: str, graph: nx.DiGraph, threshold=80):
    matches = []
    for node in graph.nodes:
        score = fuzz.partial_ratio(entity.lower(), node.lower())
        if score >= threshold:
            matches.append((node, score))
    return matches


# ================================================================
# 5. Semantic Node Retrieval
# ================================================================
def semantic_search_nodes(query: str, graph: nx.DiGraph, embed_model, threshold=0.60, top_k=10):
    query_vec = embed_model.encode(query)

    sims = []
    for node, data in graph.nodes(data=True):
        emb = data.get("embedding")
        if emb is None:
            continue
        sim = cosine_similarity([query_vec], [emb])[0][0]
        if sim >= threshold:
            sims.append((node, sim))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:top_k]


# ================================================================
# 6. Hybrid Retrieval 
# ================================================================
def hybrid_node_retrieval(query, graph, ents, embed_model):
    hybrid_scores = {}

    # fuzzy
    for e in ents:
        for node, score in fuzzy_match_nodes(e, graph):
            hybrid_scores[node] = hybrid_scores.get(node, 0) + 0.30 * (score / 100.0)

    # semantic
    semantic_nodes = semantic_search_nodes(query, graph, embed_model, threshold=0.60, top_k=10)
    for node, score in semantic_nodes:
        hybrid_scores[node] = hybrid_scores.get(node, 0) + 0.70 * score

    if len(hybrid_scores) == 0:
        print("[GraphRAG] No semantic matches passed threshold. Using fuzzy only.")
        fallback = []
        for e in ents:
            fallback.extend([node for node, _ in fuzzy_match_nodes(e, graph)])
        return fallback[:5]

    sorted_nodes = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return [node for node, _ in sorted_nodes[:5]]


# ================================================================
# 7. Triple Extraction (direct neighbors only)
# ================================================================
def get_direct_triples(graph: nx.DiGraph, seed_nodes):
    triples = []

    for node in seed_nodes:
        # Outgoing edges
        for _, target, data in graph.out_edges(node, data=True):
            triples.append({
                "source": node,
                "relation": data.get("relation", ""),
                "target": target,
                **data
            })

        # Incoming edges
        for source, _, data in graph.in_edges(node, data=True):
            triples.append({
                "source": source,
                "relation": data.get("relation", ""),
                "target": node,
                **data
            })

    return triples


# ================================================================
# 8. Triple scoring
# ================================================================
def score_triple(query: str, triple: dict, embed_model):
    text = f"{triple['source']} {triple['relation']} {triple['target']}"
    q_emb = embed_model.encode(query)
    t_emb = embed_model.encode(text)
    return cosine_similarity([q_emb], [t_emb])[0][0]


# ================================================================
# 9. Build prompt for LLM
# ================================================================
docs_df = pd.read_csv("data/documents_normalized.csv")


def build_context_for_llm(query: str, triples, top_n_docs=3):

    grouped = {}
    for t in triples:
        key = (t["doc_id"], t["doc_name"])
        grouped.setdefault(key, []).append(t)

    scored_docs = [(key, len(vals)) for key, vals in grouped.items()]
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    top_docs = scored_docs[:top_n_docs]

    lines = []

    for (doc_id, doc_name), score in top_docs:
        lines.append(f"[{doc_id} – {doc_name}]")

        lines.append("Extracted Triples:")
        lines.append("-------------------")
        for triple in grouped[(doc_id, doc_name)]:
            lines.append(f"{triple['source']} --[{triple['relation']}]--> {triple['target']}")
        lines.append("")

    graph_block = "\n".join(lines)

    final_prompt = f"""
User Query:
{query}

Top {top_n_docs} Most Relevant Documents (Knowledge Graph Triples Only):
==========================================

{graph_block}

Using ONLY the above knowledge graph triples (nodes and edges),
provide a well-phrased answer. 
DO NOT bring in any outside information or original document content.
"""

    return final_prompt


# ================================================================
# 10. Document search AND Graph-RAG answer
# ================================================================

def get_all_triples_grouped_by_document(graph):
    grouped = {}
    for u, v, data in graph.edges(data=True):
        key = (data.get("doc_id"), data.get("doc_name"))
        triple = {
            "source": u,
            "relation": data.get("relation",""),
            "target": v,
            **data
        }
        grouped.setdefault(key, []).append(triple)
    return grouped


def print_document_details(doc_id, doc_name, triples):

    print(f"\n================ {doc_id} — {doc_name} ================\n")

    matches = docs_df[docs_df["doc_id"] == doc_id]
    if len(matches) > 0:
        text = matches["Normalized Long Summary"].iloc[0]
    else:
        text = "(Document not found)"

    print("DOCUMENT TEXT:")
    print("--------------")
    print(text)
    print("\n\nExtracted Triples:")
    print("------------------")

    if len(triples) == 0:
        print("(No triples extracted from this document.)")
    else:
        for t in triples:
            print(f"{t['source']} --[{t['relation']}]--> {t['target']}")

    print("\n=========================================================\n")


# ================================================================
# 11. Query entry point
# ================================================================
def graph_rag_answer(query: str, graph: nx.DiGraph, ner_nlp, embed_model):

    print(f"\n[GraphRAG] Query: {query}")

    ents = extract_query_entities(query, ner_nlp)
    print(f"[GraphRAG] Entities: {ents}")

    seed_nodes = hybrid_node_retrieval(query, graph, ents, embed_model)
    print(f"[GraphRAG] Seed nodes: {seed_nodes}")

    if not seed_nodes:
        return "No relevant graph nodes found."

    triples = get_direct_triples(graph, seed_nodes)

    relevant = []
    for t in triples:
        sim = score_triple(query, t, embed_model)
        if sim >= 0.50:
            t["score"] = sim
            relevant.append(t)

    relevant.sort(key=lambda x: x["score"], reverse=True)
    relevant = relevant[:30]

    return build_context_for_llm(query, relevant, top_n_docs=3)


# ================================================================
# 12. LLM call
# ================================================================
def llm_answer_from_context(context: str, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "You are an AI policy expert using a knowledge graph. Use ONLY the evidence. Be concise and clear."},
            {"role": "user", "content": context}
        ],
        temperature=0.2,
        max_tokens=400
    )
    return response.choices[0].message.content


# ================================================================
# 13. CLI with both modes
# ================================================================
if __name__ == "__main__":
    graph = load_graph("ai_policy_kg_with_dependencies_children.gexf")
    embed_model = build_node_embeddings(graph)
    ner_nlp = load_query_ner()

    all_docs = get_all_triples_grouped_by_document(graph)

    while True:
        print("\nChoose an option:")
        print("1 = Ask a policy question (Graph-RAG QA)")
        print("2 = Inspect a document")
        print("quit = Exit")
        mode = input("Enter choice: ").strip().lower()

        if mode == "quit":
            break

        # Graph-RAG QA
        if mode == "1":
            q = input("\nEnter your policy question: ").strip()
            context = graph_rag_answer(q, graph, ner_nlp, embed_model)
            print("\n================= GRAPH RAG CONTEXT =================")
            print(context)
            print("=====================================================\n")

            answer = llm_answer_from_context(context)
            print("\n================ LLM ANSWER =================")
            print(answer)
            print("=============================================\n")

        # Document inspection
        elif mode == "2":
            print("\nAvailable documents:")
            for (doc_id, doc_name) in all_docs.keys():
                print(f"- {doc_id}: {doc_name}")

            chosen = input("\nEnter doc_id exactly (like doc_594): ").strip()

            found = False
            for (doc_id, doc_name), triples in all_docs.items():
                if doc_id == chosen:
                    print_document_details(doc_id, doc_name, triples)
                    found = True
                    break

            if not found:
                print("Document not found.")

        else:
            print("Invalid option.")
