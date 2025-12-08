import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
st.set_page_config(layout="wide")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

embedder = SentenceTransformer(
    "google/embeddinggemma-300m",
    device="cpu",
    use_auth_token=os.getenv("HF_TOKEN")
)

chroma_client = chromadb.PersistentClient(path="./agora_chroma_db")
collection = chroma_client.get_collection("news_chunks")

st.title("AGORA RAG Search")

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
