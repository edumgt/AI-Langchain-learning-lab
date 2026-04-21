"""RAG 12 — 도메인별 RAG 예시: 병원진료 / 법무상담 / IT업무 기술

실제 업무 도메인에서 RAG를 활용하는 패턴을 세 가지 분야로 나누어 시연합니다.
- 도메인 문서(data/docs/sample_*_notes.md)를 Chroma에 인제스트
- 도메인별 질문을 통해 컨텍스트 검색 후 LLM이 근거 기반 답변을 생성
"""
from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, vectorstore
from app.core import settings
from app.utils.console import header

COLL = "catalog_domain_docs"

DOMAIN_QUESTIONS = {
    "병원진료": "응급실에 가야 하는 증상과, 건강보험 본인부담금 기준을 설명해줘.",
    "법무상담": "부당해고를 당했을 때 신청 기간과 구제 절차를 단계적으로 알려줘.",
    "IT업무 기술": "보안 사고 발생 시 즉시 취해야 할 조치와, 패치 관리 정책의 핵심 기준을 정리해줘.",
}

SYSTEM_MSG = (
    "아래 CONTEXT에서 근거를 찾아 답하라. "
    "CONTEXT에 없는 내용은 '추가 문서 필요'라고 명시하라. "
    "답변은 한국어로, 항목별로 정리해서 작성하라."
)

def run_domain(domain: str, question: str, retriever) -> None:
    print(f"\n[bold yellow]── {domain} ──[/bold yellow]")
    print(f"[cyan]Q:[/cyan] {question}")
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([d.page_content for d in docs])
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_MSG),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])
    llm = build_chat_model()
    resp = (prompt | llm).invoke({"context": context, "q": question})
    print("[green]A:[/green]")
    print(getattr(resp, "content", str(resp)))

def main():
    header("RAG 12 — 도메인별 RAG 예시 (병원진료 / 법무상담 / IT업무 기술)")

    added = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection=COLL)
    print(f"chunks_added: {added}")

    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection=COLL)
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    for domain, question in DOMAIN_QUESTIONS.items():
        run_domain(domain, question, retriever)

if __name__ == "__main__":
    main()
