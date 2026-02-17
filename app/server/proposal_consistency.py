from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

def _parse_krw(s: str) -> int:
    s = (s or "").replace(",", "").strip()
    try:
        return int(s)
    except Exception:
        return 0

def extract_table_amounts(md: str, table_header_keyword: str) -> List[int]:
    lines = (md or "").splitlines()
    amounts = []
    in_table = False
    for line in lines:
        if table_header_keyword in line:
            in_table = True
            continue
        if in_table:
            if not line.strip():
                break
            if line.strip().startswith("|---"):
                continue
            if line.strip().startswith("|"):
                cols = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cols) >= 2:
                    amounts.append(_parse_krw(cols[1]))
    return amounts

def check_budget_total(md: str, tool_data: dict) -> Dict[str, Any]:
    tool_total = int(((tool_data or {}).get("budget_split") or {}).get("total_krw") or 0)
    table_amounts = extract_table_amounts(md, "항목")
    table_total = sum(table_amounts)
    ok = (tool_total == 0) or (table_total == tool_total)
    return {"tool_total": tool_total, "table_total": table_total, "ok": ok}

def check_package_amounts(md: str, tool_data: dict) -> Dict[str, Any]:
    tiers = ((tool_data or {}).get("sponsorship_package") or {}).get("tiers") or []
    tool_amounts = [int(t.get("amount_krw") or t.get("amount") or 0) for t in tiers]
    table_amounts = extract_table_amounts(md, "티어")
    ok = True
    if tool_amounts:
        ok = (tool_amounts == table_amounts[:len(tool_amounts)])
    return {"tool_amounts": tool_amounts, "table_amounts": table_amounts, "ok": ok}

def overall(md: str, tool_data: dict) -> Dict[str, Any]:
    b = check_budget_total(md, tool_data)
    p = check_package_amounts(md, tool_data)
    sources_ok = ("SOURCE 1" in md) or ("SOURCE 2" in md)
    return {
        "budget": b,
        "package": p,
        "sources_ok": sources_ok,
        "score": float(b["ok"] and p["ok"] and sources_ok),
    }
