from __future__ import annotations
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.server.docs_api import router as docs_router
from app.server.self_query_api import router as rag_router
from app.server.proposal_api import router as artbiz_router
from fastapi.middleware.cors import CORSMiddleware

from app.server.models import ChatRequest, ChatResponse, ApproveRequest, ApproveResponse
from fastapi import UploadFile, File
from app.server.metadata_extractor import build_sidecar_meta
from app.server.self_query_parser import parse_self_query
from app.server.index_queue import enqueue, read_jobs
from app.server.proposal_store import save_markdown, list_versions, mark_approved
from app.server.pdf_renderer import render_markdown_to_pdf
from app.server.proposal_template import template_markdown_skeleton
from app.server.proposal_normalizer import normalize_to_template, check_structure
from app.server.proposal_section_rewriter import rewrite_sections_llm, assemble_fixed_template_md
from app.server.proposal_consistency import overall as consistency_overall
from app.server.proposal_citation_enforcer import enforce_section_citations, citation_placement_check
from app.server.proposal_footnotes import apply_footnotes






from app.server.agent import run, answer_rag, answer_chat, answer_plan
from app.server.store import get_action, update_status

from app.tools.schemas import (
    BudgetSplitRequest, BudgetSplitResponse,
    TimelineRequest, TimelineResponse,
    SponsorshipPackageRequest, SponsorshipPackageResponse,
    ReportRequest, ReportResponse,
)
from app.tools.impl import budget_split, timeline, sponsorship_package, make_report


import shutil

DOCS_DIR = "/app/data/docs"
META_DIR = "/app/data/docs/.meta"
META_INDEX = "/app/data/docs/.meta/index.json"

