"""PydanticOutputParser."""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class KPI(BaseModel):
    name: str = Field(description="KPI 이름")
    definition: str = Field(description="정의")

def main():
    header("OUTPUT 03 — PydanticOutputParser")
    llm = build_chat_model(temperature=0)
    parser = PydanticOutputParser(pydantic_object=KPI)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "아래 스키마를 만족하는 값만 출력하라."),
        ("human", "관객개발 KPI 하나만 제시해줘."),
        ("system", "{format_instructions}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser
    obj = chain.invoke({})
    print(obj.model_dump())

if __name__ == "__main__":
    main()
