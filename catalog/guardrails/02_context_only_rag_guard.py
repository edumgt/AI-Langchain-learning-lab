"""Guardrails 02 — Context-only RAG guard

목표:
- 문서 근거가 없으면 답변하지 않도록(환각 방지) 프롬프트 가드레일을 적용
"""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("GUARD 02 — Context-only RAG")
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = build_chat_model(temperature=0)

    q = "이 문서 근거로만, 후원 계약서에 반드시 들어가야 할 항목을 5개만."
    docs = retriever.get_relevant_documents(q)
    context = "\n\n".join(d.page_content for d in docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 규정 준수 모드다. CONTEXT에 없는 내용은 추측하지 말고 '근거 부족'이라고 말하라."),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])

    resp = (prompt | llm).invoke({"context": context, "q": q})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
