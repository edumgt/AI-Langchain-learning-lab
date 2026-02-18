"""LangGraph 02 — Agentic loop graph (plan -> execute -> critique -> decide)

목표:
- 계획(Plan) 생성
- 실행(Execute) 답변 생성
- 비평(Critique)로 품질 점검
- 기준 통과 시 종료 / 아니면 반복

학습 포인트:
- 조건부 엣지(conditional edges)
- 루프(loop)
"""
from __future__ import annotations
from typing import TypedDict, Literal
from rich import print

from langgraph.graph import StateGraph, END

from app.core.llm_factory import build_chat_model
from app.utils.console import header
from catalog.langgraph._viz import render_graph_mermaid

class State(TypedDict):
    goal: str
    plan: str
    draft: str
    critique: str
    ok: bool
    iter: int

def main():
    header("LANGGRAPH 02 — Agentic loop (plan/execute/critique)")
    llm = build_chat_model(temperature=0.2)

    def planner(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 기획자다. 실행 가능한 간단 계획을 만든다."},
            {"role":"user","content": f"목표: {s['goal']}\n2주 계획을 5개 bullet로."},
        ])
        return {**s, "plan": getattr(resp,"content",str(resp))}

    def executor(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 실행 담당자다. 계획을 바탕으로 초안을 작성한다."},
            {"role":"user","content": f"PLAN:\n{s['plan']}\n\n초안(체크리스트/표 포함) 작성."},
        ])
        return {**s, "draft": getattr(resp,"content",str(resp))}

    def critic(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 리뷰어다. 기준: 현실성/구체성/예산 적합성. 통과면 OK=true."},
            {"role":"user","content": f"GOAL:{s['goal']}\nDRAFT:\n{s['draft']}\n\n(1) 개선점 3개 (2) OK 여부만 마지막 줄에 'OK: true/false'"},
        ])
        text = getattr(resp,"content",str(resp))
        ok = "OK: true" in text.lower()
        return {**s, "critique": text, "ok": ok, "iter": s["iter"] + 1}

    def decide(s: State) -> Literal["done", "loop"]:
        # 최대 2회 반복
        if s["ok"] or s["iter"] >= 2:
            return "done"
        return "loop"

    g = StateGraph(State)
    g.add_node("plan", planner)
    g.add_node("execute", executor)
    g.add_node("critique", critic)

    g.set_entry_point("plan")
    g.add_edge("plan", "execute")
    g.add_edge("execute", "critique")
    g.add_conditional_edges("critique", decide, {"done": END, "loop": "execute"})

    app = g.compile()
    render_graph_mermaid(app, "02_agentic_loop_graph")
    out = app.invoke({"goal":"예산 3천만원으로 2주 관객개발 SNS 캠페인 런칭", "plan":"", "draft":"", "critique":"", "ok": False, "iter": 0})
    print("\n[bold]FINAL DRAFT[/bold]\n", out["draft"])
    print("\n[bold]CRITIQUE[/bold]\n", out["critique"])

if __name__ == "__main__":
    main()
