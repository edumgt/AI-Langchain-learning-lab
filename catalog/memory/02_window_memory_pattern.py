"""Window memory 패턴: 최근 N턴만 프롬프트에 포함."""
from rich import print
from collections import deque
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("MEMORY 02 — Window memory (간단 패턴)")
    llm = build_chat_model()
    window = deque(maxlen=4)  # last 4 messages

    def ask(text: str):
        window.append(("human", text))
        prompt = ChatPromptTemplate.from_messages([("system","최근 대화만 참고한다."), *list(window)])
        resp = (prompt | llm).invoke({})
        window.append(("ai", getattr(resp,"content",str(resp))))
        return resp

    ask("나는 전시 프로젝트를 준비 중이야.")
    ask("예산은 3천만원이야.")
    ask("주 타깃은 20~30대야.")
    r = ask("이 조건으로 2주 캠페인 계획을 요약해줘.")
    print(getattr(r,"content",str(r)))

if __name__ == "__main__":
    main()
