from __future__ import annotations
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

class Route(BaseModel):
    route: str = Field(description="one of: strategy, marketing, fundraising, ops")
    reason: str = Field(description="why this route")

def main():
    header("09) Router — 질문을 도메인별 체인으로 분기")
    show_provider()

    llm = build_chat_model(temperature=0)

    router_prompt = ChatPromptTemplate.from_messages([
        ("system", "질문을 가장 적절한 route로 분류하라. route는 strategy/marketing/fundraising/ops 중 하나."),
        ("human", "{q}"),
    ])

    router = (router_prompt | llm.with_structured_output(Route))

    def strategy_chain(q: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "너는 전략 컨설턴트다. 미션/비전/로드맵 중심으로 답한다."),
            ("human", "{q}"),
        ])
        return getattr((prompt | llm).invoke({"q": q}), "content", "")

    def marketing_chain(q: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "너는 마케팅 리드다. 퍼널/콘텐츠/채널/캠페인 구조로 답한다."),
            ("human", "{q}"),
        ])
        return getattr((prompt | llm).invoke({"q": q}), "content", "")

    def fundraising_chain(q: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "너는 후원/재원조달 전문가다. 패키지/제안서/파트너십/KPI로 답한다."),
            ("human", "{q}"),
        ])
        return getattr((prompt | llm).invoke({"q": q}), "content", "")

    def ops_chain(q: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "너는 운영/재무 담당이다. 예산/일정/리스크/컴플라이언스를 포함해 답한다."),
            ("human", "{q}"),
        ])
        return getattr((prompt | llm).invoke({"q": q}), "content", "")

    dispatch = {
        "strategy": strategy_chain,
        "marketing": marketing_chain,
        "fundraising": fundraising_chain,
        "ops": ops_chain,
    }

    def route_and_answer(q: str) -> str:
        r = router.invoke({"q": q})
        fn = dispatch.get(r.route, ops_chain)
        ans = fn(q)
        return f"[ROUTE] {r.route} — {r.reason}\n\n{ans}"

    chain = RunnableLambda(route_and_answer)

    q = "지역 커뮤니티와 협업하는 관객개발 캠페인을 설계해줘. SNS와 오프라인을 같이 쓰고 싶어."
    print(chain.invoke(q))

if __name__ == "__main__":
    main()
