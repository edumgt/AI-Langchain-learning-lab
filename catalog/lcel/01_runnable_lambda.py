"""RunnableLambda / 전처리-후처리 기본."""
from rich import print
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("LCEL 01 — RunnableLambda 전처리/후처리")
    llm = build_chat_model()

    normalize = RunnableLambda(lambda x: {"topic": x.strip().lower()})
    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 튜터다."),
        ("human", "주제: {topic} 를 2문장으로 설명해줘."),
    ])
    chain = normalize | prompt | llm | StrOutputParser()
    print(chain.invoke("  LCEL (Runnable)  "))

if __name__ == "__main__":
    main()
