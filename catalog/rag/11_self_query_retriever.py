"""RAG 11 — Self-Query Retriever (메타데이터 필터 실동작)

이 데모는 인덱싱 단계에서 문서에 metadata(type, year, org)를 붙이고,
질문에서 필터 조건을 LLM이 추출해 VectorStore filtering으로 반영하는 패턴입니다.

주의:
- 결과 품질은 문서/메타데이터 설계와 모델에 크게 의존합니다.
- Chroma는 metadata 필터를 지원합니다.
"""
from __future__ import annotations
from rich import print
from typing import List

from langchain_classic.chains.query_constructor.schema import AttributeInfo
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import settings
from app.core.llm_factory import build_chat_model, build_embeddings
from app.core.rag_utils import load_documents
from app.utils.console import header

COLL = "catalog_self_query"

def main():
    header("RAG 11 — Self-Query Retriever (metadata filtering)")
    docs = load_documents(settings.DOCS_DIR)
    if not docs:
        print("[yellow]data/docs에 문서를 넣어주세요.[/yellow]")
        return

    # 1) metadata 부착(학습용 규칙)
    # - 파일명/경로로 type 추정: policy, pr, proposal 등
    enriched = []
    for d in docs:
        src = (d.metadata or {}).get("source", "") or ""
        lower = src.lower()
        if "policy" in lower or "규정" in lower:
            t = "policy"
        elif "press" in lower or "pr" in lower or "보도" in lower:
            t = "pr"
        elif "proposal" in lower or "후원" in lower or "제안" in lower:
            t = "proposal"
        else:
            t = "general"

        # year/org는 예시값(실전에서는 문서 본문/헤더에서 추출)
        d.metadata = {**(d.metadata or {}), "type": t, "year": 2026, "org": "local-arts-foundation"}
        enriched.append(d)

    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(enriched)

    vs = Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=build_embeddings(),
        collection_name=COLL,
    )
    vs.add_documents(chunks)
    vs.persist()

    # 2) Self-query 설정
    llm = build_chat_model(temperature=0)
    metadata_field_info = [
        AttributeInfo(name="type", description="문서 유형: policy|pr|proposal|general", type="string"),
        AttributeInfo(name="year", description="문서 연도(예: 2026)", type="integer"),
        AttributeInfo(name="org", description="기관 식별자", type="string"),
    ]

    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vs,
        document_contents="문화예술기관의 문서/가이드/제안서 내용",
        metadata_field_info=metadata_field_info,
        search_kwargs={"k": settings.TOP_K},
        verbose=True,
    )

    # 3) 질문: 메타데이터 조건이 섞인 질의
    q = "2026년 policy 문서 근거로, 개인정보 수집 동의 관련 주의점만 요약해줘."
    hits = retriever.get_relevant_documents(q)

    print(f"hits: {len(hits)}")
    for i, d in enumerate(hits, 1):
        print(f"--- {i} --- meta={d.metadata}")
        print(d.page_content[:240])

if __name__ == "__main__":
    main()
