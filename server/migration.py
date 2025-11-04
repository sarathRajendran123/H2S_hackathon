import os
from dotenv import load_dotenv
from google.cloud import firestore
from sentence_transformers import SentenceTransformer
import google.auth
from google.cloud import firestore

credentials, project_id = google.auth.default()

db = firestore.Client(project='gen-ai-h2s-project')

# -----------------------------
# LAZY LOAD EMBEDDING MODEL
# -----------------------------
EMBED_MODEL = None

def get_embed_model():
    """Lazy load model only when embedding is needed."""
    global EMBED_MODEL
    if EMBED_MODEL is None:
        print("🔹 Loading MiniLM model for migration...")
        EMBED_MODEL = SentenceTransformer("./models/all-MiniLM-L6-v2")  # ✅ Use pre-bundled model path
        print("✅ Model loaded.")
    return EMBED_MODEL


def generate_embedding(text: str) -> list:
    normalized = text.lower().strip()
    model = get_embed_model()
    return model.encode(normalized).tolist()


def migrate_embeddings():
    """Batch update existing articles with embeddings."""
    docs = db.collection("articles").stream()
    batch = db.batch()
    updated_count = 0

    for doc in docs:
        data = doc.to_dict()
        updates = {}

        # Only add embeddings where missing
        if "embedding" not in data:
            if "text" in data and data["text"].strip():
                updates["embedding"] = generate_embedding(data["text"])

        # Mark as verified (this is your original behavior)
        updates["verified"] = True

        if updates:
            batch.update(doc.reference, updates)
            updated_count += 1
            print(f"✅ Updated {doc.id} with new embedding and verified=True.")
        else:
            print(f"⏭ No update needed for {doc.id}.")

    if updated_count > 0:
        batch.commit()
        print(f"🎉 Migration complete — updated {updated_count} documents.")
    else:
        print("✅ No documents required migration.")


if __name__ == "__main__":
    migrate_embeddings()