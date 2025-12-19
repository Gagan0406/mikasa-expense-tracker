import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

POLICY_DIR = "./policies"
DB_DIR = "./vectorstore/policies"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# -----------------------
# LOAD FILES
# -----------------------
def load_policy_files():
    docs = []
    for filename in os.listdir(POLICY_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(POLICY_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                docs.append({"source": filename, "content": f.read()})
    return docs


# -----------------------
# CHUNKING
# -----------------------
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["###", "---", "\n\n", "\n", ".", " "]
    )

    chunks = []
    for doc in docs:
        parts = splitter.split_text(doc["content"])
        for p in parts:
            chunks.append({"content": p, "source": doc["source"]})
    return chunks


# -----------------------
# EMBEDDINGS
# -----------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# TEST embedding before continuing
print("🔍 Testing embedding model...")
test_vec = embedding_model.embed_query("hello world")
print("Embedding length:", len(test_vec))
if len(test_vec) == 0:
    raise RuntimeError("❌ HuggingFace embedding model returned EMPTY VECTORS!")


# -----------------------
# STORE IN CHROMA
# -----------------------
def store_embeddings(chunks):
    texts = [c["content"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    print("Total texts:", len(texts))
    print("Total metadatas:", len(metadatas))

    if len(texts) == 0:
        raise ValueError("❌ No chunks found. Your input files might be empty or chunking failed.")

    Chroma.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory=DB_DIR
    )

    print("🎉 Successfully saved embeddings to:", DB_DIR)


# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    docs = load_policy_files()
    print("Loaded files:", len(docs))

    chunks = chunk_documents(docs)
    print("Generated chunks:", len(chunks))

    store_embeddings(chunks)
