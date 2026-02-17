"""VectorStore: Chroma ingest & query."""
from rich import print
from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.utils.console import header

def main():
    header("RAG 03 — Chroma VectorStore")
    added = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    print("chunks_added:", added)

    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    res = vs.similarity_search("관객개발 KPI", k=3)
    print("hits:", len(res))
    for i, d in enumerate(res, 1):
        print(f"--- hit {i} ---")
        print(d.page_content[:200])

if __name__ == "__main__":
    main()
