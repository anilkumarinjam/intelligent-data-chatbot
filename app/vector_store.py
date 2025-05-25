import os
import chromadb
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Create a persistent client
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="knowledge_base")

def get_embedding(text: str):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']

def add_knowledge(id: str, text: str):
    embedding = get_embedding(text)
    collection.add(
        documents=[text],
        metadatas=[{"source": "user_feedback"}],
        ids=[id],
        embeddings=[embedding]
    )

def query_knowledge(text: str, n_results=3):
    embedding = get_embedding(text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "distances"]
    )
    if results['documents'] and len(results['documents'][0]) > 0:
        return results['documents'][0]
    else:
        return []
