"""Retry / Fallback (간단 패턴)."""
from rich import print
from langchain_core.runnables import RunnableLambda
from app.utils.console import header

def main():
    header("LCEL 05 — retry/fallback 아이디어")

    # 실제 네트워크/모델 실패를 강제로 만들기 어렵기 때문에,
    # 여기서는 예외가 나면 fallback을 실행하는 패턴을 보여준다.
    def may_fail(x):
        if x.get("ok") is False:
            raise ValueError("forced error")
        return "success"

    primary = RunnableLambda(may_fail)
    fallback = RunnableLambda(lambda x: "fallback-result")

    try:
        print(primary.invoke({"ok": False}))
    except Exception:
        print(fallback.invoke({"ok": False}))

if __name__ == "__main__":
    main()
