"""LANGGRAPH 08 — HITL approval with CLI pause (TTY가 있으면 실제 입력)

목표:
- 사람이 승인할 때까지 '대기'하는 패턴을 카탈로그로 제공
- Docker compose run -it 로 실행하면 실제 입력 가능

실행 예:
  docker compose run --rm -it lab python catalog/langgraph/08_hitl_cli_pause.py

비대화형 환경이면(auto):
- AUTO_APPROVE=true면 자동 통과
- 아니면 block 처리
"""
from __future__ import annotations
import os, sys
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
    header("LANGGRAPH 08 — HITL CLI pause")
    llm = build_chat_model(temperature=0.2)

    auto = (os.getenv("AUTO_APPROVE","true").lower() == "true")

    def draft_node(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"너는 기획자다. 실행 초안을 만든다."},
            {"role":"user","content": s["q"]},
        ])
        return {**s, "draft": getattr(resp,"content",str(resp))}

    def approve_node(s: State) -> State:
        if auto:
            return {**s, "approved": True, "reason":"AUTO_APPROVE=true"}
        if sys.stdin.isatty():
            print("\n[bold yellow]승인 필요[/bold yellow]")
            print("아래 초안을 확인하고 승인하려면 'YES' 입력:")
            print("--- DRAFT ---")
            print(s["draft"][:1200])
            ans = input("\nApprove? (YES/no): ").strip().upper()
            return {**s, "approved": (ans == "YES"), "reason": f"tty input={ans}"}
        return {**s, "approved": False, "reason":"non-tty and AUTO_APPROVE=false"}

    def route(s: State) -> Literal["finalize","block"]:
        return "finalize" if s["approved"] else "block"

    def finalize(s: State) -> State:
        resp = llm.invoke([
            {"role":"system","content":"초안을 최종 실행 계획 문서로 다듬어라(표/체크리스트 포함)."},
            {"role":"user","content": f"DRAFT:\n{s['draft']}"},
        ])
        return {**s, "final": getattr(resp,"content",str(resp))}

    def block(s: State) -> State:
        return {**s, "final": f"승인이 완료되지 않았습니다. ({s['reason']})\n\n초안을 검토 후 다시 실행하거나 AUTO_APPROVE=true로 설정하세요."}

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
    render_graph_mermaid(app, "08_hitl_cli_pause")
    out = app.invoke({"q":"예산 3천만원으로 2주 관객개발 캠페인 실행계획 작성", "draft":"", "approved": False, "final":"", "reason":""})
    print("\n[bold]FINAL[/bold]\n", out["final"])

if __name__ == "__main__":
    main()
