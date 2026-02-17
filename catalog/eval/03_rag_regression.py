"""EVAL 03 — RAG regression runner (golden set)

목표:
- golden 질문 세트를 기반으로
  1) retrieval
  2) context-only answer
  3) 간단 규칙 기반 체크(must_contain)
  을 수행하고 pass rate를 리포트로 저장

학습 포인트:
- RAG 파이프라인을 '회귀 테스트'처럼 돌리는 패턴
- 운영에서는 LLM judge + grounding/citation 검사까지 확장 가능
"""
from __future__ import annotations
import os, json, time
from rich import print
from langchain_core.prompts import ChatPromptTemplate

from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.core.llm_factory import build_chat_model
from app.utils.console import header

GOLDEN_PATH = "/app/data/eval/golden.jsonl"
REPORT_PATH = "/app/storage/eval_rag_report.json"

def main():
    header("EVAL 03 — RAG regression (golden set)")
    os.makedirs("/app/storage", exist_ok=True)

    # ensure index
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    llm = build_chat_model(temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 CONTEXT 기반으로만 답한다. 근거가 부족하면 '근거 부족'이라고 답한다."),
        ("human", "CONTEXT:\n{context}\n\nQ:\n{q}"),
    ])

    cases = []
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))

    results = []
    passed = 0

    for c in cases:
        q = c["question"]
        docs = retriever.get_relevant_documents(q)
        context = "\n\n".join(d.page_content for d in docs)

        resp = (prompt | llm).invoke({"context": context, "q": q})
        text = getattr(resp, "content", str(resp))

        must = c.get("must_contain", [])
        ok = all(m in text for m in must)

        results.append({
            "id": c.get("id"),
            "question": q,
            "ok": ok,
            "must_contain": must,
            "answer_preview": text[:400],
            "docs": [{"meta": d.metadata, "preview": d.page_content[:180]} for d in docs[:3]],
        })
        if ok:
            passed += 1

        print({"id": c.get("id"), "ok": ok})

    report = {
        "total": len(cases),
        "passed": passed,
        "pass_rate": (passed / max(len(cases),1)),
        "ts": time.time(),
        "results": results,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[bold]Report saved[/bold]: {REPORT_PATH}")
    print(f"Pass rate: {passed}/{len(cases)} = {report['pass_rate']:.2f}")

if __name__ == "__main__":
    main()
