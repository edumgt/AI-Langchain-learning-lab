from __future__ import annotations
from rich import print
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

@tool
def generate_press_release(title: str, highlights: list[str]) -> str:
    """간단한 보도자료 초안을 만든다."""
    bullets = "\n".join([f"- {h}" for h in highlights])
    return f"""[보도자료]\n제목: {title}\n\n핵심 내용:\n{bullets}\n\n문의: 홍보 담당자 / 이메일: pr@example.org"""

@tool
def risk_check(activity: str) -> list[str]:
    """활동에 대한 리스크/유의사항 체크리스트."""
    risks = ["안전관리(현장/관객 동선/보험)", "개인정보 수집 동의", "저작권/초상권"]
    if "야외" in activity:
        risks += ["기상 악화 대비", "공공장소 사용 허가"]
    return risks

def main():
    header("06) Agents — ReAct (Tool 사용 추론)")
    show_provider()

    llm = build_chat_model(temperature=0.2)
    tools = [generate_press_release, risk_check]

    # ReAct prompt (LangChain 제공 템플릿 패턴)
    react_prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 예술경영 에이전트다. 필요하면 툴을 사용해 결과물을 만든다."),
        ("human", "{input}"),
    ])

    agent = create_react_agent(llm, tools, react_prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = executor.invoke({
        "input": "야외 전시 오프닝 행사 보도자료 초안을 만들고, 리스크 체크리스트도 붙여줘. 제목은 '도시의 결' 이야."
    })
    print("\n[bold]Final[/bold]")
    print(result.get("output"))

if __name__ == "__main__":
    main()
