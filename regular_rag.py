from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

print("[Import] done")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,
    separators=["\n\n", "\n", " ", ""]
)

df = pd.read_csv("data/documents_normalized.csv")

chunk_records = []
for _, row in df.iterrows():
    doc_id = row["doc_id"]
    title = row["Official name"]
    content = row["Long summary"]
    chunks = splitter.split_text(content)
    for chunk_id, chunk_text in enumerate(chunks):
        chunk_records.append({
            "doc_id": doc_id,
            "title": title,
            "chunk_id": chunk_id,
            "chunk_uid": f"{doc_id}_{chunk_id}",
            "chunk_text": chunk_text
        })

chunks_df = pd.DataFrame(chunk_records)

print("Total chunks generated:", len(chunks_df))
print("Average chunks per document:", chunks_df.groupby("doc_id").size().mean())
print(chunks_df.tail())

load_dotenv()
hf_token = os.getenv("HF_TOKEN")
embedder = SentenceTransformer("google/embeddinggemma-300m", use_auth_token=hf_token)

chroma_client = chromadb.PersistentClient(path="./agora_chroma_db")

try:
    chroma_client.delete_collection("news_chunks")
    print("Deleted old collection.")
except:
    print("No old collection found.")

collection = chroma_client.create_collection(
    name="news_chunks",
    metadata={"hnsw:space": "cosine"},
    embedding_function=None
)

ids = chunks_df["chunk_uid"].tolist()
documents = chunks_df["chunk_text"].tolist()
metadatas = chunks_df[["doc_id", "title", "chunk_id"]].to_dict(orient="records")

embeddings = embedder.encode(documents, show_progress_bar=True).tolist()

BATCH_SIZE = 500
for i in range(0, len(documents), BATCH_SIZE):
    batch_ids = ids[i:i+BATCH_SIZE]
    batch_docs = documents[i:i+BATCH_SIZE]
    batch_meta = metadatas[i:i+BATCH_SIZE]
    batch_emb = embeddings[i:i+BATCH_SIZE]
    print(f"Inserting batch {i} → {i+len(batch_ids)}")
    collection.add(
        ids=batch_ids,
        documents=batch_docs,
        metadatas=batch_meta,
        embeddings=batch_emb
    )
