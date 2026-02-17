from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

def main():
    header("02) LCEL(Runnable) 파이프라인")
    show_provider()

    llm = build_chat_model()

    # 1) 입력 전처리
    normalize = RunnableLambda(lambda x: {"topic": x.strip()})

    # 2) 프롬프트
    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 학습 튜터다. 짧고 명확하게 설명한다."),
        ("human", "주제: {topic}\n- 핵심 개념 3개\n- 예시 2개\n- 주의점 1개"),
    ])

    # 3) 문자열 출력 파서
    chain = normalize | prompt | llm | StrOutputParser()

    out = chain.invoke("LCEL (LangChain Expression Language)")
    print(out)

    # 4) RunnablePassthrough로 병렬/합성(간단 예시)
    def summarize(text: str) -> str:
        return text[:200] + "..." if len(text) > 200 else text

    chain2 = (
        {"raw": chain, "summary": chain | RunnableLambda(summarize)}
    )
    out2 = chain2.invoke("RAG (Retrieval Augmented Generation)")
    print("\n[bold]raw[/bold]\n", out2["raw"])
    print("\n[bold]summary[/bold]\n", out2["summary"])

if __name__ == "__main__":
    main()
