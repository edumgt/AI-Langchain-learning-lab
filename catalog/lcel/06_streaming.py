"""Streaming 출력(백엔드 지원 시)."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("LCEL 06 — Streaming (지원 모델에서)")
    llm = build_chat_model(streaming=True)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 강연자다."),
        ("human", "LangChain의 LCEL을 5문장으로 설명해줘."),
    ])

    chain = prompt | llm
    # stream()은 토큰/청크를 yield (모델/래퍼에 따라 다름)
    for chunk in chain.stream({}):
        c = getattr(chunk, "content", None)
        if c:
            print(c, end="")
    print()

if __name__ == "__main__":
    main()
