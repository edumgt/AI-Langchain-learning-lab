"""LangGraph 01 — Minimal graph (state -> node -> state)

LangGraph는 '상태(state)'와 '노드(node)'를 연결해 워크플로우를 구성합니다.
이 예시는 가장 단순한 형태의 그래프를 보여줍니다.
"""
from __future__ import annotations
from typing import TypedDict
from rich import print

from langgraph.graph import StateGraph, END

from app.core.llm_factory import build_chat_model
from app.utils.console import header
from catalog.langgraph._viz import render_graph_mermaid

class State(TypedDict):
    topic: str
    answer: str

def main():
    header("LANGGRAPH 01 — Minimal graph")
    llm = build_chat_model()

    def generate(state: State) -> State:
        resp = llm.invoke([{"role":"user","content": f"주제: {state['topic']}\n핵심 3개로 설명해줘."}])
        return {"topic": state["topic"], "answer": getattr(resp, "content", str(resp))}

    g = StateGraph(State)
    g.add_node("generate", generate)
    g.set_entry_point("generate")
    g.add_edge("generate", END)

    app = g.compile()
    render_graph_mermaid(app, "01_minimal_graph")
    out = app.invoke({"topic": "LangGraph", "answer": ""})
    print(out["answer"])

if __name__ == "__main__":
    main()
