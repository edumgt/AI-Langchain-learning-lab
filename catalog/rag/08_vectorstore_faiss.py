"""RAG 08 — FAISS VectorStore (비교용)

- Chroma와 달리 로컬 파일로 단순 저장(serialize) 형태로 학습 가능
- 작은 데이터셋에서 빠르게 실험할 때 유용

주의:
- FAISS 저장/로드는 serialize 방식으로 동작하며, 운영 환경에서는 보안/버전 관리 고려 필요
"""
import os
from rich import print
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import settings
from app.core.llm_factory import build_embeddings
from app.core.rag_utils import load_documents
from app.utils.console import header

FAISS_DIR = "/app/storage/faiss_catalog"

def main():
    header("RAG 08 — FAISS VectorStore")
    docs = load_documents(settings.DOCS_DIR)
    if not docs:
        print("[yellow]data/docs에 문서를 넣어주세요.[/yellow]")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)

    os.makedirs(FAISS_DIR, exist_ok=True)
    emb = build_embeddings()
    vs = FAISS.from_documents(chunks, emb)
    vs.save_local(FAISS_DIR)

    vs2 = FAISS.load_local(FAISS_DIR, emb, allow_dangerous_deserialization=True)
    res = vs2.similarity_search("후원 패키지 구성 요소", k=3)
    print(f"hits: {len(res)}")
    for i, d in enumerate(res, 1):
        print(f"--- hit {i} ---")
        print(d.page_content[:220])

if __name__ == "__main__":
    main()
