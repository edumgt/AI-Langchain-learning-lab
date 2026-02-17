from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional

class BudgetSplitRequest(BaseModel):
    total_krw: int = Field(gt=0)
    paid_ads_ratio: float = Field(default=0.45, ge=0, le=1)
    content_ratio: float = Field(default=0.30, ge=0, le=1)
    community_ratio: float = Field(default=0.15, ge=0, le=1)
    contingency_ratio: float = Field(default=0.10, ge=0, le=1)

class BudgetSplitResponse(BaseModel):
    ads_paid: int
    content_prod: int
    community: int
    contingency: int
    total: int

class TimelineRequest(BaseModel):
    start_date: str = Field(description="YYYY-MM-DD")
    weeks: int = Field(default=2, ge=1, le=12)
    goal: str = Field(default="관객개발 캠페인")

class TimelineItem(BaseModel):
    week: int
    title: str
    deliverables: list[str]
    owner: str

class TimelineResponse(BaseModel):
    start_date: str
    weeks: int
    items: list[TimelineItem]

class SponsorshipPackageRequest(BaseModel):
    tier_count: int = Field(default=3, ge=1, le=5)
    total_target_krw: int = Field(gt=0)
    org_type: Literal["museum","theatre","festival","foundation","gallery","general"] = "general"

class SponsorshipTier(BaseModel):
    name: str
    price_krw: int
    benefits: list[str]
    kpis: list[str]

class SponsorshipPackageResponse(BaseModel):
    total_target_krw: int
    tiers: list[SponsorshipTier]

class ReportRequest(BaseModel):
    campaign_title: str
    period: str = Field(description="예: 2026-02-01~2026-02-14")
    budget_total_krw: int
    kpis: list[str]
    highlights: list[str]

class ReportResponse(BaseModel):
    markdown: str
