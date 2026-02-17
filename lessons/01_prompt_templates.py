from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from app.core.llm_factory import build_chat_model
from app.core.prompts import artbiz_system_messages
from lessons._utils import header, show_provider

def main():
    header("01) PromptTemplate & Messages")
    show_provider()

    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        *[(m["role"], m["content"]) for m in artbiz_system_messages()],
        ("system", "출력은 마크다운으로, 제목/요약/실행항목을 포함하세요."),
        ("human", "기관 유형: {org_type}\n목표: {goal}\n예산: {budget}"),
    ])

    chain = prompt | llm

    resp = chain.invoke({
        "org_type": "지역 공공문화재단",
        "goal": "2026 상반기 관객개발(20~30대 신규 유입 + 재방문)",
        "budget": "3천만원",
    })
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
