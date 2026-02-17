"""리스트 스키마: wrapper 모델."""
from rich import print
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header
from catalog.structured._schemas import SponsorPackage, SponsorPackageList

def main():
    header("STRUCTURED 02 — list schema")
    llm = build_chat_model(temperature=0).with_structured_output(SponsorPackageList)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "반드시 packages 배열로 2개를 반환하라."),
        ("human", "공연 프로젝트 후원 패키지 2개를 packages에 넣어줘."),
    ])

    out = (prompt | llm).invoke({})
    for p in out.packages:
        print(p.model_dump())

if __name__ == "__main__":
    main()
