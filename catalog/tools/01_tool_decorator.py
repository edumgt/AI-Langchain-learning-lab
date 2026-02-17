"""@tool 데코레이터 기본."""
from rich import print
from langchain_core.tools import tool
from app.utils.console import header

@tool
def budget_split(total_krw: int, n: int) -> dict:
    """예산을 n개 항목으로 균등 분배"""
    each = total_krw // max(n,1)
    return {"each": each, "total": total_krw, "n": n}

def main():
    header("TOOLS 01 — @tool")
    print(budget_split.invoke({"total_krw": 30000000, "n": 3}))

if __name__ == "__main__":
    main()
