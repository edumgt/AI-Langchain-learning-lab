from __future__ import annotations
import re
from typing import Dict, Tuple, List
from app.server.proposal_template import SECTIONS, template_markdown_skeleton

def _extract_sections(md: str) -> Dict[str, str]:
    # Map by normalized heading title to content
    lines = (md or "").splitlines()
    sec_map: Dict[str, List[str]] = {}
    cur = None
    cur_title = None
    for line in lines:
        m = re.match(r"^##\s+(.*)$", line.strip())
        if m:
            cur_title = m.group(1).strip()
            cur = cur_title
            sec_map.setdefault(cur, [])
            continue
        if cur is not None:
            sec_map[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in sec_map.items()}

def normalize_to_template(md: str) -> Tuple[str, Dict[str, any]]:
    """Normalize any markdown to the fixed v13 template.

    - Ensures all required sections exist and in correct order.
    - Tries to reuse content from existing sections by fuzzy matching titles.
    - Preserves any 'SOURCE 1/2' lines if present.
    """
    src = md or ""
    extracted = _extract_sections(src)

    # capture sources anywhere
    sources = []
    for line in src.splitlines():
        if "SOURCE 1" in line or "SOURCE 2" in line:
            sources.append(line.strip())

    out = ["# 후원 제안서 (고정 템플릿 v13)", ""]
    used = []
    for s in SECTIONS:
        out.append(f"## {s.title}")
        # find best matching extracted section by contains
        content = ""
        for k, v in extracted.items():
            if s.title.split(". ", 1)[-1].split("(")[0].strip() in k:
                content = v
                used.append(k)
                break
        # if missing, put placeholder skeleton section (from skeleton)
        if not content:
            content = "(작성)"
        out.append(content.strip())
        out.append("")

        # ensure required tables exist in certain sections
        if s.key == "sponsorship_package" and "|" not in content:
            out += [
                "| 티어 | 금액(KRW) | 핵심 혜택 | KPI |",
                "|---|---:|---|---|",
                "| PLATINUM | 0 | (작성) | (작성) |",
                "| GOLD | 0 | (작성) | (작성) |",
                "| SILVER | 0 | (작성) | (작성) |",
                "",
            ]
        if s.key == "timeline" and "| 주차" not in content:
            out += [
                "| 주차 | 목표 | 산출물 | 담당 |",
                "|---:|---|---|---|",
                "| 1 | (작성) | (작성) | (작성) |",
                "| 2 | (작성) | (작성) | (작성) |",
                "",
            ]
        if s.key == "budget" and "| 항목" not in content:
            out += [
                "| 항목 | 금액(KRW) | 비고 |",
                "|---|---:|---|",
                "| 유료광고 | 0 | |",
                "| 콘텐츠 제작 | 0 | |",
                "| 커뮤니티/협업 | 0 | |",
                "| 예비비 | 0 | |",
                "",
            ]
        if s.key == "appendix_sources":
            if sources:
                out += [*sources, ""]
            else:
                out += ["- SOURCE 1: (문서/규정/노트 인용)", "- SOURCE 2: (문서/규정/노트 인용)", ""]

    normalized = "\n".join(out).strip() + "\n"
    report = {
        "sections_required": len(SECTIONS),
        "sections_found": len(extracted),
        "used_titles": used,
        "has_sources": bool(sources),
    }
    return normalized, report

def check_structure(md: str) -> Dict[str, any]:
    titles = [s.title for s in SECTIONS]
    found = []
    for line in (md or "").splitlines():
        if line.startswith("## "):
            found.append(line[3:].strip())
    missing = [t for t in titles if t not in found]
    order_ok = True
    # order check: indices increasing
    idxs = [found.index(t) for t in titles if t in found]
    if idxs != sorted(idxs):
        order_ok = False
    tables_ok = all([
        ("| 티어" in md) ,
        ("| 주차" in md),
        ("| 항목" in md),
    ])
    sources_ok = ("SOURCE 1" in md) or ("SOURCE 2" in md)
    return {
        "missing_sections": missing,
        "order_ok": order_ok,
        "tables_ok": tables_ok,
        "sources_ok": sources_ok,
        "score": float(order_ok and tables_ok and (len(missing)==0)),
    }
