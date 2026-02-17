"""AGENTS 03 — Safe tool router + validation (카탈로그 패턴)

목표:
- LLM이 무조건 툴을 쓰게 두지 않고, '라우터' 단계에서
  어떤 툴을 써도 되는지(또는 툴 없이 답할지) 먼저 결정한다.
- 툴 결과는 Pydantic으로 검증한 뒤, '정제된 결과'만 최종 응답에 사용한다.

학습 포인트:
- structured routing (with_structured_output)
- allowlist tools
- tool output validation (Pydantic)
"""
from __future__ import annotations
from rich import print
from pydantic import BaseModel, Field, ValidationError
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.utils.console import header

# 1) tools
@tool
def calc_budget_split(total_krw: int, ads_ratio: float = 0.5, content_ratio: float = 0.3) -> dict:
    """간단 예산 분배(학습용)."""
    events_ratio = max(0.0, 1.0 - ads_ratio - content_ratio)
    return {
        "ads_paid": int(total_krw * ads_ratio),
        "content_prod": int(total_krw * content_ratio),
        "events": int(total_krw * events_ratio),
        "total": total_krw,
    }

@tool
def draft_copy(theme: str) -> dict:
    """홍보 카피 3개 생성(학습용)."""
    return {"theme": theme, "copies": [f"{theme} — 당신의 하루를 바꾸는 순간", f"{theme} — 도시가 예술이 되는 시간", f"{theme} — 함께라서 더 깊다"]}

# 2) router schema
class Route(BaseModel):
    use_tools: bool = Field(description="툴을 사용해야 하면 true")
    tools: list[str] = Field(description="허용된 툴 이름 리스트")
    reason: str

# 3) validator schemas
class BudgetPlan(BaseModel):
    ads_paid: int
    content_prod: int
    events: int
    total: int

class CopySet(BaseModel):
    theme: str
    copies: list[str]

ALLOWED = {"calc_budget_split": calc_budget_split, "draft_copy": draft_copy}

def main():
    header("AGENTS 03 — Safe Tool Router + Validation")
    llm = build_chat_model(temperature=0)

    router = llm.with_structured_output(Route)
    router_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "너는 툴 라우터다. 아래 규칙을 지켜라.\n"
         "- tools는 허용 목록 중에서만 선택: calc_budget_split, draft_copy\n"
         "- 숫자 계산/예산 배분이면 calc_budget_split 권장\n"
         "- 카피 생성이면 draft_copy 권장\n"
         "- 애매하면 tools 사용하지 말고 use_tools=false\n"
         "- tools가 비어있으면 use_tools=false로"),
        ("human", "{q}"),
    ])

    q = "예산 30000000원으로 관객개발 캠페인 예산 배분안을 표로 만들고, 카피도 2개만 줘."
    r = (router_prompt | router).invoke({"q": q})
    print("[bold]ROUTE[/bold]", r.model_dump())

    # allowlist enforce
    selected = [t for t in r.tools if t in ALLOWED]
    if not r.use_tools or not selected:
        resp = llm.invoke([{"role":"user","content": q}])
        print(getattr(resp,"content",str(resp)))
        return

    # tool execution (explicit)
    tool_results = {}
    for t in selected:
        if t == "calc_budget_split":
            tool_results[t] = ALLOWED[t].invoke({"total_krw": 30000000})
        elif t == "draft_copy":
            tool_results[t] = ALLOWED[t].invoke({"theme": "도시의 결"})

    # validate & normalize (guardrail)
    budget = None
    copies = None
    try:
        if "calc_budget_split" in tool_results:
            budget = BudgetPlan(**tool_results["calc_budget_split"]).model_dump()
        if "draft_copy" in tool_results:
            copies = CopySet(**tool_results["draft_copy"]).model_dump()
    except ValidationError as e:
        print("[red]Tool output validation failed[/red]")
        print(e)
        return

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "아래 TOOL_DATA만 근거로 표/카피를 정리해라. TOOL_DATA에 없는 정보는 추측하지 말라."),
        ("human", "Q:{q}\n\nTOOL_DATA:\n{tool_data}"),
    ])

    tool_data = {"budget": budget, "copies": copies}
    resp = (final_prompt | llm).invoke({"q": q, "tool_data": json.dumps(tool_data, ensure_ascii=False, indent=2)})
    print(getattr(resp,"content",str(resp)))

if __name__ == "__main__":
    main()
