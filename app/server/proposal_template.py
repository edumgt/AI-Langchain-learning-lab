from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class Section:
    key: str
    title: str
    required: bool = True

# 8~10 page-ish fixed structure (sections count fixed; page count depends on content)
SECTIONS: List[Section] = [
    Section("executive_summary", "1. 요약(Executive Summary)"),
    Section("context_goal", "2. 배경/목표(Why & Goals)"),
    Section("audience_strategy", "3. 타깃/전략(Target & Strategy)"),
    Section("sponsorship_package", "4. 후원 패키지(티어/혜택)"),
    Section("kpi_measurement", "5. KPI/측정(Measurement)"),
    Section("timeline", "6. 일정/운영(Timeline & Ops)"),
    Section("budget", "7. 예산/집행(Budget)"),
    Section("activation", "8. 노출/활성화(Brand Activation)"),
    Section("risk_compliance", "9. 리스크/컴플라이언스(Risk)"),
    Section("appendix_sources", "10. 부록/근거(Sources & Appendix)"),
]

def template_markdown_skeleton() -> str:
    lines = ["# 후원 제안서 (고정 템플릿 v13)", ""]
    for s in SECTIONS:
        lines.append(f"## {s.title}")
        if s.key == "sponsorship_package":
            lines += [
                "",
                "| 티어 | 금액(KRW) | 핵심 혜택 | KPI |",
                "|---|---:|---|---|",
                "| PLATINUM | 0 | (작성) | (작성) |",
                "| GOLD | 0 | (작성) | (작성) |",
                "| SILVER | 0 | (작성) | (작성) |",
                "",
            ]
        elif s.key == "timeline":
            lines += [
                "",
                "| 주차 | 목표 | 산출물 | 담당 |",
                "|---:|---|---|---|",
                "| 1 | (작성) | (작성) | (작성) |",
                "| 2 | (작성) | (작성) | (작성) |",
                "",
            ]
        elif s.key == "budget":
            lines += [
                "",
                "| 항목 | 금액(KRW) | 비고 |",
                "|---|---:|---|",
                "| 유료광고 | 0 | |",
                "| 콘텐츠 제작 | 0 | |",
                "| 커뮤니티/협업 | 0 | |",
                "| 예비비 | 0 | |",
                "",
            ]
        elif s.key == "appendix_sources":
            lines += [
                "",
                "- SOURCE 1: (문서/규정/노트 인용)",
                "- SOURCE 2: (문서/규정/노트 인용)",
                "",
            ]
        else:
            lines += ["", "(작성)", ""]
    return "\n".join(lines)
