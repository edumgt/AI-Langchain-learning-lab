"""partial() / 변수 처리."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("PROMPTS 03 — partial() & variables")
    llm = build_chat_model()

    base = ChatPromptTemplate.from_messages([
        ("system", "너는 {role}다. 톤은 {tone}."),
        ("human", "{task}"),
    ])

    prompt = base.partial(role="예술경영 컨설턴트", tone="실무적이고 구조적")
    resp = (prompt | llm).invoke({"task":"지역 문화재단 6개월 프로그램 로드맵을 표로 제시해줘."})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
