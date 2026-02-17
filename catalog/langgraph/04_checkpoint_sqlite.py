"""LangGraph 04 — SQLite Checkpointing (상태 저장/복구)

학습 포인트:
- 체크포인터를 통해 그래프 실행 상태를 저장하고,
  동일 thread_id로 이어서 실행할 수 있음(재시도/중단 복구)

주의:
- API는 버전에 따라 달라질 수 있습니다.
"""
from __future__ import annotations
from typing import TypedDict
from rich import print

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.llm_factory import build_chat_model
from app.utils.console import header

class State(TypedDict):
    topic: str
    answer: str

def main():
    header("LANGGRAPH 04 — SQLite checkpointing")
    llm = build_chat_model()

    def node(state: State) -> State:
        resp = llm.invoke([{"role":"user","content": f"{state['topic']}를 2문장으로 설명해줘."}])
        return {**state, "answer": getattr(resp, "content", str(resp))}

    g = StateGraph(State)
    g.add_node("node", node)
    g.set_entry_point("node")
    g.add_edge("node", END)

    saver = SqliteSaver.from_conn_string("/app/storage/langgraph_checkpoint.sqlite")
    app = g.compile(checkpointer=saver)

    config = {"configurable": {"thread_id": "demo-thread"}}
    out1 = app.invoke({"topic": "LCEL", "answer": ""}, config=config)
    print("[bold]run1[/bold]\n", out1["answer"])

    # 동일 thread_id로 다시 invoke하면 체크포인트가 남아있는 상태에서 이어붙일 수 있음(패턴 학습)
    out2 = app.invoke({"topic": "LangGraph", "answer": ""}, config=config)
    print("\n[bold]run2[/bold]\n", out2["answer"])

if __name__ == "__main__":
    main()
