# embedding_service.py
from functools import lru_cache
from sentence_transformers import SentenceTransformer

EMBED_MODEL = None

def get_embed_model():
    global EMBED_MODEL
    if EMBED_MODEL is None:
        print("🔹 Loading MiniLM model...")
        EMBED_MODEL = SentenceTransformer("./models/all-MiniLM-L6-v2", device="cpu")
    return EMBED_MODEL

@lru_cache(maxsize=8192)
def get_embedding(text: str):
    return get_embed_model().encode(text, convert_to_tensor=True)

def embed_text(text: str) -> list:
    return get_embed_model().encode(text, convert_to_tensor=False).tolist()