"""작은 회귀 테스트 러너(학습용)."""
from __future__ import annotations
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

CASES = [
    {"q":"후원 패키지 1개 제안", "must_contain":["후원","혜택"]},
    {"q":"관객개발 KPI 3개", "must_contain":["KPI"]},
]

def main():
    header("EVAL 02 — Regression runner (tiny)")
    llm = build_chat_model(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system","간단히 답하라."),
        ("human","{q}"),
    ])
    chain = prompt | llm

    passed = 0
    for c in CASES:
        resp = chain.invoke({"q": c["q"]})
        text = getattr(resp,"content",str(resp))
        ok = all(m in text for m in c["must_contain"])
        print({"q": c["q"], "ok": ok})
        if ok: passed += 1
    print(f"passed {passed}/{len(CASES)}")

if __name__ == "__main__":
    main()
