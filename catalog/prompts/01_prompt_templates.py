"""PromptTemplate / ChatPromptTemplate 기본."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("PROMPTS 01 — ChatPromptTemplate 기본")
    llm = build_chat_model()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 친절한 튜터다."),
        ("human", "주제: {topic}\n핵심 3개만 알려줘."),
    ])
    chain = prompt | llm
    resp = chain.invoke({"topic":"LangChain PromptTemplate"})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
