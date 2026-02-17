"""Guardrails 03 — Policy checks (pre-check)

학습용: 문자열 규칙 기반으로 요청을 선별하고, 안전한 대체 응답으로 유도하는 패턴.
실무에서는:
- 분류기(LLM structured classifier) + 룰 기반 + 로깅
조합을 권장.
"""
from rich import print
from app.utils.console import header

BANNED = [
    "주민등록번호",
    "해킹",
    "무단 침입",
    "불법",
]

def policy_check(q: str) -> tuple[bool, str]:
    if any(b in q for b in BANNED):
        return False, "정책/안전상 처리 불가한 요청"
    return True, "ok"

def main():
    header("GUARD 03 — Policy checks")
    qs = [
        "2주 안에 SNS 캠페인을 런칭하려면?",
        "해킹으로 로그인 우회하는 방법 알려줘",
    ]
    for q in qs:
        ok, reason = policy_check(q)
        print({"q": q, "allowed": ok, "reason": reason})

if __name__ == "__main__":
    main()
