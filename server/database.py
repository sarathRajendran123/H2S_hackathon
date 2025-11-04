import hashlib
import re
from google.cloud import firestore
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json
from typing import Optional
from sentence_transformers import util
import google.auth
from google.cloud import firestore

db = firestore.Client(project='gen-ai-h2s-project')

credentials, project_id = google.auth.default()

EMBED_MODEL = None

def get_embed_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        EMBED_MODEL = SentenceTransformer("./models/all-MiniLM-L6-v2")
    return EMBED_MODEL

def generate_embedding(text: str) -> list:
    normalized = text.lower().strip()
    model = get_embed_model()
    return model.encode(normalized).tolist()

def generate_id(url, text):
    content = (url + text).encode("utf-8")
    return hashlib.sha256(content).hexdigest()

def normalize_text(text: str) -> str:
    normalized = re.sub(r"[^\w\s]", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized.strip())
    return normalized

def generate_normalized_id(url: str, text: str) -> str:
    norm_url = url.lower() if url else ""
    norm_text = normalize_text(text)
    content = (norm_url + norm_text).encode("utf-8")
    return hashlib.sha256(content).hexdigest()

def get_article_doc(article_id):
    doc_ref = db.collection("articles").document(article_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def firestore_semantic_search(text: str, min_similarity: float = 0.90, days_back: int = 30) -> Optional[dict]:
    if not text.strip():
        return None

    cutoff = datetime.utcnow() - timedelta(days=days_back)
    query = db.collection("articles").where("last_updated", ">=", cutoff).limit(50).stream()
    candidates = []
    query_embedding = generate_embedding(text)

    for doc in query:
        data = doc.to_dict()
        if "embedding" in data and data.get("text"):
            stored_emb = data["embedding"]
            similarity = util.cos_sim(query_embedding, stored_emb)[0][0].item()
            if similarity > min_similarity:
                candidates.append({
                    "doc": data,
                    "id": doc.id,
                    "similarity": similarity
                })

    if candidates:
        best = max(candidates, key=lambda c: (c["similarity"], c["doc"].get("text_score", 0)))
        print(f"Firestore semantic hit! Best sim: {best['similarity']:.3f} on {best['id']}")
        return {"best": best["doc"], "best_id": best["id"], "similarity": best["similarity"]}

    print("No Firestore semantic hit.")
    return None
