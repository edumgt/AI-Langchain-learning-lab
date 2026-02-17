"""RAG 10 — Ensemble Retriever (BM25 + Vector)

학습 포인트:
- EnsembleRetriever로 키워드 기반(BM25)과 임베딩 기반(Vector) 결과를 결합
"""
from rich import print
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import settings
from app.core.rag_utils import load_documents, ingest_dir, vectorstore
from app.utils.console import header

def main():
    header("RAG 10 — Ensemble Retriever (BM25 + Chroma)")
    docs = load_documents(settings.DOCS_DIR)
    if not docs:
        print("[yellow]data/docs에 문서를 넣어주세요.[/yellow]")
        return

    # Vector (Chroma)
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vector_ret = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    # BM25
    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)
    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = settings.TOP_K

    ensemble = EnsembleRetriever(retrievers=[bm25, vector_ret], weights=[0.45, 0.55])
    q = "후원 제안서에 포함될 KPI와 혜택"
    hits = ensemble.get_relevant_documents(q)

    print(f"hits: {len(hits)}")
    for i, d in enumerate(hits, 1):
        print(f"--- {i} ---")
        print(d.page_content[:220])

if __name__ == "__main__":
    main()
