"""LLM tool-calling: bind_tools. (백엔드에 따라 차이)"""
from rich import print
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

@tool
def kpi_suggestions(goal: str) -> list[str]:
    """목표 기반 KPI 제안"""
    base = ["신규 방문자 수", "재방문율", "전환율(클릭→예매)", "NPS", "회원/구독자 증가"]
    if "후원" in goal:
        base += ["후원 유치 금액", "리드→계약 전환율"]
    return base

def main():
    header("TOOLS 02 — bind_tools (tool calling)")
    llm = build_chat_model(temperature=0)
    llm_tools = llm.bind_tools([kpi_suggestions])

    prompt = ChatPromptTemplate.from_messages([
        ("system","필요하면 도구를 호출해라."),
        ("human","목표는 '후원 유치'야. KPI 추천하고 간단히 설명해줘."),
    ])

    resp = (prompt | llm_tools).invoke({})
    print(resp)
    c = getattr(resp,"content",None)
    if c:
        print("\n[bold]content[/bold]\n", c)

if __name__ == "__main__":
    main()
