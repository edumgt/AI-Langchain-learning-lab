from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, build_vectorstore
from app.core import settings
from lessons._utils import header, show_provider

def main():
    header("08) RAG 고급 — MultiQuery + Contextual Compression")
    show_provider()

    if not settings.RAG_ENABLED:
        print("[red]RAG_ENABLED=false 입니다. .env에서 true로 바꾸세요.[/red]")
        return

    # ensure index
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection_name="lab_docs")

    vs = build_vectorstore(settings.CHROMA_PERSIST_DIR, collection_name="lab_docs")
    base_retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = build_chat_model(temperature=0.2)

    # 1) Multi-query retriever: 질문을 여러 관점으로 재작성해 recall 증가
    mqr = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

    # 2) Compression retriever: 가져온 문서에서 질문과 관련된 부분만 추출
    compressor = LLMChainExtractor.from_llm(llm)
    ccr = ContextualCompressionRetriever(base_retriever=mqr, base_compressor=compressor)

    question = "기관의 관객개발 성과를 측정할 수 있는 KPI 설계 프레임을 제안해줘."
    docs = ccr.get_relevant_documents(question)

    context = "\n\n".join([d.page_content for d in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "CONTEXT에서 근거를 찾아 실행 가능한 프레임을 제시하라. 근거가 부족하면 일반론+추가자료요청으로 구분하라."),
        ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])

    resp = (prompt | llm).invoke({"context": context, "q": question})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
