from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Literal, Optional, Tuple, List, Dict

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from app.core import settings
from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir, vectorstore
from app.server.store import create_action

from app.tools.schemas import (
    BudgetSplitRequest,
    TimelineRequest,
    SponsorshipPackageRequest,
)
from app.tools.impl import budget_split, timeline, sponsorship_package


# ---------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------

Mode = Literal["chat", "rag", "plan"]


class Route(BaseModel):
    mode: Mode = Field(description="처리 모드: chat|rag|plan")
    need_approval: bool = Field(description="승인 필요 여부")
    action_type: str = Field(default="none", description="none|publish|email|budget_commit 등")
    reason: str = Field(default="", description="선택 근거")


@dataclass
class RAGResult:
    answer: str
    used_docs: List[Dict[str, Any]]


@dataclass
class PlanToolData:
    data: Dict[str, Any]
    notes: List[str]


# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------

_ROUTER_SYSTEM = (
    "너는 예술경영 도우미 라우터다.\n"
    "- 일반 설명/아이디어면 mode=chat\n"
    "- 내부 문서 근거가 필요한 질문이면 mode=rag\n"
    "- 실행 계획/예산/일정/체크리스트면 mode=plan\n"
    "- 외부로 발행/공개(보도자료, 공지, 이메일 발송, 예산 확정 등)은 need_approval=true, action_type 지정\n"
    "반드시 스키마(JSON)로만 답하라."
)


def route(q: str) -> Route:
    """Route user question into chat/rag/plan with approval policy.

    NOTE:
    - Some local LLM providers (e.g., Ollama via langchain_community) do NOT implement
      `with_structured_output()`. To keep the lab robust, we use a deterministic
      keyword router instead of structured output.
    """
    q_l = (q or "").lower()

    plan_keys = ["예산", "budget", "일정", "timeline", "계획", "체크리스트", "로드맵", "to-do", "실행", "weeks", "2주", "주간"]
    rag_keys = ["근거", "출처", "문서", "자료", "규정", "가이드", "정책", "내부", "첨부", "업로드", "pdf", "보고서"]
    approval_keys = ["발행", "게시", "보도자료", "공지", "대외", "메일", "발송", "예산 확정", "계약", "승인", "공개", "배포"]

    # mode decision
    if any(k in q for k in plan_keys) or any(k in q_l for k in plan_keys):
        mode: Mode = "plan"
        reason = "실행 계획/예산/일정 키워드 감지"
    elif any(k in q for k in rag_keys) or any(k in q_l for k in rag_keys):
        mode = "rag"
        reason = "문서/근거/정책 키워드 감지"
    else:
        mode = "chat"
        reason = "일반 상담/아이디어 요청으로 판단"

    need_approval = any(k in q for k in approval_keys) or any(k in q_l for k in approval_keys)

    action_type = "none"
    if need_approval:
        if "메일" in q or "email" in q_l:
            action_type = "email"
        elif "예산" in q and ("확정" in q or "commit" in q_l):
            action_type = "budget_commit"
        else:
            action_type = "publish"

    return Route(mode=mode, need_approval=need_approval, action_type=action_type, reason=reason)


# ---------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------

def answer_chat(q: str) -> Tuple[str, List[Dict[str, Any]]]:
    llm = build_chat_model(temperature=0.2)
    resp = llm.invoke(
        [
            {"role": "system", "content": "너는 예술경영전문가 조력자다. 과장하지 말고, 실행 가능한 조언을 준다."},
            {"role": "user", "content": q},
        ]
    )
    return getattr(resp, "content", str(resp)), []


# ---------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------

_RAG_SYSTEM = (
    "너는 CONTEXT 기반으로만 답한다.\n"
    "- CONTEXT에 근거가 없으면 '근거 부족'이라고 답한다.\n"
    "- 마지막에 '근거' 섹션을 만들고 SOURCE 1~2를 짧게 인용/요약한다.\n"
    "- 숫자/사실은 CONTEXT에서만 가져온다."
)


def _build_rag_context(docs: list[Any], max_sources: int = 2) -> str:
    """Make a compact context with SOURCE markers."""
    picked = docs[:max_sources]
    parts = []
    for i, d in enumerate(picked, start=1):
        parts.append(f"SOURCE {i}:\n{d.page_content}")
    return "\n\n".join(parts)


def answer_rag(q: str, top_k: Optional[int] = None) -> Tuple[str, List[Dict[str, Any]]]:
    # 1) Ensure docs are ingested
    ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    # 2) Search
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    k = int(top_k or settings.TOP_K)
    docs = vs.similarity_search(q, k=k)

    # 3) Prompt
    llm = build_chat_model(temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _RAG_SYSTEM),
            ("human", "CONTEXT:\n{context}\n\nQ:\n{q}"),
        ]
    )

    context = _build_rag_context(docs, max_sources=2)
    resp = (prompt | llm).invoke({"context": context, "q": q})

    used = [
        {"meta": getattr(d, "metadata", {}), "preview": (d.page_content or "")[:200]}
        for d in docs[:3]
    ]
    return getattr(resp, "content", str(resp)), used


