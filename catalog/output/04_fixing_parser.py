"""OutputFixingParser: 파싱 실패를 LLM으로 보정(백엔드에 따라 품질 차)."""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class Plan(BaseModel):
    title: str
    steps: list[str]

def main():
    header("OUTPUT 04 — OutputFixingParser")
    llm = build_chat_model(temperature=0)
    base_parser = PydanticOutputParser(pydantic_object=Plan)
    fixing = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "대충 말하지 말고 계획을 제시해라(일부러 포맷을 흔들어본다)."),
        ("human", "2주짜리 SNS 캠페인 계획을 만들어줘."),
    ])

    raw = (prompt | llm).invoke({})
    text = getattr(raw, "content", str(raw))
    obj = fixing.parse(text)
    print(obj)

if __name__ == "__main__":
    main()
