from __future__ import annotations
import os, json
from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core import settings
from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, vectorstore
from app.server.store import create_action
from app.tools.schemas import BudgetSplitRequest, TimelineRequest, SponsorshipPackageRequest
from app.tools.impl import budget_split, timeline, sponsorship_package


class Route(BaseModel):
    mode: Literal["chat","rag","plan"] = Field(description="처리 모드")
    need_approval: bool = Field(description="승인 필요 여부")
    action_type: str = Field(default="none", description="none|publish|email|budget_commit 등")
    reason: str

def route(q: str) -> Route:
    llm = build_chat_model(temperature=0).with_structured_output(Route)
    p = ChatPromptTemplate.from_messages([
        ("system",
         "너는 예술경영 도우미 라우터다.\n"
         "- 일반 설명/아이디어면 mode=chat\n"
         "- 내부 문서 근거가 필요한 질문이면 mode=rag\n"
         "- 실행 계획/예산/일정/체크리스트면 mode=plan\n"
         "- 외부로 발행/공개(보도자료, 공지, 이메일 발송, 예산 확정 등)은 need_approval=true, action_type 지정\n"
         "반드시 스키마로만 답하라."),
        ("human","{q}")
    ])
    return (p | llm).invoke({"q": q})

def answer_chat(q: str) -> tuple[str, list[dict]]:
    llm = build_chat_model(temperature=0.2)
    resp = llm.invoke([{"role":"system","content":"너는 예술경영전문가 조력자다."},
                       {"role":"user","content": q}])
    return getattr(resp,"content",str(resp)), []

def answer_rag(q: str, top_k: int | None = None) -> tuple[str, list[dict]]:
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    k = top_k or settings.TOP_K
    docs = vs.similarity_search(q, k=k)
    context = "\n\n".join(d.page_content for d in docs)

    llm = build_chat_model(temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system","너는 CONTEXT 기반으로만 답한다. CONTEXT에 없으면 '근거 부족'이라고 답한다. 마지막에 '근거' 섹션에 SOURCE 1~2를 인용."),
        ("human","CONTEXT:\n{context}\n\nQ:\n{q}")
    ])
    resp = (prompt | llm).invoke({"context": "\n\n".join([f"SOURCE {i+1}: {d.page_content}" for i,d in enumerate(docs[:2])]),
                                 "q": q})
    used = [{"meta": d.metadata, "preview": d.page_content[:200]} for d in docs[:3]]
    return getattr(resp,"content",str(resp)), used

def answer_plan(q: str) -> tuple[str, list[dict]]:
    """Tool-assisted plan.

    - 예산/타임라인/후원 패키지 같은 구조 데이터는 툴로 산출
    - LLM은 TOOL_DATA를 기반으로 문서화
    """
    # heuristic tool calls (학습용): 질문에 키워드가 있으면 해당 툴을 실행
    tool_data = {}
    if any(k in q for k in ["예산", "budget", "원", "KRW"]):
        tool_data["budget_split"] = budget_split(BudgetSplitRequest(total_krw=30000000)).model_dump()
    if any(k in q for k in ["2주", "weeks", "일정", "timeline"]):
        tool_data["timeline"] = timeline(TimelineRequest(start_date="2026-02-17", weeks=2, goal="관객개발 캠페인")).model_dump()
    if any(k in q for k in ["후원", "스폰서", "sponsor", "패키지"]):
        tool_data["sponsorship_package"] = sponsorship_package(SponsorshipPackageRequest(tier_count=3, total_target_krw=30000000, org_type="general")).model_dump()

    llm = build_chat_model(temperature=0.2)
    resp = llm.invoke([
        {"role":"system","content":"너는 예술경영 실행 PM이다. 아래 TOOL_DATA를 근거로 2주 실행계획을 표/체크리스트/리스크로 구성해라. TOOL_DATA 밖 숫자는 추측하지 말라."},
        {"role":"user","content": f"Q: {q}

TOOL_DATA:
{json.dumps(tool_data, ensure_ascii=False, indent=2)}"},
    ])
    return getattr(resp,"content",str(resp)), []

def run(q: str, mode: str | None = None, top_k: int | None = None, auto_approve: bool | None = None):
    r = route(q)
    chosen = mode or r.mode

    # approval policy (env default)
    if auto_approve is None:
        auto_approve = (os.getenv("AUTO_APPROVE","true").lower() == "true")
    if r.need_approval and not auto_approve:
        action = create_action({"q": q, "suggested_mode": chosen, "action_type": r.action_type, "reason": r.reason})
        return {"answer": f"승인이 필요한 작업으로 분류되었습니다(action_type={r.action_type}). /approve 로 승인 후 진행하세요.",
                "mode": chosen, "used_docs": [], "pending_action": action}

    if chosen == "chat":
        ans, used = answer_chat(q)
    elif chosen == "plan":
        ans, used = answer_plan(q)
    else:
        ans, used = answer_rag(q, top_k=top_k)

    return {"answer": ans, "mode": chosen, "used_docs": used, "pending_action": None}