def _load_index():
    os.makedirs(META_DIR, exist_ok=True)
    if not os.path.exists(META_INDEX):
        with open(META_INDEX, "w", encoding="utf-8") as f:
            json.dump({"docs":[]}, f, ensure_ascii=False, indent=2)
    with open(META_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_index(data):
    os.makedirs(META_DIR, exist_ok=True)
    with open(META_INDEX, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _upsert_doc(meta: dict):
    idx = _load_index()
    docs = idx.get("docs", [])
    docs = [d for d in docs if d.get("filename") != meta.get("filename")]
    docs.append(meta)
    idx["docs"] = sorted(docs, key=lambda x: x.get("filename",""))
    _save_index(idx)
    return idx


app = FastAPI(title="ArtBiz LangChain E2E", version="0.6.0")

app.mount('/', StaticFiles(directory='/app/app/server/static', html=True), name='static')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_router)
app.include_router(rag_router)
app.include_router(artbiz_router)


@app.post("/tools/budget-split", response_model=BudgetSplitResponse)
def tools_budget_split(req: BudgetSplitRequest):
    return budget_split(req)

@app.post("/tools/timeline", response_model=TimelineResponse)
def tools_timeline(req: TimelineRequest):
    return timeline(req)

@app.post("/tools/sponsorship-package", response_model=SponsorshipPackageResponse)
def tools_sponsorship_package(req: SponsorshipPackageRequest):
    return sponsorship_package(req)

@app.post("/tools/report", response_model=ReportResponse)
def tools_report(req: ReportRequest):
    return make_report(req)



@app.post("/docs/upload")
async def docs_upload(file: UploadFile = File(...)):
    os.makedirs(DOCS_DIR, exist_ok=True)
    filename = os.path.basename(file.filename)
    dest = os.path.join(DOCS_DIR, filename)
    with open(dest, "wb") as f:
        f.write(await file.read())

    meta = build_sidecar_meta(dest)
    _upsert_doc(meta)
    return {"ok": True, "meta": meta}

@app.get("/docs")
def docs_list():
    idx = _load_index()
    return idx



@app.post("/rag/self-query")
def rag_self_query(payload: dict):
    # expected: { "q": "...", "top_k": 4 }
    q = payload.get("q","")
    if not q:
        raise HTTPException(400, "q is required")
    top_k = int(payload.get("top_k") or 4)

    parsed = parse_self_query(q)

    # use parsed filters
    from app.core import settings
    from app.core.rag_utils import ingest_dir, vectorstore
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    # chroma where filter
    where = {}
    if parsed.doc_type:
        where["type"] = parsed.doc_type
    if parsed.year:
        where["year"] = parsed.year
    if parsed.org:
        where["org"] = parsed.org

    docs = vs.similarity_search(parsed.rewritten_query, k=top_k, filter=where or None)
    used = [{"meta": d.metadata, "preview": d.page_content[:220]} for d in docs]

    return {
        "q": q,
        "parsed": parsed.model_dump(),
        "where_filter": where,
        "docs": used,
    }



@app.post("/artbiz/proposal")
def artbiz_proposal(payload: dict):
    """Generate sponsor proposal draft.

    Modes:
    - v13 default: LLM draft -> normalize_to_template (rule-based)
    - v14: rewrite_mode='llm_sections' => LLM writes narrative sections, tables filled deterministically from TOOL_DATA

    payload extras:
      - rewrite_mode: 'llm_sections' | 'v13'
      - normalize: bool (default true)
      - save: bool, format: md|pdf|both
      - tags, template_version, logo_path
    """
    sponsor_name = payload.get("sponsor_name","")
    campaign_title = payload.get("campaign_title","")
    budget_total_krw = int(payload.get("budget_total_krw") or 30000000)
    weeks = int(payload.get("weeks") or 2)
    org_type = payload.get("org_type","general")
    auto_approve = payload.get("auto_approve")
    if auto_approve is None:
        auto_approve = (os.getenv("AUTO_APPROVE","true").lower() == "true")

    rewrite_mode = (payload.get("rewrite_mode") or "llm_sections")  # default v14
    normalize_flag = bool(payload.get("normalize", True))

    # tool data
    from app.tools.schemas import BudgetSplitRequest, TimelineRequest, SponsorshipPackageRequest
    from app.tools.impl import budget_split, timeline, sponsorship_package
    tool_data = {
        "budget_split": budget_split(BudgetSplitRequest(total_krw=budget_total_krw)).model_dump(),
        "timeline": timeline(TimelineRequest(start_date=str(datetime.date.today()), weeks=weeks, goal=campaign_title or "관객개발 캠페인")).model_dump(),
        "sponsorship_package": sponsorship_package(SponsorshipPackageRequest(tier_count=3, total_target_krw=budget_total_krw, org_type=org_type)).model_dump(),
    }

    # RAG context
    from app.core import settings
    from app.core.rag_utils import ingest_dir, vectorstore
    _ = ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    vs = vectorstore(settings.CHROMA_PERSIST_DIR, collection="catalog_docs")
    docs = vs.similarity_search("후원 패키지 혜택 KPI 관객개발", k=2)
    used_docs = [{"meta": d.metadata, "preview": d.page_content[:220]} for d in docs]

    # generate draft
    if rewrite_mode == "llm_sections":
        narratives, tables = rewrite_sections_llm(
            sponsor_name=sponsor_name,
            campaign_title=campaign_title,
            tool_data=tool_data,
            used_docs=used_docs,
            base_notes="",
        )
        draft_text = assemble_fixed_template_md(
            sponsor_name=sponsor_name,
            campaign_title=campaign_title,
            narratives=narratives,
            tables=tables,
        )
        # optional normalize (should be already compliant, but keep as safety)
        if normalize_flag:
            draft_text, structure_report = normalize_to_template(draft_text)
        else:
            structure_report = check_structure(draft_text)
    else:
        # fallback to v13 behavior (prompting)
        from app.core.llm_factory import build_chat_model
        from langchain_core.prompts import ChatPromptTemplate
        import json as _json

        context = "\n\n".join([f"SOURCE {i+1}: {d.page_content}" for i, d in enumerate(docs)])
        llm = build_chat_model(temperature=0.2)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "너는 예술경영 후원 제안서 작성자다.\n"
             "- TOOL_DATA의 숫자/구조를 그대로 활용해 제안서를 작성한다(추측 금지).\n"
             "- CONTEXT에서 근거를 찾아 '근거' 섹션에 SOURCE 1~2를 반드시 인용한다.\n"
             "- 마지막에 리스크 체크리스트 포함."),
            ("human",
             "SPONSOR: {sponsor_name}\nCAMPAIGN: {campaign_title}\n\nTOOL_DATA:\n{tool_data}\n\nCONTEXT:\n{context}\n\n"
             "요청: 후원사 맞춤 제안서(요약, 목표, 패키지, KPI, 일정, 예산, 리스크) 작성"),
        ])
        draft = (prompt | llm).invoke({
            "sponsor_name": sponsor_name,
            "campaign_title": campaign_title,
            "tool_data": _json.dumps(tool_data, ensure_ascii=False, indent=2),
            "context": context
        })
        draft_text = getattr(draft, "content", str(draft))
        if normalize_flag:
            draft_text, structure_report = normalize_to_template(draft_text)
        else:
            structure_report = check_structure(draft_text)

    # v15: ensure citations are placed within sections (footnote-like)
    draft_text, citation_enforce_report = enforce_section_citations(draft_text, min_markers_per_section=1)
    citation_placement_report = citation_placement_check(draft_text, min_total_markers=6)
    # v16: convert SOURCE markers to footnotes [1]/[2] and map in appendix
    draft_text, footnote_report = apply_footnotes(draft_text, used_docs)

    # v14: consistency report (tables vs tool_data + sources)
    consistency_report = consistency_overall(draft_text, tool_data)

    # optionally save
    save_flag = bool(payload.get("save", False))
    save_format = (payload.get("format") or "both")
    saved_version = None
    if save_flag:
        meta = save_markdown(
            sponsor_name,
            campaign_title,
            draft_text,
            tool_data=tool_data,
            used_docs=used_docs,
            tags=payload.get("tags") or [],
            template_version=payload.get("template_version"),
        )
        if save_format in ["pdf", "both"]:
            render_markdown_to_pdf(
                draft_text,
                meta["paths"]["pdf"],
                title=f"{sponsor_name} - {campaign_title}",
                meta={
                    "sponsor_name": sponsor_name,
                    "campaign_title": campaign_title,
                    "date": datetime.date.today().isoformat(),
                    "header_left": campaign_title or "ArtBiz Proposal",
                    "logo_path": payload.get("logo_path"),
                },
            )
        saved_version = {"id": meta["id"], "paths": meta["paths"]}

    if not auto_approve:
        from app.server.store import create_action
        action = create_action({
            "action_type": "proposal_publish",
            "sponsor_name": sponsor_name,
            "campaign_title": campaign_title,
            "tool_data": tool_data,
            "draft": draft_text,
            "used_docs": used_docs,
            "saved_version": saved_version,
            "structure_report": structure_report,
            "consistency_report": consistency_report,
            "citation_enforce_report": citation_enforce_report,
            "citation_placement_report": citation_placement_report,
        "footnote_report": footnote_report,
            "footnote_report": footnote_report,
        })
        return {
            "ok": True,
            "pending_action": action,
            "message": "proposal draft created; approve to finalize",
            "saved_version": saved_version,
            "structure_report": structure_report,
            "consistency_report": consistency_report,
            "citation_enforce_report": citation_enforce_report,
            "citation_placement_report": citation_placement_report,
        "footnote_report": footnote_report,
            "footnote_report": footnote_report,
        }

    return {
        "ok": True,
        "proposal": draft_text,
        "tool_data": tool_data,
        "used_docs": used_docs,
        "saved_version": saved_version,
        "structure_report": structure_report,
        "consistency_report": consistency_report,
            "citation_enforce_report": citation_enforce_report,
            "citation_placement_report": citation_placement_report,
        "footnote_report": footnote_report,
            "footnote_report": footnote_report,
        "rewrite_mode": rewrite_mode,
        "citation_enforce_report": citation_enforce_report,
        "citation_placement_report": citation_placement_report,
        "footnote_report": footnote_report,
            "footnote_report": footnote_report,
    }

