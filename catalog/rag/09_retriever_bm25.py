"""RAG 09 — BM25 Retriever (키워드 기반)

- Vector search(임베딩)만으로는 특정 키워드/고유명사에 약할 수 있음
- BM25는 전통적인 키워드 검색으로 이를 보완

학습 포인트:
- BM25Retriever
- (확장) EnsembleRetriever로 BM25 + Vector를 합칠 수 있음
"""
from rich import print
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import settings
from app.core.rag_utils import load_documents
from app.utils.console import header

def main():
    header("RAG 09 — BM25 Retriever")
    docs = load_documents(settings.DOCS_DIR)
    if not docs:
        print("[yellow]data/docs에 문서를 넣어주세요.[/yellow]")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)

    retriever = BM25Retriever.from_documents(chunks)
    retriever.k = settings.TOP_K

    q = "관객개발 KPI"
    hits = retriever.get_relevant_documents(q)
    print(f"hits: {len(hits)}")
    for i, d in enumerate(hits, 1):
        print(f"--- {i} ---")
        print(d.page_content[:220])

if __name__ == "__main__":
    main()
