"""Guardrails 01 — Schema guard (structured output)

목표:
- 응답을 Pydantic 스키마로 강제해 형식/누락을 줄이는 가드레일 패턴
"""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class CampaignPlan(BaseModel):
    title: str
    budget_krw: int
    channels: list[str]
    steps: list[str] = Field(min_length=3, description="3개 이상 실행 단계")

def main():
    header("GUARD 01 — Schema guard")
    llm = build_chat_model(temperature=0).with_structured_output(CampaignPlan)

    prompt = ChatPromptTemplate.from_messages([
        ("system","스키마를 만족하는 값만 반환하라."),
        ("human","예산 30000000원으로 2주 SNS 캠페인 계획을 만들어줘. title/budget_krw/channels/steps로."),
    ])

    out = (prompt | llm).invoke({})
    print(out.model_dump())

if __name__ == "__main__":
    main()
