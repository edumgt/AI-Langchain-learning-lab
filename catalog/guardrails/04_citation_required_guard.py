"""Guardrails 04 — Citation-required pattern (학습용)

목표:
- 답변에 반드시 '근거' 섹션(문서 snippet)을 포함시키는 패턴
- 실제 서비스에서는 인용(페이지/문단/출처)을 정교화해야 함
"""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("GUARD 04 — Citation-required pattern")
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    docs = vs.similarity_search("후원 혜택", k=3)

    context = "\n\n".join([f"[SOURCE {i+1}] {d.page_content}" for i, d in enumerate(docs)])

    llm = build_chat_model(temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system","반드시 '근거' 섹션에 SOURCE를 최소 2개 인용하라. SOURCE 밖 내용은 추측하지 말라."),
        ("human","CONTEXT:\n{context}\n\n질문: 후원 패키지 혜택을 5개로 요약해줘. 마지막에 근거(인용) 포함."),
    ])

    resp = (prompt | llm).invoke({"context": context})
    print(getattr(resp,"content",str(resp)))

if __name__ == "__main__":
    main()
