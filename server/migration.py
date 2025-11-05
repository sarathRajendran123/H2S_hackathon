import os
from dotenv import load_dotenv
import google.auth
from google.cloud import firestore
from embedding_service import get_embedding  

load_dotenv()

# -----------------------------
# FIRESTORE CONFIG
# -----------------------------
credentials, project_id = google.auth.default()
db = firestore.Client(project=project_id)  

# -----------------------------
# GENERATE EMBEDDING (uses shared model)
# -----------------------------
def generate_embedding(text: str) -> list:
    """Generate embedding using global shared model from app.py."""
    return get_embedding(text).tolist() 


# -----------------------------
# MIGRATION SCRIPT
# -----------------------------
def migrate_embeddings():
    """Add missing embeddings & verified flag to Firestore documents."""
    docs = db.collection("articles").stream()
    batch = db.batch()
    updated_count = 0

    for doc in docs:
        data = doc.to_dict()
        updates = {}

        if "embedding" not in data and data.get("text"):
            updates["embedding"] = generate_embedding(data["text"])

        updates["verified"] = True

        if updates:
            batch.update(doc.reference, updates)
            updated_count += 1
            print(f"✅ Updated {doc.id} (embedding + verified=True)")
        else:
            print(f"⏭ No update needed for {doc.id}")

    if updated_count > 0:
        batch.commit()
        print(f"🎉 Migration complete — updated {updated_count} documents.")
    else:
        print("✅ No documents needed migration.")


if __name__ == "__main__":
    migrate_embeddings()
