"""Structured classification router."""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class Route(BaseModel):
    route: str = Field(description="strategy|marketing|fundraising|ops")
    reason: str

def main():
    header("ROUTERS 01 — Classification router")
    llm = build_chat_model(temperature=0).with_structured_output(Route)

    prompt = ChatPromptTemplate.from_messages([
        ("system","route는 strategy/marketing/fundraising/ops 중 하나."),
        ("human","{q}"),
    ])

    r = (prompt | llm).invoke({"q":"후원제안서를 만들고 싶어. 패키지 구성 도와줘."})
    print(r.model_dump())

if __name__ == "__main__":
    main()
