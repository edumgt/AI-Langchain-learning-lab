"""LLM-as-judge 미니 평가."""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class Score(BaseModel):
    realism: int = Field(ge=1, le=5)
    specificity: int = Field(ge=1, le=5)
    budget_fit: int = Field(ge=1, le=5)
    feedback: str

def main():
    header("EVAL 01 — Mini judge")
    llm = build_chat_model(temperature=0.2)
    judge = llm.with_structured_output(Score)

    q = "예산 3천만원으로 관객개발을 하려면?"
    candidate = "TV 광고를 대규모로 집행하고 유명 연예인 모델을 쓰면 됩니다."

    prompt = ChatPromptTemplate.from_messages([
        ("system","너는 평가자다. 기준: 현실성/구체성/예산 적합성"),
        ("human","Q:{q}\nA:{a}"),
    ])

    score = (prompt | judge).invoke({"q": q, "a": candidate})
    print(score.model_dump())

if __name__ == "__main__":
    main()
