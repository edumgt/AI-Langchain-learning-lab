"""LangGraph 03 — Guarded graph (policy check -> answer)

학습 포인트:
- 입력 검증/정책 체크를 그래프 앞단에 넣는 패턴
- 실패 시 안전 응답으로 종료
"""
from __future__ import annotations
from typing import TypedDict, Literal
from rich import print

from langgraph.graph import StateGraph, END
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class State(TypedDict):
    q: str
    allowed: bool
    reason: str
    answer: str

def main():
    header("LANGGRAPH 03 — Guarded graph")
    llm = build_chat_model(temperature=0)

    def policy_check(s: State) -> State:
        # 학습용: 간단 정책(예: 개인정보/불법 요청) 체크 흉내
        banned = ["주민등록번호", "해킹", "무단 침입", "불법"]
        if any(b in s["q"] for b in banned):
            return {**s, "allowed": False, "reason": "정책/안전상 제공 불가"}
        return {**s, "allowed": True, "reason": "ok"}

    def route(s: State) -> Literal["answer", "block"]:
        return "answer" if s["allowed"] else "block"

    def block(s: State) -> State:
        return {**s, "answer": f"요청을 처리할 수 없습니다: {s['reason']}. 대신 안전한 범위에서 일반 가이드를 제공할까요?"}

    def answer(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 도움되는 조력자다."},
            {"role":"user","content": s["q"]},
        ])
        return {**s, "answer": getattr(resp,"content",str(resp))}

    g = StateGraph(State)
    g.add_node("policy", policy_check)
    g.add_node("block", block)
    g.add_node("answer", answer)

    g.set_entry_point("policy")
    g.add_conditional_edges("policy", route, {"answer":"answer", "block":"block"})
    g.add_edge("answer", END)
    g.add_edge("block", END)

    app = g.compile()
    out = app.invoke({"q":"2주 안에 SNS 캠페인을 런칭하려면?", "allowed": True, "reason":"", "answer":""})
    print(out["answer"])

if __name__ == "__main__":
    main()
