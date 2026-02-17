from __future__ import annotations
from rich import print
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

@tool
def budget_split(total_krw: int, items: list[str]) -> dict:
    """예산을 항목 수로 균등 분배해 간단한 권장 배분안을 만든다."""
    n = max(len(items), 1)
    each = total_krw // n
    return {name: each for name in items}

@tool
def kpi_suggestions(goal: str) -> list[str]:
    """목표에 맞는 KPI 아이디어를 추천한다."""
    base = [
        "신규 방문자 수",
        "재방문율",
        "캠페인 전환율(클릭→예매)",
        "회원/구독자 증가",
        "만족도(NPS/설문)",
        "파트너십 확보 수",
    ]
    if "후원" in goal or "스폰서" in goal:
        base += ["후원 유치 금액", "리드→계약 전환율", "후원사 유지율"]
    return base

def main():
    header("05) Tool Calling (LLM + tools)")
    show_provider()

    llm = build_chat_model()
    llm_tools = llm.bind_tools([budget_split, kpi_suggestions])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "필요하면 툴을 호출해 정확한 숫자/목록을 만든 뒤 답한다."),
        ("human", "예산 30000000원으로 관객개발 캠페인 3개를 운영하려고 해. 항목은 광고, 콘텐츠, 이벤트야. 예산배분과 KPI를 표로 정리해줘."),
    ])

    resp = (prompt | llm_tools).invoke({})

    # Some models will return tool calls; ChatOpenAI/ChatOllama wrappers handle it.
    # For learning: show raw
    print("[bold]Raw model output[/bold]")
    print(resp)

    # If tool-calls were executed by wrapper, content may include final answer.
    content = getattr(resp, "content", None)
    if content:
        print("\n[bold]Answer[/bold]")
        print(content)
    else:
        print("\n[dim]Model returned a tool-call message object. Different backends behave differently.[/dim]")

if __name__ == "__main__":
    main()
