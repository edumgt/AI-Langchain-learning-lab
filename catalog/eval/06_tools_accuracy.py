"""EVAL 06 — Tools accuracy / schema checks (v8)

목표:
- 도메인 툴이 스키마를 만족하고(sum/범위) 기본 불변식을 지키는지 테스트
- 운영에서는 더 많은 케이스를 golden으로 늘리고 CI에서 실행

저장:
- /app/storage/eval_tools_report.json
"""
from __future__ import annotations
import json, os, time
from rich import print
from pydantic import ValidationError

from app.tools.schemas import (
    BudgetSplitRequest, BudgetSplitResponse,
    TimelineRequest, TimelineResponse,
    SponsorshipPackageRequest, SponsorshipPackageResponse,
    ReportRequest, ReportResponse,
)
from app.tools.impl import budget_split, timeline, sponsorship_package, make_report
from app.utils.console import header

REPORT = "/app/storage/eval_tools_report.json"

def main():
    header("EVAL 06 — Tools accuracy / schema")
    os.makedirs("/app/storage", exist_ok=True)

    results = []

    # budget split invariants
    b = budget_split(BudgetSplitRequest(total_krw=30000000))
    ok_budget = (b.ads_paid + b.content_prod + b.community + b.contingency) == b.total
    results.append({"case":"budget_sum", "ok": ok_budget, "data": b.model_dump()})

    # timeline basic
    t = timeline(TimelineRequest(start_date="2026-02-17", weeks=2, goal="관객개발"))
    ok_tl = (len(t.items) == 2 and t.items[0].week == 1 and t.items[1].week == 2)
    results.append({"case":"timeline_len", "ok": ok_tl})

    # sponsorship package sum
    p = sponsorship_package(SponsorshipPackageRequest(tier_count=3, total_target_krw=30000000, org_type="festival"))
    ok_pkg = sum(x.price_krw for x in p.tiers) == p.total_target_krw
    results.append({"case":"package_sum", "ok": ok_pkg, "tiers":[x.model_dump() for x in p.tiers]})

    # report non-empty
    rep = make_report(ReportRequest(
        campaign_title="Test",
        period="2026-02-01~2026-02-14",
        budget_total_krw=30000000,
        kpis=["신규 방문자 비율","재방문율"],
        highlights=["파트너 협업 이벤트 2회 진행"],
    ))
    results.append({"case":"report_nonempty", "ok": len(rep.markdown) > 50})

    passed = sum(1 for r in results if r["ok"])
    out = {"ts": time.time(), "total": len(results), "passed": passed, "pass_rate": passed/len(results), "results": results}

    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"saved: {REPORT}")
    print(f"pass_rate: {passed}/{len(results)}")

if __name__ == "__main__":
    main()
