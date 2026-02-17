"""EVAL 04 — LLM-as-a-Judge (grounding / citation checks)

목표:
- RAG 답변이 CONTEXT에 근거했는지(grounded) LLM으로 판정
- 간단 점수/사유/개선안을 구조화 출력으로 받기

학습 포인트:
- 평가도 체인으로 만들고, 리그레션 리포트에 합칠 수 있음
- 운영에서는 더 정교한 rubric + 다양한 judge 모델 조합을 고려

주의:
- Judge가 완벽하진 않음(확률적). 그러나 회귀 비교/상대 평가에는 유용.
"""
from __future__ import annotations
import json, os, time
from rich import print
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from app.core import settings
from app.core.rag_utils import ingest_dir, vectorstore
from app.core.llm_factory import build_chat_model
from app.utils.console import header

REPORT_PATH = "/app/storage/eval_llm_judge_report.json"

class Judgement(BaseModel):
    grounded: bool = Field(description="답변이 CONTEXT에 충분히 근거하면 true")
    score: int = Field(ge=0, le=10, description="근거 충실도 점수(0~10)")
    rationale: str = Field(description="판정 근거(짧게)")
    missing: list[str] = Field(default_factory=list, description="CONTEXT에 없어서 추측한 것으로 보이는 포인트")
    suggestions: list[str] = Field(default_factory=list, description="개선 제안")

def main():
    header("EVAL 04 — LLM-as-a-Judge (grounding)")
    os.makedirs("/app/storage", exist_ok=True)

    # index + retriever
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    retriever = vs.as_retriever(search_kwargs={"k": settings.TOP_K})

    # answer model
    answer_llm = build_chat_model(temperature=0)

    # judge model (같은 모델로 해도 되지만, 운영은 분리 권장)
    judge_llm = build_chat_model(temperature=0).with_structured_output(Judgement)

    q = "후원 패키지 혜택을 3개로 요약해줘."
    docs = retriever.get_relevant_documents(q)
    context = "\n\n".join(d.page_content for d in docs)

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system","너는 CONTEXT 기반으로만 답한다. CONTEXT에 없으면 '근거 부족'이라고 답한다."),
        ("human","CONTEXT:\n{context}\n\nQ:\n{q}"),
    ])
    answer = (answer_prompt | answer_llm).invoke({"context": context, "q": q})
    answer_text = getattr(answer, "content", str(answer))

    judge_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "너는 엄격한 평가자다.\n"
         "아래 CONTEXT와 ANSWER를 비교해 grounded 여부를 판단하라.\n"
         "- CONTEXT에 없는 구체적 주장/수치/고유명사는 grounded=false 가능\n"
         "- '근거 부족'이라고 정직하게 말하면 grounded=true로 평가 가능\n"
         "- score는 근거 충실도(0~10).\n"
         "반드시 스키마로만 답하라."),
        ("human","CONTEXT:\n{context}\n\nANSWER:\n{answer}\n\nQUESTION:\n{q}"),
    ])

    j = (judge_prompt | judge_llm).invoke({"context": context, "answer": answer_text, "q": q})

    report = {
        "ts": time.time(),
        "question": q,
        "answer_preview": answer_text[:500],
        "judge": j.model_dump(),
        "docs": [{"meta": d.metadata, "preview": d.page_content[:200]} for d in docs[:3]],
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[bold]ANSWER[/bold]\n", answer_text)
    print("\n[bold]JUDGE[/bold]\n", report["judge"])
    print(f"\n[dim]saved: {REPORT_PATH}[/dim]")

if __name__ == "__main__":
    main()
