from __future__ import annotations
import datetime as dt
from app.tools.schemas import (
    BudgetSplitRequest, BudgetSplitResponse,
    TimelineRequest, TimelineResponse, TimelineItem,
    SponsorshipPackageRequest, SponsorshipPackageResponse, SponsorshipTier,
    ReportRequest, ReportResponse,
)

def budget_split(req: BudgetSplitRequest) -> BudgetSplitResponse:
    # normalize ratios if sum != 1 (simple scale)
    ratios = [req.paid_ads_ratio, req.content_ratio, req.community_ratio, req.contingency_ratio]
    s = sum(ratios) or 1.0
    ratios = [r / s for r in ratios]
    ads, cont, comm, contg = ratios
    total = req.total_krw
    ads_paid = int(total * ads)
    content_prod = int(total * cont)
    community = int(total * comm)
    contingency = total - ads_paid - content_prod - community
    return BudgetSplitResponse(
        ads_paid=ads_paid,
        content_prod=content_prod,
        community=community,
        contingency=contingency,
        total=total,
    )

def timeline(req: TimelineRequest) -> TimelineResponse:
    # simple template timeline
    items = []
    for w in range(1, req.weeks + 1):
        if w == 1:
            items.append(TimelineItem(
                week=w,
                title="전략/세팅",
                deliverables=["타깃 페르소나 정의", "메시지 프레임", "채널/예산 배분", "콘텐츠 캘린더 초안"],
                owner="PM/마케팅"
            ))
        elif w == 2:
            items.append(TimelineItem(
                week=w,
                title="콘텐츠 제작/런칭",
                deliverables=["키비주얼/카피 확정", "랜딩/예약/구매 동선 점검", "런칭 게시/광고 집행", "모니터링 대시보드"],
                owner="마케팅/디자인"
            ))
        else:
            items.append(TimelineItem(
                week=w,
                title="운영/최적화",
                deliverables=["A/B 테스트", "커뮤니티 협업 이벤트", "리포트/회고", "후속 제안서"],
                owner="운영/분석"
            ))
    return TimelineResponse(start_date=req.start_date, weeks=req.weeks, items=items)

def sponsorship_package(req: SponsorshipPackageRequest) -> SponsorshipPackageResponse:
    # naive tiering: descending prices summing to total target (approx)
    base = req.total_target_krw
    tier_count = req.tier_count
    weights = list(range(tier_count, 0, -1))  # e.g., 3,2,1
    ws = sum(weights)
    prices = [int(base * (w/ws)) for w in weights]
    # adjust last tier to match total
    prices[-1] = base - sum(prices[:-1])

    names = ["PLATINUM", "GOLD", "SILVER", "BRONZE", "SUPPORTER"][:tier_count]
    benefits_common = [
        "로고 노출(웹/현장/인쇄물)",
        "초청권/네트워킹",
        "성과 리포트 제공",
    ]
    org_extra = {
        "festival": ["프로그램 북 광고", "VIP 라운지 네이밍"],
        "museum": ["특별전 프리뷰 초청", "교육 프로그램 공동브랜딩"],
        "theatre": ["커튼콜 스폰서 멘션", "로비 프로모션 부스"],
        "foundation": ["CSR 스토리 콘텐츠 제작", "임직원 참여 프로그램"],
        "gallery": ["컬렉터 프리뷰", "작가 토크 후원"],
        "general": ["공식 파트너 표기", "SNS 공동 캠페인"],
    }
    extra = org_extra.get(req.org_type, org_extra["general"])

    tiers = []
    for i in range(tier_count):
        b = benefits_common.copy()
        if i == 0:
            b += extra + ["메인 타이틀 스폰서 네이밍(가능 시)"]
        elif i == 1:
            b += extra
        else:
            b += ["현장 배너 노출 확대"]

        kpis = ["노출(Impressions)", "참여(Clicks/Engagement)", "전환(Leads/Tickets)"]
        tiers.append(SponsorshipTier(name=names[i], price_krw=prices[i], benefits=b, kpis=kpis))

    return SponsorshipPackageResponse(total_target_krw=req.total_target_krw, tiers=tiers)

def make_report(req: ReportRequest) -> ReportResponse:
    md = []
    md.append(f"# {req.campaign_title} 성과 리포트")
    md.append("")
    md.append(f"- 기간: {req.period}")
    md.append(f"- 총예산: {req.budget_total_krw:,} KRW")
    md.append("")
    md.append("## 핵심 KPI")
    for k in req.kpis:
        md.append(f"- {k}")
    md.append("")
    md.append("## 하이라이트")
    for h in req.highlights:
        md.append(f"- {h}")
    md.append("")
    md.append("## 다음 액션")
    md += [
        "- 상위 퍼포먼스 콘텐츠 리패키징/재집행",
        "- 파트너/후원사 대상 성과 공유 및 후속 제안",
        "- 데이터 기반 타깃 세그먼트 정교화",
    ]
    md.append("")
    md.append("> 본 문서는 학습용 템플릿입니다. 조직/행사 특성에 맞게 수정하세요.")
    return ReportResponse(markdown="\n".join(md))
