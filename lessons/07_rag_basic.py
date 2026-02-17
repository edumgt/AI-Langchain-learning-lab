from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, build_vectorstore
from app.core import settings
from lessons._utils import header, show_provider

def main():
    header("07) RAG 기본 — ingest + retrieve + answer")
    show_provider()

    if not settings.RAG_ENABLED:
        print("[red]RAG_ENABLED=false 입니다. .env에서 true로 바꾸세요.[/red]")
        return

    # 1) Ingest
    added = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection_name="lab_docs")
    print(f"[green]chunks_added:[/green] {added}")

    # 2) Retrieve
    vs = build_vectorstore(settings.CHROMA_PERSIST_DIR, collection_name="lab_docs")
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    question = "이 문서들 기반으로, 기관의 홍보/마케팅 운영 시 주의할 점을 5가지로 정리해줘."
    docs = retriever.get_relevant_documents(question)

    context = "\n\n".join([d.page_content for d in docs])
    prompt = ChatPromptTemplate.from_messages([
        ("system", "아래 CONTEXT 기반으로만 답하라. 없으면 '추가 문서 필요'라고 말하라."),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])

    llm = build_chat_model()
    resp = (prompt | llm).invoke({"context": context, "q": question})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
