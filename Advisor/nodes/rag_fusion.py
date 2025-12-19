from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()

DB_DIR = "./vectorstore/policies"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embedding_model
)

def rag_fusion_node(state):
    queries = state["rewritten_queries"]

    seen_chunks = set()
    fused_context = []

    for q in queries:
        results = vector_db.similarity_search(q, k=4)
        for doc in results:
            if doc.page_content not in seen_chunks:
                seen_chunks.add(doc.page_content)
                fused_context.append(
                    f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
                )

    return {
        "rag_context": "\n\n".join(fused_context)
    }