@app.get("/artbiz/proposals")
def artbiz_proposals():
    return {"ok": True, "items": list_versions(100)}



@app.get("/artbiz/proposal/template")
def artbiz_proposal_template():
    return {"ok": True, "template": template_markdown_skeleton()}

@app.post("/artbiz/proposal/check")
def artbiz_proposal_check(payload: dict):
    md = payload.get("markdown","")
    return {"ok": True, "check": check_structure(md)}


@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    out = run(req.q, mode=req.mode, top_k=req.top_k, auto_approve=req.auto_approve)
    return ChatResponse(**out)

@app.post("/approve", response_model=ApproveResponse)
def approve(req: ApproveRequest):
    action = get_action(req.action_id)
    if not action:
        raise HTTPException(404, "action not found")

    token_env = os.getenv("APPROVE_TOKEN","YES")
    if req.token is not None and req.token != token_env:
        raise HTTPException(403, "invalid token")

    if req.approve:
        update_status(req.action_id, "approved")
        # 실행: 승인된 q를 실제 수행(간단히 suggested_mode대로)
        payload = action["payload"]
        mode = payload.get("suggested_mode","rag")
        q = payload.get("q","")
        if mode == "chat":
            ans, used = answer_chat(q)
        elif mode == "plan":
            ans, used = answer_plan(q)
        else:
            ans, used = answer_rag(q)

        update_status(req.action_id, "done")
        return ApproveResponse(ok=True, message="approved and executed", action={"id": req.action_id, "status":"done", "answer": ans, "used_docs": used})

    update_status(req.action_id, "rejected")
    return ApproveResponse(ok=True, message="rejected", action={"id": req.action_id, "status":"rejected"})
