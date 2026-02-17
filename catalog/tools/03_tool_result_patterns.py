"""Tools 03 — Tool result patterns (추천 패턴 모음)

학습 포인트:
1) Tool 결과를 '구조화'해서 LLM이 후속 작업(요약/표/리포트)에 쓰기 쉽게 만들기
2) Tool 결과를 그대로 user에게 노출하지 말고, 후처리(chain)로 정제하기
"""
from rich import print
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from app.core.llm_factory import build_chat_model
from app.utils.console import header

@tool
def calc_media_plan(total_krw: int) -> dict:
    """간단한 미디어 플랜 계산(학습용)."""
    return {
        "ads_paid": int(total_krw * 0.5),
        "content_prod": int(total_krw * 0.3),
        "events": int(total_krw * 0.2),
    }

def main():
    header("TOOLS 03 — Tool result patterns")
    llm = build_chat_model(temperature=0)
    llm_tools = llm.bind_tools([calc_media_plan])

    prompt = ChatPromptTemplate.from_messages([
        ("system","필요하면 툴을 호출해 숫자를 얻고, 표로 정리해라."),
        ("human","예산 30000000원 관객개발 캠페인 예산 배분안을 표로."),
    ])

    # 1) 모델이 툴 콜 -> (백엔드가 자동 실행할 수도/아닐 수도)
    resp = (prompt | llm_tools).invoke({})

    # 2) 후처리 패턴: content만 뽑아서 안전하게 표시
    def safe_text(msg):
        return getattr(msg, "content", str(msg))

    post = RunnableLambda(lambda x: safe_text(x))
    out = post.invoke(resp)

    print(out)

if __name__ == "__main__":
    main()
