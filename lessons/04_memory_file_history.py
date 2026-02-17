from __future__ import annotations
import os
from rich import print
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

HIST_DIR = "/app/storage/chat_history"

def get_history(session_id: str):
    os.makedirs(HIST_DIR, exist_ok=True)
    path = os.path.join(HIST_DIR, f"{session_id}.json")
    return FileChatMessageHistory(path)

def main():
    header("04) Memory — FileChatMessageHistory + RunnableWithMessageHistory")
    show_provider()

    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 대화 맥락을 기억하는 조력자다. 사용자 선호/제약을 유지한다."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm

    chat = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    session_id = "demo-user-001"

    r1 = chat.invoke({"input": "나는 예산 3천만원으로 관객개발을 하고 싶어."}, config={"configurable": {"session_id": session_id}})
    print(getattr(r1, "content", str(r1)))

    r2 = chat.invoke({"input": "방금 말한 예산 조건을 반영해서 3가지 캠페인 아이디어만 제시해줘."}, config={"configurable": {"session_id": session_id}})
    print("\n" + getattr(r2, "content", str(r2)))

    print("\n[dim]대화 기록 파일: storage/chat_history/demo-user-001.json[/dim]")

if __name__ == "__main__":
    main()
