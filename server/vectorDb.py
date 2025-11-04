import hashlib
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone, ServerlessSpec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os
from typing import Optional

# -----------------------------
# CONFIGURATION & GLOBALS
# -----------------------------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API")
INDEX_NAME = "fact-check-cache"
NAMESPACE = "default"
VERIFIED_NAMESPACE = "verified_fakes"

# Lazy-loaded globals
EMBED_MODEL = None
pc = None
index = None


# -----------------------------
# LAZY LOADERS
# -----------------------------
def get_embed_model():
    """Lazy load the MiniLM embedding model AFTER app startup."""
    global EMBED_MODEL
    if EMBED_MODEL is None:
        print("🔹 Loading MiniLM embedder (lazy load)...")
        EMBED_MODEL = SentenceTransformer("./models/all-MiniLM-L6-v2")
        print("✅ MiniLM Loaded")
    return EMBED_MODEL


def init_pinecone():
    """Lazy init Pinecone to avoid Cloud Run cold start failures."""
    global pc, index

    if pc is None:
        if not PINECONE_API_KEY:
            raise RuntimeError("❌ Missing env var: PINECONE_API")

        print("🔹 Initializing Pinecone client...")
        pc = Pinecone(api_key=PINECONE_API_KEY)

    if index is None:
        print("🔹 Checking Pinecone index...")
        existing = [i["name"] for i in pc.list_indexes()]  # <== moved inside init

        if INDEX_NAME not in existing:
            print(f"🟢 Creating Pinecone index '{INDEX_NAME}'...")
            pc.create_index(
                name=INDEX_NAME,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        index = pc.Index(INDEX_NAME)
        print(f"✅ Connected to Pinecone index '{INDEX_NAME}'")

    return index


# -----------------------------
# HELPERS
# -----------------------------
def embed_text(text: str) -> list:
    model = get_embed_model()
    normalized = text.lower().strip()
    return model.encode(normalized).tolist()


def anon_user_id(fingerprint: str) -> str:
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(fingerprint.encode())
    return digest.finalize().hex()[:16]


def text_hash(text: str, url: Optional[str] = None) -> str:
    return hashlib.sha256(((url or "") + text).encode()).hexdigest()


# -----------------------------
# SEARCH FUNCTIONS
# -----------------------------
def search_feedback(text: str, article_id: Optional[str] = None) -> dict:
    if not text.strip():
        return {"error": "No text provided"}

    index = init_pinecone()
    vec_id = article_id or text_hash(text)
    vector = embed_text(text)

    exact_match = index.fetch(ids=[vec_id], namespace=NAMESPACE)
    if exact_match.vectors:
        metadata = exact_match.vectors[vec_id].metadata
        if metadata.get("unique_user_count", 0) >= 1:
            return {
                "score": metadata.get("score", 0.5),
                "explanation": metadata.get("explanation", ""),
                "details": [{"prediction": metadata.get("prediction", "Unknown")}],
                "source": "cache",
                "text": metadata.get("text", text),
                "article_id": article_id,
            }

    query_filter = {"unique_user_count": {"$gte": 1}}
    if article_id:
        query_filter["article_id"] = {"$eq": article_id}

    similar_results = index.query(
        vector=vector,
        top_k=1,
        include_metadata=True,
        namespace=NAMESPACE,
        filter=query_filter,
    )

    if similar_results.matches and similar_results.matches[0].score > 0.85:
        metadata = similar_results.matches[0].metadata
        return {
            "score": metadata.get("score", 0.5),
            "explanation": metadata.get("explanation", ""),
            "details": [{"prediction": metadata.get("prediction", "Unknown")}],
            "source": "cache",
            "text": metadata.get("text", text),
            "article_id": article_id,
        }

    return {"status": "no_reliable_match"}


def search_feedback_semantic(
    text: str, article_id: Optional[str] = None, verified_only: bool = False
) -> dict:
    if not text.strip():
        return {"error": "No text provided"}

    index = init_pinecone()
    vector = embed_text(text)
    namespace = VERIFIED_NAMESPACE if verified_only else NAMESPACE
    query_filter = {"verified": {"$eq": True}} if not verified_only else {}

    if article_id:
        query_filter["article_id"] = {"$eq": article_id}

    similar_results = index.query(
        vector=vector,
        top_k=10,
        include_metadata=True,
        namespace=namespace,
        filter=query_filter,
    )

    if similar_results.matches:
        best = max(
            (m for m in similar_results.matches if m.score > 0.75),
            key=lambda m: m.score,
            default=None,
        )

        if best:
            metadata = best.metadata
            return {
                "score": metadata.get("score", 0.5),
                "explanation": metadata.get("explanation", ""),
                "prediction": metadata.get("prediction", "Unknown"),
                "text": metadata.get("text", text),
                "article_id": metadata.get("article_id"),
                "source": "cache",
                "similarity": best.score,
                "details": [{"prediction": metadata.get("prediction", "Unknown")}],
            }

    return {"status": "no_reliable_match"}


# -----------------------------
# STORE USER FEEDBACK
# -----------------------------
def store_feedback(
    text: str,
    explanation: str,
    sources: list,
    user_fingerprint: str,
    article_id: Optional[str] = None,
    score: float = 0.5,
    prediction: str = "Unknown",
    verified: bool = True,
) -> dict:
    if not text.strip() or not explanation:
        return {"error": "Missing text or explanation"}

    index = init_pinecone()
    vector = embed_text(text)
    vec_id = article_id or text_hash(text)
    anon_id = anon_user_id(user_fingerprint)
    timestamp = datetime.utcnow().isoformat()
    namespace = VERIFIED_NAMESPACE if verified else NAMESPACE

    existing = index.fetch(ids=[vec_id], namespace=namespace)

    metadata = {
        "article_id": article_id or vec_id,
        "text_hash": vec_id,
        "text": text[:1000],
        "explanation": explanation[:2000],
        "sources": sources,
        "score": score,
        "prediction": prediction,
        "verified": verified,
        "timestamp": timestamp,
        "ttl_expiry": (datetime.utcnow() + timedelta(days=15)).isoformat(),
        "confirmations": 1,
        "unique_users": [anon_id],
        "unique_user_count": 1,
    }

    if existing.vectors:
        old = existing.vectors[vec_id].metadata
        metadata.update({
            "score": (old.get("score", 0.5) + score) / 2,
            "confirmations": old.get("confirmations", 0) + 1,
            "unique_users": list(set(old.get("unique_users", []) + [anon_id])),
            "unique_user_count": len(list(set(old.get("unique_users", []) + [anon_id]))),
            "prediction": prediction if prediction != "Unknown" else old.get("prediction"),
            "verified": verified or old.get("verified", False),
        })

    index.upsert(
        vectors=[{"id": vec_id, "values": vector, "metadata": metadata}],
        namespace=namespace,
    )
    return {"status": "stored", "article_id": article_id}


# -----------------------------
# CLEANUP EXPIRED VECTORS
# -----------------------------
def cleanup_expired(days: int = 15) -> dict:
    index = init_pinecone()
    now = datetime.utcnow()
    deleted_total = 0

    for ns in [NAMESPACE, VERIFIED_NAMESPACE]:
        try:
            results = index.query(
                vector=[0] * 384,
                top_k=1000,
                include_metadata=True,
                filter={"ttl_expiry": {"$lt": now.isoformat()}},
                namespace=ns,
            )
            expired = [m.id for m in results.matches]
            if expired:
                index.delete(ids=expired, namespace=ns)
                deleted_total += len(expired)
                print(f"[Cleanup] Deleted {len(expired)} expired vectors from {ns}")
        except Exception as e:
            print(f"[Cleanup Error in {ns}] {e}")

    return {"status": "success", "deleted": deleted_total}