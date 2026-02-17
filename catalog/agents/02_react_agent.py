"""ReAct Agent 데모."""
from rich import print
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from app.core.llm_factory import build_chat_model
from app.utils.console import header

@tool
def risk_check(activity: str) -> list[str]:
    """활동 리스크 체크"""
    risks = ["안전관리", "개인정보 수집 동의", "저작권/초상권"]
    if "야외" in activity:
        risks += ["기상 악화 대비", "공공장소 허가"]
    return risks

@tool
def draft_press_release(title: str) -> str:
    """보도자료 초안"""
    return f"""[보도자료]\n제목: {title}\n\n- 행사 개요\n- 주요 프로그램\n- 기대 효과\n\n문의: pr@example.org"""

def main():
    header("AGENTS 02 — ReAct Agent")
    llm = build_chat_model(temperature=0.2)
    tools = [risk_check, draft_press_release]

    prompt = ChatPromptTemplate.from_messages([
        ("system","너는 예술경영 에이전트다. 필요하면 툴을 사용해 결과물을 만든다."),
        ("human","{input}"),
    ])

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    out = executor.invoke({"input":"야외 전시 오프닝 행사 보도자료 초안을 만들고, 리스크 체크리스트도 붙여줘. 제목은 '도시의 결'."})
    print("\n[bold]Final[/bold]\n", out.get("output"))

if __name__ == "__main__":
    main()
