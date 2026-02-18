"""LangGraph 05 — Subgraph pattern (분해/조합)

학습 포인트:
- 큰 워크플로우를 작은 그래프로 나누고(subgraph),
  상위 그래프에서 조합하는 설계 감각
"""
from __future__ import annotations
from typing import TypedDict
from rich import print

from langgraph.graph import StateGraph, END

from app.core.llm_factory import build_chat_model
from app.utils.console import header
from catalog.langgraph._viz import render_graph_mermaid

class State(TypedDict):
    q: str
    outline: str
    answer: str

def make_outline_graph(llm):
    def outline_node(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"아웃라인만 만든다(5개 bullet)."},
            {"role":"user","content": s["q"]},
        ])
        return {**s, "outline": getattr(resp,"content",str(resp))}
    g = StateGraph(State)
    g.add_node("outline", outline_node)
    g.set_entry_point("outline")
    g.add_edge("outline", END)
    return g.compile()

def make_answer_graph(llm):
    def answer_node(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"아웃라인을 근거로 답변을 작성한다."},
            {"role":"user","content": f"OUTLINE:\n{s['outline']}\n\nQ:{s['q']}\n\n답변 작성"},
        ])
        return {**s, "answer": getattr(resp,"content",str(resp))}
    g = StateGraph(State)
    g.add_node("answer", answer_node)
    g.set_entry_point("answer")
    g.add_edge("answer", END)
    return g.compile()

def main():
    header("LANGGRAPH 05 — Subgraph pattern")
    llm = build_chat_model(temperature=0.2)
    outline_app = make_outline_graph(llm)
    answer_app = make_answer_graph(llm)
    render_graph_mermaid(outline_app, "05_subgraph_pattern_outline")
    render_graph_mermaid(answer_app, "05_subgraph_pattern_answer")

    q = "예산 3천만원으로 지역 커뮤니티 협업 관객개발 캠페인을 2주 안에 실행하는 계획"
    s: State = {"q": q, "outline": "", "answer": ""}

    s = outline_app.invoke(s)
    s = answer_app.invoke(s)
    print("[bold]OUTLINE[/bold]\n", s["outline"])
    print("\n[bold]ANSWER[/bold]\n", s["answer"])

if __name__ == "__main__":
    main()
