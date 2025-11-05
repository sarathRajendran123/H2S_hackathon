import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional
import google.auth
from google.cloud import firestore

from google.cloud import firestore
from sentence_transformers import util

from embedding_service import get_embedding  
credentials, project_id = google.auth.default()
db = firestore.Client(project=project_id)  

# ---------------- Utility Helpers -----------------

# ----------------- Utility Helpers -----------------

def generate_embedding(text: str) -> list:
    """Generate embedding as a Python list"""
    emb = get_embedding(text)           
    return emb.tolist()                   


def generate_id(url, text):
    """Generate unique ID for (url + text) combination"""
    content = (url + text).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def normalize_text(text: str) -> str:
    """Lowercase + remove symbols + collapse spaces"""
    normalized = re.sub(r"[^\w\s]", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized.strip())
    return normalized


def generate_normalized_id(url: str, text: str) -> str:
    """Generate stable ID (ignoring punctuation & formatting)"""
    norm_url = url.lower() if url else ""
    norm_text = normalize_text(text)
    content = (norm_url + norm_text).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def get_article_doc(article_id):
    """Fetch existing article from Firestore"""
    doc = db.collection("articles").document(article_id).get()
    return doc.to_dict() if doc.exists else None


# ----------------- Semantic Search in Firestore -----------------

def firestore_semantic_search(
    text: str,
    min_similarity: float = 0.90,
    days_back: int = 30
) -> Optional[dict]:

    if not text.strip():
        return None

    cutoff = datetime.utcnow() - timedelta(days=days_back)

    query = (
        db.collection("articles")
          .where("last_updated", ">=", cutoff)
          .limit(50)
          .stream()
    )

    query_emb = get_embedding(text) 
    candidates = []

    for doc in query:
        data = doc.to_dict()
        if "embedding" in data and data.get("text"):
            stored_emb = data["embedding"]    # list
            similarity = util.cos_sim(query_emb, stored_emb)[0][0].item()

            if similarity > min_similarity:
                candidates.append({
                    "doc": data,
                    "id": doc.id,
                    "similarity": similarity
                })

    if candidates:
        best = max(
            candidates,
            key=lambda c: (c["similarity"], c["doc"].get("text_score", 0))
        )

        print(f"📌 Firestore semantic match: sim={best['similarity']:.3f}")
        return {
            "best": best["doc"],
            "best_id": best["id"],
            "similarity": best["similarity"]
        }

    print("ℹ️ No Firestore semantic match")
    return None