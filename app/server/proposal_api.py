from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate

from app.core import settings
from app.core.llm_factory import build_chat_model
from app.core.rag_utils import ingest_dir_meta, vectorstore

router = APIRouter(prefix="/artbiz", tags=["artbiz"])

class ProposalRequest(BaseModel):
    sponsor_name: str = Field(min_length=1)
    campaign_title: str = Field(min_length=1)
    org_type: Literal["museum","theatre","festival","foundation","gallery","general"] = "general"
    budget_target_krw: int = Field(gt=0)
    constraints: list[str] = Field(default_factory=list)
    need_approval: bool = True

class ProposalResponse(BaseModel):
    proposal_markdown: str
    risks: list[str]
    used_docs: list[dict]

@router.post("/proposal", response_model=ProposalResponse)
def proposal(req: ProposalRequest):
    # ensure index
    ingest_dir_meta(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    # retrieve supporting docs
    q = f"{req.org_type} 후원 패키지 혜택 KPI 개인정보 보도자료 유의사항"
    docs = vs.similarity_search(q, k=4)

    context = "\n\n".join([f"SOURCE {i+1}: {d.page_content}" for i, d in enumerate(docs[:2])])

    # risk checklist (deterministic)
    risks = [
        "개인정보/초상권 수집 시 동의 문구 및 보관기간 명시 필요",
        "후원 혜택의 과장/확정되지 않은 노출 약속 금지(계약서 기준)",
        "브랜드/로고 사용 가이드(사이즈/색상/배치) 준수 필요",
        "현장 운영(부스/배너) 안전/동선/인허가 체크 필요",
    ]
    if req.need_approval:
        risks.append("외부 발행물(보도자료/공지/대외메일)은 HITL 승인 후 배포 권장")

    llm = build_chat_model(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "너는 예술경영 후원 제안서 작성자다.\n"
         "- 반드시 Markdown으로 작성\n"
         "- 숫자/금액은 입력값만 사용(추측 금지)\n"
         "- '근거' 섹션에 SOURCE 1~2 인용\n"
         "- '리스크 체크' 섹션에 제공된 RISKS를 반영"),
        ("human",
         "SPONSOR:{sponsor}\nCAMPAIGN:{campaign}\nORG_TYPE:{org_type}\nBUDGET_TARGET_KRW:{budget}\n"
         "CONSTRAINTS:{constraints}\n\nCONTEXT:\n{context}\n\nRISKS:\n{risks}\n\n"
         "요청: 1) 요약 2) 제안 구조(티어/혜택/KPI) 3) 실행 일정(2주) 4) 측정/리포트 5) 리스크 체크 6) 근거"),
    ])

    resp = (prompt | llm).invoke({
        "sponsor": req.sponsor_name,
        "campaign": req.campaign_title,
        "org_type": req.org_type,
        "budget": f"{req.budget_target_krw}",
        "constraints": ", ".join(req.constraints) if req.constraints else "없음",
        "context": context,
        "risks": "\n".join([f"- {r}" for r in risks]),
    })

    used = [{"meta": d.metadata, "preview": d.page_content[:200]} for d in docs[:3]]
    return ProposalResponse(proposal_markdown=getattr(resp,"content",str(resp)), risks=risks, used_docs=used)
