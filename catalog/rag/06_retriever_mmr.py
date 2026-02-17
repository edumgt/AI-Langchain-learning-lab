"""Retriever MMR 데모 (Chroma 기반).

MMR은 유사도 상위 문서들 중에서도 '다양성'을 확보해 중복을 줄이려는 전략입니다.
"""
from rich import print
from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.utils.console import header

def main():
    header("RAG 06 — MMR Retriever")
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": settings.TOP_K, "fetch_k": max(settings.TOP_K*4, 10)})
    q = "관객개발 KPI 설계 시 유의점"
    docs = retriever.get_relevant_documents(q)

    print(f"docs: {len(docs)}")
    for i, d in enumerate(docs, 1):
        print(f"--- {i} ---")
        print(d.page_content[:220])

if __name__ == "__main__":
    main()
