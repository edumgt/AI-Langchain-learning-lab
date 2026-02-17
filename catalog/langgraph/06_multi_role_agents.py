"""LangGraph 06 — Multi-role (strategy/marketing/fundraising/ops) 합의 패턴

학습 포인트:
- '역할별'로 병렬 산출물을 만들고
- 마지막에 합의/통합 노드로 수렴시키는 패턴

※ 실제 멀티에이전트 프레임워크가 아니라, 카탈로그 학습용 설계 패턴입니다.
"""
from __future__ import annotations
from typing import TypedDict
from rich import print

from langgraph.graph import StateGraph, END

from app.core.llm_factory import build_chat_model
from app.utils.console import header

class State(TypedDict):
    q: str
    strategy: str
    marketing: str
    fundraising: str
    ops: str
    final: str

def main():
    header("LANGGRAPH 06 — Multi-role synthesis")
    llm = build_chat_model(temperature=0.2)

    def role_node(role: str, instruction: str):
        def _fn(s: State) -> State:
            resp = llm.invoke([
                {"role":"system","content": instruction},
                {"role":"user","content": s["q"]},
            ])
            return {**s, role: getattr(resp,"content",str(resp))}
        return _fn

    def synth(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"아래 4개 관점을 통합해 실행 계획 1개로 정리(표 포함)."},
            {"role":"user","content": f"Q:{s['q']}\n\n[STRATEGY]\n{s['strategy']}\n\n[MARKETING]\n{s['marketing']}\n\n[FUNDRAISING]\n{s['fundraising']}\n\n[OPS]\n{s['ops']}"},
        ])
        return {**s, "final": getattr(resp,"content",str(resp))}

    g = StateGraph(State)
    g.add_node("strategy", role_node("strategy","너는 전략 컨설턴트다. 목표/우선순위/리스크 중심."))
    g.add_node("marketing", role_node("marketing","너는 마케팅 리드다. 채널/콘텐츠/퍼널 중심."))
    g.add_node("fundraising", role_node("fundraising","너는 후원 전문가다. 패키지/제안서/KPI 중심."))
    g.add_node("ops", role_node("ops","너는 운영 담당이다. 일정/예산/체크리스트 중심."))
    g.add_node("synth", synth)

    g.set_entry_point("strategy")
    g.add_edge("strategy","marketing")
    g.add_edge("marketing","fundraising")
    g.add_edge("fundraising","ops")
    g.add_edge("ops","synth")
    g.add_edge("synth", END)

    app = g.compile()
    out = app.invoke({
        "q":"예산 3천만원, 지역 커뮤니티 협업, 2주 관객개발 캠페인 런칭 계획",
        "strategy":"","marketing":"","fundraising":"","ops":"","final":""
    })
    print(out["final"])

if __name__ == "__main__":
    main()
