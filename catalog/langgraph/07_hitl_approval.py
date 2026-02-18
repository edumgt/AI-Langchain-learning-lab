"""LANGGRAPH 07 — Human-in-the-loop approval (패턴 데모)

실무에서는 중요한 액션(메일 발송/결제/DB 변경 등)을 수행하기 전에
- 승인을 받거나
- 승인 토큰/플래그가 있어야 진행
하도록 설계합니다.

이 카탈로그 데모는 비대화형 Docker에서도 돌 수 있도록,
환경변수로 승인 여부를 흉내 냅니다.

- AUTO_APPROVE=true 이면 자동 통과
- AUTO_APPROVE=false 이면 APPROVE_TOKEN이 'YES'일 때만 통과 (그 외는 block)

.env.example 참고
"""
from __future__ import annotations
import os
from typing import TypedDict, Literal
from rich import print

from langgraph.graph import StateGraph, END
from app.core.llm_factory import build_chat_model
from app.utils.console import header
from catalog.langgraph._viz import render_graph_mermaid

class State(TypedDict):
    q: str
    draft: str
    approved: bool
    final: str
    reason: str

def main():
    header("LANGGRAPH 07 — HITL approval (pattern)")
    llm = build_chat_model(temperature=0.2)

    auto = (os.getenv("AUTO_APPROVE","true").lower() == "true")
    token = os.getenv("APPROVE_TOKEN","YES")

    def draft_node(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 기획자다. 초안을 만든다."},
            {"role":"user","content": s["q"]},
        ])
        return {**s, "draft": getattr(resp,"content",str(resp))}

    def approve_node(s: State) -> State:
        if auto:
            return {**s, "approved": True, "reason":"AUTO_APPROVE=true"}
        # 비대화형 환경에서는 토큰으로 승인 흉내
        return {**s, "approved": (token == "YES"), "reason": f"AUTO_APPROVE=false, token={token}"}

    def route(s: State) -> Literal["finalize","block"]:
        return "finalize" if s["approved"] else "block"

    def finalize(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"초안을 최종 문서로 다듬어라."},
            {"role":"user","content": f"DRAFT:\n{s['draft']}\n\n최종본으로 정리(표/체크리스트 포함)"},
        ])
        return {**s, "final": getattr(resp,"content",str(resp))}

    def block(s: State) -> State:
        return {**s, "final": f"승인이 필요합니다. ({s['reason']})\n\n초안은 생성됐으니 검토 후 승인 토큰을 설정하세요."}

    g = StateGraph(State)
    g.add_node("draft", draft_node)
    g.add_node("approve", approve_node)
    g.add_node("finalize", finalize)
    g.add_node("block", block)

    g.set_entry_point("draft")
    g.add_edge("draft","approve")
    g.add_conditional_edges("approve", route, {"finalize":"finalize", "block":"block"})
    g.add_edge("finalize", END)
    g.add_edge("block", END)

    app = g.compile()
    render_graph_mermaid(app, "07_hitl_approval")
    out = app.invoke({"q":"예산 3천만원, 2주 관객개발 캠페인 실행 계획 만들어줘.", "draft":"", "approved": False, "final":"", "reason":""})
    print(out["final"])

if __name__ == "__main__":
    main()
