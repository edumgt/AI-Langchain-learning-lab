from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, vectorstore
from app.core import settings
from lessons._utils import header, show_provider

# 도메인별 질의 예시
DOMAIN_QUESTIONS = {
    "병원진료": "응급실에 가야 하는 증상과, 외래진료 예약 없이 방문했을 때 절차를 알려줘.",
    "법무상담": "직장 내 괴롭힘을 당했을 때 취할 수 있는 법적 절차와 신고 방법을 설명해줘.",
    "IT업무 기술": "서버가 응답하지 않을 때 1차 점검 절차와, 보안 사고 발생 시 즉시 해야 할 조치를 알려줘.",
}

SYSTEM_MSG = (
    "아래 CONTEXT에서 근거를 찾아 답하라. "
    "CONTEXT에 없는 내용은 '추가 문서 필요'라고 명시하라. "
    "답변은 한국어로, 항목별로 정리해서 작성하라."
)

def run_rag_for_domain(domain: str, question: str, retriever) -> None:
    print(f"\n[bold yellow]── {domain} ──[/bold yellow]")
    print(f"[cyan]질문:[/cyan] {question}")

    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_MSG),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])

    llm = build_chat_model()
    resp = (prompt | llm).invoke({"context": context, "q": question})
    print("[green]답변:[/green]")
    print(getattr(resp, "content", str(resp)))

def main():
    header("13) RAG 도메인 예시 — 병원진료 / 법무상담 / IT업무 기술")
    show_provider()

    if not settings.RAG_ENABLED:
        print("[red]RAG_ENABLED=false 입니다. .env에서 true로 바꾸세요.[/red]")
        return

    # Ingest (세 도메인 문서가 DOCS_DIR에 포함됨)
    added = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="domain_docs")
    print(f"[green]chunks_added:[/green] {added}")

    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="domain_docs")
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    for domain, question in DOMAIN_QUESTIONS.items():
        run_rag_for_domain(domain, question, retriever)

if __name__ == "__main__":
    main()
