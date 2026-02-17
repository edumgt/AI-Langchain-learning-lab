"""llm.with_structured_output(Pydantic)"""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class SponsorPackage(BaseModel):
    title: str = Field(description="패키지명")
    price_krw: int = Field(description="가격(원)")
    benefits: list[str] = Field(description="혜택")
    risks: list[str] = Field(description="리스크")

def main():
    header("STRUCTURED 01 — with_structured_output")
    llm = build_chat_model(temperature=0)
    sllm = llm.with_structured_output(SponsorPackage)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "스키마를 만족하는 데이터로만 답하라."),
        ("human", "지역 전시 후원 패키지 1개를 제안해줘."),
    ])

    obj = (prompt | sllm).invoke({})
    print(obj.model_dump())

if __name__ == "__main__":
    main()
