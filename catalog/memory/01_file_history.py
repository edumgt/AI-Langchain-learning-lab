"""FileChatMessageHistory."""
import os
from rich import print
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory
from app.core.llm_factory import build_chat_model
from app.utils.console import header

HIST_DIR = "/app/storage/chat_history"

def get_history(session_id: str):
    os.makedirs(HIST_DIR, exist_ok=True)
    return FileChatMessageHistory(os.path.join(HIST_DIR, f"{session_id}.json"))

def main():
    header("MEMORY 01 — FileChatMessageHistory")
    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 사용자 제약을 기억한다."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm
    chat = RunnableWithMessageHistory(chain, get_history, input_messages_key="input", history_messages_key="history")

    sid = "catalog-demo"
    r1 = chat.invoke({"input":"예산은 3천만원이고, 지역 커뮤니티 협업이 중요해."}, config={"configurable":{"session_id":sid}})
    print(getattr(r1,"content",str(r1)))
    r2 = chat.invoke({"input":"그 조건 유지하고 3가지 캠페인만."}, config={"configurable":{"session_id":sid}})
    print(getattr(r2,"content",str(r2)))

if __name__ == "__main__":
    main()
