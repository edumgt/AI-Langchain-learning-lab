from __future__ import annotations
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

class Score(BaseModel):
    correctness: int = Field(ge=1, le=5, description="정확성(1~5)")
    usefulness: int = Field(ge=1, le=5, description="유용성(1~5)")
    grounded: int = Field(ge=1, le=5, description="근거 기반(1~5)")
    feedback: str = Field(description="개선 피드백")

def main():
    header("12) Simple Eval — LLM-as-judge (학습용 미니 평가)")
    show_provider()

    llm = build_chat_model(temperature=0.2)

    # candidate answer (pretend this is your model output)
    question = "예산 3천만원으로 관객개발을 하려면 뭘 해야 해?"
    candidate = """3천만원이면 광고를 많이 집행하고 인플루언서도 대규모로 쓰는 게 좋습니다.
또한 TV 광고를 하면 효과가 큽니다."""

    judge_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 평가자다. 질문/답변을 보고 점수와 피드백을 구조화된 형태로 반환한다."),
        ("human", "QUESTION:\n{q}\n\nCANDIDATE ANSWER:\n{a}\n\n평가 기준: 현실성/예산 적합성/구체성/근거"),
    ])

    judge = llm.with_structured_output(Score)
    score = (judge_prompt | judge).invoke({"q": question, "a": candidate})

    print(score.model_dump())

if __name__ == "__main__":
    main()