# ---------------------------------------------------------------------
# Plan (tool-assisted)
# ---------------------------------------------------------------------

_PLAN_SYSTEM = (
    "너는 예술경영 실행 PM이다.\n"
    "아래 TOOL_DATA(JSON)만 근거로 2주 실행계획을 작성해라.\n"
    "- TOOL_DATA 밖 숫자는 추측하지 말라.\n"
    "- 출력 형식: 1) 요약 2) 2주 실행계획 표 3) 체크리스트 4) 리스크/대응 5) 필요 승인 항목\n"
)


def _collect_tool_data(q: str) -> PlanToolData:
    """Heuristic tool calls for learning/demo purposes."""
    data: Dict[str, Any] = {}
    notes: List[str] = []

    # Budget
    if any(k in q for k in ["예산", "budget", "원", "KRW"]):
        try:
            data["budget_split"] = budget_split(
                BudgetSplitRequest(total_krw=30_000_000)
            ).model_dump()
        except Exception as e:
            notes.append(f"budget_split tool failed: {e!r}")

    # Timeline
    if any(k in q for k in ["2주", "weeks", "일정", "timeline"]):
        try:
            data["timeline"] = timeline(
                TimelineRequest(start_date="2026-02-17", weeks=2, goal="관객개발 캠페인")
            ).model_dump()
        except Exception as e:
            notes.append(f"timeline tool failed: {e!r}")

    # Sponsorship package
    if any(k in q for k in ["후원", "스폰서", "sponsor", "패키지"]):
        try:
            data["sponsorship_package"] = sponsorship_package(
                SponsorshipPackageRequest(
                    tier_count=3,
                    total_target_krw=30_000_000,
                    org_type="general",
                )
            ).model_dump()
        except Exception as e:
            notes.append(f"sponsorship_package tool failed: {e!r}")

    if not data:
        notes.append(
            "TOOL_DATA가 비어 있습니다. 질문에 예산/일정/후원 같은 키워드가 없거나, 추가 정보가 필요합니다."
        )

    return PlanToolData(data=data, notes=notes)


def answer_plan(q: str) -> Tuple[str, List[Dict[str, Any]]]:
    tool = _collect_tool_data(q)

    tool_payload = {
        "tool_data": tool.data,
        "tool_notes": tool.notes,
    }
    tool_json = json.dumps(tool_payload, ensure_ascii=False, indent=2)

    llm = build_chat_model(temperature=0.2)

    user_content = (
        f"Q: {q}\n\n"
        "요구사항:\n"
        "- 2주 실행계획(주차/일자 단위)\n"
        "- 역할(R&R)과 산출물\n"
        "- 체크리스트\n"
        "- 리스크와 대응\n\n"
        "TOOL_DATA(JSON):\n"
        f"{tool_json}\n"
    )

    resp = llm.invoke(
        [
            {"role": "system", "content": _PLAN_SYSTEM},
            {"role": "user", "content": user_content},
        ]
    )

    # plan 모드는 tool metadata를 used_docs에 남겨서 UI에서 확인 가능하게
    used = [{"meta": {"source": "tools"}, "preview": tool_json[:400]}]
    return getattr(resp, "content", str(resp)), used


# ---------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------

def run(
    q: str,
    mode: Optional[Mode] = None,
    top_k: Optional[int] = None,
    auto_approve: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Entry point used by API.
    Returns a stable response schema for UI consumers.
    """
    r = route(q)
    chosen: Mode = mode or r.mode

    # approval policy (env default)
    if auto_approve is None:
        auto_approve = (os.getenv("AUTO_APPROVE", "true").lower() == "true")

    if r.need_approval and not auto_approve:
        action = create_action(
            {
                "q": q,
                "suggested_mode": chosen,
                "action_type": r.action_type,
                "reason": r.reason,
            }
        )
        return {
            "answer": (
                f"승인이 필요한 작업으로 분류되었습니다(action_type={r.action_type}). "
                "(/approve로 승인 후 진행)"
            ),
            "mode": chosen,
            "used_docs": [],
            "pending_action": action,
        }

    if chosen == "chat":
        ans, used = answer_chat(q)
    elif chosen == "plan":
        ans, used = answer_plan(q)
    else:
        ans, used = answer_rag(q, top_k=top_k)

    return {
        "answer": ans,
        "mode": chosen,
        "used_docs": used,
        "pending_action": None,
    }
