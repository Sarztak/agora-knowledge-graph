import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

# Import Graph RAG functions
from graph_rag import (
    load_graph,
    build_node_embeddings,
    load_query_ner,
    graph_rag_answer,
    llm_answer_from_context
)

load_dotenv()
st.set_page_config(layout="wide")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Text RAG components
embedder = SentenceTransformer(
    "google/embeddinggemma-300m",
    device="cpu",
    use_auth_token=os.getenv("HF_TOKEN")
)

chroma_client = chromadb.PersistentClient(path="./agora_chroma_db")
collection = chroma_client.get_collection("news_chunks")

# Graph RAG components (cached)
@st.cache_resource
def load_graph_rag_components():
    """Load and cache Graph RAG components"""
    graph = load_graph("ai_policy_kg_with_dependencies_children.gexf")
    embed_model = build_node_embeddings(graph)
    ner_nlp = load_query_ner()
    return graph, embed_model, ner_nlp

st.title("AGORA RAG Search")

# RAG mode selection
rag_mode = st.radio("Select RAG Mode", ["Text RAG", "Graph RAG"], horizontal=True)

query = st.text_input("Enter your query")
top_k = st.slider("Top K", 1, 10, 5)

def retrieve_chunks(query_text, k):
    q_emb = embedder.encode([query_text])[0].tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=k)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    return list(zip(docs, metas))

def build_context(chunks):
    blocks = []
    for text, meta in chunks:
        blocks.append(f"[{meta['doc_id']} – {meta['title']} (chunk {meta['chunk_id']})]\n{text}\n")
    return "\n".join(blocks)

def ask_llm(query_text, context):
    prompt = f"""
Use the context to answer the query.

Context:
{context}

Query: {query_text}

Answer clearly and concisely.
"""
    resp = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

if st.button("Run"):
    if query.strip() == "":
        st.error("Enter a query.")
    else:
        if rag_mode == "Text RAG":
            # Text RAG path
            chunks = retrieve_chunks(query, top_k)
            context = build_context(chunks)
            answer = ask_llm(query, context)

            st.subheader("Answer")
            st.write(answer)

            st.subheader("Retrieved Chunks")
            for text, meta in chunks:
                st.markdown(f"**{meta['doc_id']} – {meta['title']} (chunk {meta['chunk_id']})**")
                st.write(text)
                st.markdown("---")
        
        else:  # Graph RAG
            with st.spinner("Loading Graph RAG components..."):
                graph, embed_model, ner_nlp = load_graph_rag_components()
            
            with st.spinner("Querying knowledge graph..."):
                context = graph_rag_answer(query, graph, ner_nlp, embed_model)
            
            with st.spinner("Generating answer..."):
                answer = llm_answer_from_context(context)
            
            st.subheader("Answer")
            st.write(answer)
            
            st.subheader("Graph RAG Context")
            with st.expander("View context sent to LLM"):
                st.text(context)
