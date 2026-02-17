"""Multi-prompt routing pattern."""
from rich import print
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from app.core.llm_factory import build_chat_model
from app.utils.console import header

class Route(BaseModel):
    route: str
    reason: str

def main():
    header("ROUTERS 02 — Multi-prompt router pattern")
    base_llm = build_chat_model(temperature=0)
    router_llm = base_llm.with_structured_output(Route)

    router_prompt = ChatPromptTemplate.from_messages([
        ("system","route는 strategy/marketing/fundraising/ops 중 하나."),
        ("human","{q}"),
    ])

    def make_chain(system_msg: str):
        return ChatPromptTemplate.from_messages([
            ("system", system_msg),
            ("human","{q}"),
        ]) | base_llm

    chains = {
        "strategy": make_chain("너는 전략 컨설턴트다. 미션/비전/로드맵 중심."),
        "marketing": make_chain("너는 마케팅 리드다. 퍼널/채널/콘텐츠/캠페인."),
        "fundraising": make_chain("너는 후원 전문가다. 패키지/제안서/KPI/파트너십."),
        "ops": make_chain("너는 운영 담당이다. 예산/일정/리스크/컴플라이언스."),
    }

    def route_and_answer(inp):
        q = inp["q"]
        r = (router_prompt | router_llm).invoke({"q": q})
        ch = chains.get(r.route, chains["ops"])
        ans = ch.invoke({"q": q})
        return f"[ROUTE] {r.route} — {r.reason}\n\n{getattr(ans,'content',str(ans))}"

    chain = RunnableLambda(route_and_answer)
    print(chain.invoke({"q":"지역 커뮤니티와 협업하는 관객개발 캠페인을 2주 안에 실행하려면?"}))

if __name__ == "__main__":
    main()
