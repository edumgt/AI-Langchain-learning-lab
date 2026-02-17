from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever

from app.core import settings
from app.core.llm_factory import build_chat_model, build_embeddings
from app.core.rag_utils import ingest_dir_meta, vectorstore
from app.utils.console import header  # unused but kept for parity

router = APIRouter(prefix="/rag", tags=["rag"])

class SelfQueryRequest(BaseModel):
    q: str = Field(min_length=1)
    k: int = 4

class SelfQueryResponse(BaseModel):
    answer: str
    used_docs: list[dict]
    parsed_query: dict | None = None

@router.post("/self-query", response_model=SelfQueryResponse)
def self_query(req: SelfQueryRequest):
    # ensure index has metadata
    ingest_dir_meta(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    llm = build_chat_model(temperature=0)

    metadata_field_info = [
        AttributeInfo(name="type", description="문서 유형: policy|pr|proposal|general", type="string"),
        AttributeInfo(name="year", description="문서 연도(예: 2026)", type="integer"),
        AttributeInfo(name="org", description="기관 식별자", type="string"),
    ]

    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vs,
        document_contents="예술경영 관련 내부 문서/가이드/제안서",
        metadata_field_info=metadata_field_info,
        search_kwargs={"k": req.k},
        verbose=True,
    )

    docs = retriever.get_relevant_documents(req.q)
    context = "\n\n".join([f"SOURCE {i+1}: {d.page_content}" for i, d in enumerate(docs[:2])])

    prompt = build_chat_model(temperature=0)  # reuse model
    resp = prompt.invoke([
        {"role":"system","content":"너는 CONTEXT 기반으로만 답한다. 마지막에 근거 섹션에 SOURCE 1~2를 인용하라."},
        {"role":"user","content": f"CONTEXT:\n{context}\n\nQ:\n{req.q}"},
    ])
    used = [{"meta": d.metadata, "preview": d.page_content[:200]} for d in docs[:3]]
    return SelfQueryResponse(answer=getattr(resp,"content",str(resp)), used_docs=used, parsed_query=None)
