from __future__ import annotations
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

class SponsorPackage(BaseModel):
    title: str = Field(description="후원 패키지 이름")
    target: str = Field(description="타깃 후원사/파트너 유형")
    benefits: list[str] = Field(description="후원 혜택 목록")
    price_krw: int = Field(description="권장 금액(원)")
    risks: list[str] = Field(description="주의/리스크")

def main():
    header("03) Structured Output (Pydantic)")
    show_provider()

    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 예술경영 컨설턴트다. 요구사항을 만족하는 구조화된 답을 만든다."),
        ("human", "지역 전시 프로젝트 후원 패키지 2개를 제안해줘. 예산 규모는 중소기업을 타깃으로."),
    ])

    # LangChain: structured output
    structured_llm = llm.with_structured_output(SponsorPackage)

    chain = prompt | structured_llm
    result = chain.invoke({})

    # result is a SponsorPackage instance (single). We asked 2 packages, so model might return one.
    # For learning: call twice with different instruction or extend to list schema.
    print(result.model_dump())

    # List schema (advanced): define wrapper
    class SponsorPackageList(BaseModel):
        packages: list[SponsorPackage]

    structured_llm2 = llm.with_structured_output(SponsorPackageList)
    chain2 = ChatPromptTemplate.from_messages([
        ("system", "반드시 JSON schema를 만족하는 구조로만 답한다."),
        ("human", "지역 전시 프로젝트 후원 패키지 2개를 제안해줘. packages 배열에 넣어줘."),
    ]) | structured_llm2

    result2 = chain2.invoke({})
    print("\n[bold]packages[/bold]")
    for p in result2.packages:
        print("-", p.model_dump())

if __name__ == "__main__":
    main()
