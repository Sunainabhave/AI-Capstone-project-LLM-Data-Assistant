import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from google.generativeai import embedding as embedding_api
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ✅ Set up Qdrant
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False
)

COLLECTION_NAME = "unstructured_chunks"

# ✅ Set up Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Use the correct model (NOT gemini-pro)
llm_model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-1.5-pro" if needed


# ✅ Create collection (if not already created)
qdrant.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Gemini embeddings = 768
)


# ✅ Correct way to embed text using Gemini
def embed_text(text: str):
    try:
        res = embedding_api.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return res["embedding"]
    except Exception as e:
        print("❌ Embedding failed:", e)
        return []


def add_to_qdrant(chunks):
    points = []
    for chunk in chunks:
        vector = embed_text(chunk)
        if vector:
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": chunk}
            ))
    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)


def search_qdrant(query: str, top_k=3):
    q_vector = embed_text(query)
    results = qdrant.search(collection_name=COLLECTION_NAME, query_vector=q_vector, limit=top_k)
    matched_chunks = [r.payload["text"] for r in results]

    # ✅ Use Gemini LLM to summarize matched content
    prompt = f"""
Use the following context to answer the user's question.

Context:
{" ".join(matched_chunks)}

Question: {query}

Answer:"""

    response = llm_model.generate_content(prompt)
    return {
        "answer": response.text,
        "matched_chunks": matched_chunks
    }
