"""batch() / map-like 처리."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("LCEL 04 — batch()")
    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 제목 생성기다. 8자 내외."),
        ("human", "{topic}"),
    ])

    chain = prompt | llm
    inputs = [{"topic":"관객개발"}, {"topic":"후원제안서"}, {"topic":"브랜딩"}]
    res = chain.batch(inputs)
    for r in res:
        print(getattr(r, "content", str(r)))

if __name__ == "__main__":
    main()
