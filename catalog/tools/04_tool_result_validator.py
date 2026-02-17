"""TOOLS 04 — Tool result validator (Pydantic) 단독 데모

학습 포인트:
- 툴 결과는 외부 시스템/코드에서 오므로 신뢰하면 안 됨
- Pydantic으로 스키마 검증 -> 정상일 때만 후속 체인/응답에 사용
"""
from rich import print
from pydantic import BaseModel, ValidationError
from app.utils.console import header

class BudgetPlan(BaseModel):
    ads_paid: int
    content_prod: int
    events: int
    total: int

def main():
    header("TOOLS 04 — Pydantic validate tool outputs")

    good = {"ads_paid":15000000, "content_prod":9000000, "events":6000000, "total":30000000}
    bad = {"ads_paid":"fifteen million", "total":30000000}

    print("[bold]GOOD[/bold]", BudgetPlan(**good).model_dump())

    try:
        BudgetPlan(**bad)
    except ValidationError as e:
        print("[bold red]BAD rejected[/bold red]")
        print(e)

if __name__ == "__main__":
    main()
