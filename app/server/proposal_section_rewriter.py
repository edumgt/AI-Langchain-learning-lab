from __future__ import annotations
import json
from typing import Dict

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.server.proposal_template import SECTIONS
from app.server.proposal_table_fillers import build_tables_block

class SectionDraft(BaseModel):
    executive_summary: str = Field(default="")
    context_goal: str = Field(default="")
    audience_strategy: str = Field(default="")
    kpi_measurement: str = Field(default="")
    activation: str = Field(default="")
    risk_compliance: str = Field(default="")
    appendix_sources: str = Field(default="")

def rewrite_sections_llm(
    sponsor_name: str,
    campaign_title: str,
    tool_data: dict,
    used_docs: list,
    base_notes: str = "",
) -> tuple[dict, dict]:
    """LLM rewrites narrative sections only. Tables are filled deterministically."""
    tables = build_tables_block(tool_data)
    doc_snips = "\n".join([f"- {d.get('preview','')}" for d in (used_docs or [])][:2])

    llm = build_chat_model(temperature=0.2).with_structured_output(SectionDraft)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "너는 예술경영 후원 제안서 작성자다.\n"
         "규칙:\n"
         "1) 숫자/금액/기간은 TOOL_DATA와 TABLES를 절대 벗어나지 말 것(추측 금지)\n"
         "2) 서술 섹션만 작성한다(표는 작성하지 말 것)\n"
         "3) 각 서술 섹션 마지막 문장에 (SOURCE 1) 또는 (SOURCE 2)를 1회 이상 넣는다. appendix_sources에는 SOURCE 1/2 목록을 남긴다\n"
         "4) 한국어로, 간결하고 실행 가능한 문장\n"),
        ("human",
         "SPONSOR={sponsor}\nCAMPAIGN={campaign}\n\n"
         "TOOL_DATA(JSON):\n{tool_data}\n\n"
         "TABLES(결정론):\n{tables}\n\n"
         "DOC_SNIPS:\n{doc_snips}\n\n"
         "BASE_NOTES(있으면 참고):\n{base_notes}\n\n"
         "출력 스키마 섹션별 본문만 생성: executive_summary, context_goal, audience_strategy, kpi_measurement, activation, risk_compliance, appendix_sources"),
    ])

    out = (prompt | llm).invoke({
        "sponsor": sponsor_name,
        "campaign": campaign_title,
        "tool_data": json.dumps(tool_data, ensure_ascii=False, indent=2),
        "tables": json.dumps(tables, ensure_ascii=False, indent=2),
        "doc_snips": doc_snips,
        "base_notes": base_notes or "",
    })
    data = out.model_dump()

    # ensure sources exist
    if "SOURCE 1" not in (data.get("appendix_sources") or ""):
        data["appendix_sources"] = (
            (data.get("appendix_sources","") or "").strip()
            + "\n- SOURCE 1: (문서 인용)\n- SOURCE 2: (문서 인용)\n"
        ).strip()

    return data, tables

def assemble_fixed_template_md(
    sponsor_name: str,
    campaign_title: str,
    narratives: dict,
    tables: dict,
) -> str:
    """Assemble fixed template headings + deterministic tables."""
    lines = ["# 후원 제안서 (고정 템플릿 v14)", ""]

    section_map = {
        "executive_summary": narratives.get("executive_summary","(작성)"),
        "context_goal": narratives.get("context_goal","(작성)"),
        "audience_strategy": narratives.get("audience_strategy","(작성)"),
        "sponsorship_package": tables.get("package_table",""),
        "kpi_measurement": narratives.get("kpi_measurement","(작성)"),
        "timeline": tables.get("timeline_table",""),
        "budget": tables.get("budget_table",""),
        "activation": narratives.get("activation","(작성)"),
        "risk_compliance": narratives.get("risk_compliance","(작성)"),
        "appendix_sources": narratives.get("appendix_sources","- SOURCE 1: ...\n- SOURCE 2: ..."),
    }

    for s in SECTIONS:
        lines.append(f"## {s.title}")
        content = section_map.get(s.key, "(작성)")
        lines.append((content or "(작성)").strip())
        lines.append("")

    return "\n".join(lines).strip() + "\n"
