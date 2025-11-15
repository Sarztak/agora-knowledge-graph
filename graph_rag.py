import networkx as nx
import spacy
from rapidfuzz import fuzz
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
from dotenv import load_dotenv

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
# 6. Hybrid Retrieval (Semantic + Fuzzy)
# ================================================================
def hybrid_node_retrieval(query, graph, ents, embed_model):
    hybrid_scores = {}

    # FUZZY
    for e in ents:
        for node, score in fuzzy_match_nodes(e, graph):
            hybrid_scores[node] = hybrid_scores.get(node, 0) + 0.30 * (score / 100.0)

    # SEMANTIC
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
# 7. DIRECT Triple Extraction (NOT graph hop expansion)
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
# 8. Triple-level semantic scoring
# ================================================================
def score_triple(query: str, triple: dict, embed_model):
    text = f"{triple['source']} {triple['relation']} {triple['target']}"
    q_emb = embed_model.encode(query)
    t_emb = embed_model.encode(text)
    return cosine_similarity([q_emb], [t_emb])[0][0]


# ================================================================
# 9. Build LLM context
# ================================================================
def build_context_for_llm(query: str, triples, top_n_docs=3):
    grouped = {}
    for t in triples:
        key = (t["doc_id"], t["doc_name"])
        grouped.setdefault(key, []).append(t)

    # Score documents by number of high-relevance triples
    scored_docs = [(key, len(vals)) for key, vals in grouped.items()]
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    top_docs = scored_docs[:top_n_docs]

    lines = []
    for (doc_id, doc_name), score in top_docs:
        lines.append(f"[{doc_id} – {doc_name}]")
        for t in grouped[(doc_id, doc_name)]:
            lines.append(f"{t['source']} --[{t['relation']}]--> {t['target']}")
        lines.append("")

    graph_block = "\n".join(lines)

    final_prompt = f"""
User Query:
{query}

Top {top_n_docs} Most Relevant Documents (Filtered Triples):
---------------------------------------------------------------
{graph_block}

Using ONLY the above structured evidence, provide a factual, well-structured answer.
"""
    return final_prompt


# ================================================================
# 10. Main Graph-RAG Entry
# ================================================================
def graph_rag_answer(query: str, graph: nx.DiGraph, ner_nlp, embed_model):
    print(f"\n[GraphRAG] Query: {query}")

    ents = extract_query_entities(query, ner_nlp)
    print(f"[GraphRAG] Entities: {ents}")

    seed_nodes = hybrid_node_retrieval(query, graph, ents, embed_model)
    print(f"[GraphRAG] Seed nodes: {seed_nodes}")

    if not seed_nodes:
        return "No relevant graph nodes found."

    # DIRECT triple extraction
    all_triples = get_direct_triples(graph, seed_nodes)

    # Semantic filtering
    relevant = []
    for t in all_triples:
        sim = score_triple(query, t, embed_model)
        if sim >= 0.50:
            t["score"] = sim
            relevant.append(t)

    relevant.sort(key=lambda x: x["score"], reverse=True)
    relevant = relevant[:30]  
    return build_context_for_llm(query, relevant, top_n_docs=3)


# ================================================================
# 11. LLM Call
# ================================================================
def llm_answer_from_context(context: str, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "You are an AI policy expert using a knowledge graph. Use ONLY the evidence."},
            {"role": "user", "content": context}
        ],
        temperature=0.2,
        max_tokens=400
    )
    return response.choices[0].message.content


# ================================================================
# 12. CLI 
# ================================================================
if __name__ == "__main__":
    graph = load_graph("ai_policy_kg_with_dependencies_4.gexf")
    embed_model = build_node_embeddings(graph)
    ner_nlp = load_query_ner()

    while True:
        user_query = input("\nEnter your policy question (or 'quit'): ")
        if user_query.lower() == "quit":
            break

        context = graph_rag_answer(user_query, graph, ner_nlp, embed_model)

        print("\n================= GRAPH RAG CONTEXT =================")
        print(context)
        print("=====================================================\n")

        answer = llm_answer_from_context(context)

        print("\n================ LLM ANSWER =================")
        print(answer)
        print("=============================================\n")
