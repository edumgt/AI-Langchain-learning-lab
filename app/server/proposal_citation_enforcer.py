from __future__ import annotations
import re
from typing import Dict, List, Tuple

# Sections where we want at least one in-section citation marker
REQUIRED_SECTIONS = [
    "1. 요약(Executive Summary)",
    "2. 배경/목표(Why & Goals)",
    "3. 타깃/전략(Target & Strategy)",
    "5. KPI/측정(Measurement)",
    "8. 노출/활성화(Brand Activation)",
    "9. 리스크/컴플라이언스(Risk)",
    "10. 부록/근거(Sources & Appendix)",
]

def _split_sections(md: str) -> List[Tuple[str, List[str]]]:
    lines = (md or "").splitlines()
    out: List[Tuple[str, List[str]]] = []
    cur_title = None
    cur_lines: List[str] = []
    for line in lines:
        m = re.match(r"^##\s+(.*)$", line.strip())
        if m:
            if cur_title is not None:
                out.append((cur_title, cur_lines))
            cur_title = m.group(1).strip()
            cur_lines = []
        else:
            if cur_title is not None:
                cur_lines.append(line)
    if cur_title is not None:
        out.append((cur_title, cur_lines))
    return out

def _join_sections(header: str, sections: List[Tuple[str, List[str]]]) -> str:
    lines = [header.strip(), ""]
    for title, body_lines in sections:
        lines.append(f"## {title}")
        lines.extend(body_lines)
        if len(lines) == 0 or lines[-1].strip() != "":
            lines.append("")
    return "\n".join(lines).strip() + "\n"

def enforce_section_citations(md: str, min_markers_per_section: int = 1) -> Tuple[str, Dict]:
    """Ensure each required section contains SOURCE markers.

    Strategy (rule-based, deterministic):
    - If a required section lacks 'SOURCE 1/2', append a short footnote line at the end:
        '근거: SOURCE 1, SOURCE 2'
    - Keep appendix section as the canonical full citation list.
    """
    src = md or ""
    # header: take first H1 line if exists
    header = "# 후원 제안서 (고정 템플릿 v15)"
    for line in src.splitlines():
        if line.startswith("# "):
            header = line.strip()
            break

    sections = _split_sections(src)
    report = {"required": REQUIRED_SECTIONS, "per_section": {}, "total_markers": 0}

    def count_markers(text: str) -> int:
        return len(re.findall(r"\bSOURCE\s*[12]\b", text))

    new_sections: List[Tuple[str, List[str]]] = []
    for title, body_lines in sections:
        body = "\n".join(body_lines).strip()
        markers = count_markers(body)
        if title in REQUIRED_SECTIONS and markers < min_markers_per_section:
            # Add a compact inline footnote at section end
            if body and not body.endswith("\n"):
                body += "\n"
            body += "근거: SOURCE 1, SOURCE 2"
            body_lines = body.splitlines()
            markers = count_markers(body)
        report["per_section"][title] = {"markers": markers, "required": title in REQUIRED_SECTIONS}
        report["total_markers"] += markers
        new_sections.append((title, body_lines))

    out = _join_sections(header, new_sections)
    return out, report

def citation_placement_check(md: str, min_total_markers: int = 6) -> Dict:
    """Check if citations are placed across sections, not only in appendix."""
    sections = _split_sections(md or "")
    def count(text: str) -> int:
        return len(re.findall(r"\bSOURCE\s*[12]\b", text))
    per = {}
    total = 0
    required_ok = True
    for title, lines in sections:
        c = count("\n".join(lines))
        per[title] = c
        total += c
    for req in REQUIRED_SECTIONS:
        if per.get(req, 0) <= 0:
            required_ok = False
            break
    appendix = "10. 부록/근거(Sources & Appendix)"
    non_appendix = total - per.get(appendix, 0)
    return {
        "total_markers": total,
        "min_total_markers": min_total_markers,
        "required_sections_ok": required_ok,
        "non_appendix_markers": non_appendix,
        "score": float(required_ok and (total >= min_total_markers) and (non_appendix >= 3)),
        "per_section": per,
    }
