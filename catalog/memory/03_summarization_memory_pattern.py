"""Summarization memory 패턴: 오래된 대화를 요약해서 축약 저장."""
from rich import print
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("MEMORY 03 — Summarization memory (패턴)")
    llm = build_chat_model(temperature=0.2)

    conversation = [
        "사용자: 우리는 지역 공공문화재단이다.",
        "사용자: 2026년 상반기 관객개발 목표가 있다.",
        "사용자: 예산은 3천만원이다.",
        "사용자: 지역 커뮤니티 협업을 넣고 싶다.",
        "어시스턴트: (여러 답변들...)",
    ]

    # 요약을 별도 'state'로 저장하는 패턴
    prompt = [
        {"role":"system","content":"아래 대화를 5줄 이내의 '요약 상태'로 만들어라."},
        {"role":"user","content":"\n".join(conversation)},
    ]
    resp = llm.invoke(prompt)
    summary_state = getattr(resp,"content",str(resp))
    print("[bold]Summary state[/bold]\n", summary_state)

    # 이후 질문은 summary_state + 최근 메시지로 처리
    follow = llm.invoke([
        {"role":"system","content":"요약 상태를 참고해 답하라:\n"+summary_state},
        {"role":"user","content":"이 조건으로 KPI 5개만 추천해줘."},
    ])
    print("\n[bold]Answer[/bold]\n", getattr(follow,"content",str(follow)))

if __name__ == "__main__":
    main()
