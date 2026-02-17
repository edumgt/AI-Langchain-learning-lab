"""Retriever: MultiQuery + Compression."""
from rich import print
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.utils.console import header

def main():
    header("RAG 04 — MultiQuery + Compression")
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    base = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = build_chat_model(temperature=0.2)

    mqr = MultiQueryRetriever.from_llm(retriever=base, llm=llm)
    compressor = LLMChainExtractor.from_llm(llm)
    ccr = ContextualCompressionRetriever(base_retriever=mqr, base_compressor=compressor)

    q = "문화예술기관에서 관객개발 성과지표(KPI)를 설계할 때 주의점을 알려줘."
    docs = ccr.get_relevant_documents(q)
    context = "\n\n".join([d.page_content for d in docs])

    prompt = ChatPromptTemplate.from_messages([
        ("system","CONTEXT 기반으로만 답하고, 부족하면 추가자료 요청을 명시해라."),
        ("human","CONTEXT:\n{context}\n\nQUESTION:\n{q}"),
    ])

    resp = (prompt | llm).invoke({"context": context, "q": q})
    print(getattr(resp,"content",str(resp)))

if __name__ == "__main__":
    main()
