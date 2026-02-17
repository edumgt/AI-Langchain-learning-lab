from __future__ import annotations
from typing import Dict, List, Any
import math

def _fmt_krw(n: int) -> str:
    return f"{int(n):,}"

def build_package_table(tool_data: dict) -> str:
    pkg = (tool_data or {}).get("sponsorship_package") or {}
    tiers = pkg.get("tiers") or []
    # expected keys: name, amount_krw, benefits, kpi
    lines = [
        "| 티어 | 금액(KRW) | 핵심 혜택 | KPI |",
        "|---|---:|---|---|",
    ]
    if not tiers:
        tiers = [
            {"name":"PLATINUM","amount_krw":0,"benefits":"(작성)","kpi":"(작성)"},
            {"name":"GOLD","amount_krw":0,"benefits":"(작성)","kpi":"(작성)"},
            {"name":"SILVER","amount_krw":0,"benefits":"(작성)","kpi":"(작성)"},
        ]
    for t in tiers:
        name = t.get("name") or t.get("tier") or "TIER"
        amount = int(t.get("amount_krw") or t.get("amount") or 0)
        benefits = t.get("benefits") or t.get("benefit_summary") or "(작성)"
        kpi = t.get("kpi") or "(작성)"
        lines.append(f"| {name} | {_fmt_krw(amount)} | {benefits} | {kpi} |")
    return "\n".join(lines)

def build_timeline_table(tool_data: dict) -> str:
    tl = (tool_data or {}).get("timeline") or {}
    weeks = tl.get("weeks") or []
    lines = [
        "| 주차 | 목표 | 산출물 | 담당 |",
        "|---:|---|---|---|",
    ]
    if not weeks:
        weeks = [{"week":1,"goal":"(작성)","deliverables":"(작성)","owner":"(작성)"}]
    for w in weeks:
        week = w.get("week") or w.get("week_no") or ""
        goal = w.get("goal") or "(작성)"
        deliverables = w.get("deliverables") or w.get("output") or "(작성)"
        owner = w.get("owner") or w.get("assignee") or "(작성)"
        lines.append(f"| {week} | {goal} | {deliverables} | {owner} |")
    return "\n".join(lines)

def build_budget_table(tool_data: dict) -> str:
    bs = (tool_data or {}).get("budget_split") or {}
    items = bs.get("items") or bs.get("allocations") or []
    lines = [
        "| 항목 | 금액(KRW) | 비고 |",
        "|---|---:|---|",
    ]
    if not items:
        items = [{"name":"유료광고","amount_krw":0,"note":""}]
    for it in items:
        name = it.get("name") or it.get("category") or "항목"
        amt = int(it.get("amount_krw") or it.get("amount") or 0)
        note = it.get("note") or it.get("rationale") or ""
        lines.append(f"| {name} | {_fmt_krw(amt)} | {note} |")
    return "\n".join(lines)

def build_tables_block(tool_data: dict) -> dict:
    return {
        "package_table": build_package_table(tool_data),
        "timeline_table": build_timeline_table(tool_data),
        "budget_table": build_budget_table(tool_data),
    }
