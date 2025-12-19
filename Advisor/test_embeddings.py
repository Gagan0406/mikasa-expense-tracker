import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

DB_DIR = "./vectorstore/policies"

# -------------------------
# Load embedding model
# -------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# -------------------------
# Load existing Chroma DB
# -------------------------
def load_vector_db():
    if not os.path.exists(DB_DIR):
        raise FileNotFoundError(f"❌ Vector DB not found at: {DB_DIR}")

    print("📦 Loading Chroma vector database...")
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embedding_model
    )
    print("✅ Vector DB Loaded!")
    return db


# -------------------------
# Search function
# -------------------------
def search_policies(query, k=5):
    db = load_vector_db()

    print(f"\n🔍 Searching for: {query}")
    results = db.similarity_search_with_score(query, k=k)

    print(f"\n📌 Top {k} Results:")
    for i, (doc, score) in enumerate(results):
        print("\n------------------------------")
        print(f"Result {i+1}")
        print(f"Similarity Score: {score:.4f}")
        print("Source File:", doc.metadata.get("source", "Unknown"))
        print("Content Preview:")
        print(doc.page_content[:300], "...")
    print("------------------------------\n")


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    # SAMPLE QUERIES — test all 3 types
    queries = [
        "affordable health policy for a 25 year old female",
        "low premium insurance for family protection",
        "government financial support scheme for farmers",
        "health insurance for senior citizens",
        "policy with good coverage and low monthly cost"
    ]

    for q in queries:
        search_policies(q, k=3)
