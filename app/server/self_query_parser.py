from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model

class ParsedQuery(BaseModel):
    rewritten_query: str = Field(description="필터를 제거하고 검색에 적합하게 재작성된 질의")
    doc_type: Optional[Literal["policy","pr","proposal","general"]] = None
    year: Optional[int] = None
    org: Optional[str] = None
    rationale: str = ""

def parse_self_query(q: str) -> ParsedQuery:
    llm = build_chat_model(temperature=0).with_structured_output(ParsedQuery)
    p = ChatPromptTemplate.from_messages([
        ("system",
         "너는 검색 질의 파서다. 사용자의 질문에서 메타데이터 필터를 추출한다.\n"
         "- doc_type은 policy|pr|proposal|general 중 하나 또는 null\n"
         "- year는 4자리 연도 또는 null\n"
         "- org는 기관명 문자열 또는 null\n"
         "- rewritten_query는 필터 조건을 제거하고 '내용 검색'에 적합하게 재작성\n"
         "반드시 스키마로만 답하라."),
        ("human","{q}")
    ])
    return (p | llm).invoke({"q": q})
