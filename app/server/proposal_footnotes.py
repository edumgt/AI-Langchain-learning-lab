from __future__ import annotations
import re
from typing import List, Dict, Tuple

APPENDIX_TITLE = "10. 부록/근거(Sources & Appendix)"

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
        if not lines or lines[-1].strip() != "":
            lines.append("")
    return "\n".join(lines).strip() + "\n"

def _extract_h1(md: str) -> str:
    for line in (md or "").splitlines():
        if line.startswith("# "):
            return line.strip()
    return "# 후원 제안서"

def _mk_appendix_mapping(used_docs: List[Dict]) -> List[str]:
    # used_docs: [{meta, preview}, ...]
    s1 = (used_docs[0]["preview"] if used_docs and len(used_docs) > 0 else "(문서 인용)")
    s2 = (used_docs[1]["preview"] if used_docs and len(used_docs) > 1 else "(문서 인용)")
    # keep snippets short
    s1 = (s1 or "").strip().replace("\n"," ")
    s2 = (s2 or "").strip().replace("\n"," ")
    if len(s1) > 220: s1 = s1[:220] + "…"
    if len(s2) > 220: s2 = s2[:220] + "…"
    return [f"[1] {s1}", f"[2] {s2}"]

def apply_footnotes(md: str, used_docs: List[Dict] | None = None) -> Tuple[str, Dict]:
    """Convert SOURCE markers to footnote markers [1]/[2] in-body,
    and ensure appendix contains [1]/[2] mapping lines.

    Rules:
    - In non-appendix sections: replace 'SOURCE 1' -> '[1]', 'SOURCE 2' -> '[2]'
      and also '(SOURCE 1)' -> '[1]' etc.
    - In appendix: ensure mapping exists; keep any original SOURCE lines but append mapping if missing.
    """
    used_docs = used_docs or []
    header = _extract_h1(md)
    sections = _split_sections(md)

    total_src1 = 0
    total_src2 = 0
    out_sections: List[Tuple[str, List[str]]] = []
    appendix_seen = False
    appendix_lines: List[str] = []

    def repl_body(text: str) -> str:
        nonlocal total_src1, total_src2
        # count before replace
        total_src1 += len(re.findall(r"\bSOURCE\s*1\b", text))
        total_src2 += len(re.findall(r"\bSOURCE\s*2\b", text))
        text = re.sub(r"\(\s*SOURCE\s*1\s*\)", "[1]", text, flags=re.I)
        text = re.sub(r"\(\s*SOURCE\s*2\s*\)", "[2]", text, flags=re.I)
        text = re.sub(r"\bSOURCE\s*1\b", "[1]", text, flags=re.I)
        text = re.sub(r"\bSOURCE\s*2\b", "[2]", text, flags=re.I)
        return text

    for title, body_lines in sections:
        body = "\n".join(body_lines)
        if title == APPENDIX_TITLE:
            appendix_seen = True
            appendix_lines = body_lines[:]  # keep as-is for now
            out_sections.append((title, body_lines))
        else:
            body2 = repl_body(body)
            out_sections.append((title, body2.splitlines()))

    # ensure appendix exists
    if not appendix_seen:
        out_sections.append((APPENDIX_TITLE, ["- (근거)", ""]))

    # rebuild to edit appendix in-place
    # find appendix index
    idx = None
    for i,(t,_) in enumerate(out_sections):
        if t == APPENDIX_TITLE:
            idx = i
            break

    mapping = _mk_appendix_mapping(used_docs)
    if idx is not None:
        app_body = "\n".join(out_sections[idx][1])
        # if mapping missing, append
        if "[1]" not in app_body or "[2]" not in app_body:
            # keep a blank line before mapping for readability
            new_lines = out_sections[idx][1][:]
            if new_lines and new_lines[-1].strip() != "":
                new_lines.append("")
            new_lines += mapping
            new_lines.append("")
            out_sections[idx] = (APPENDIX_TITLE, new_lines)

    # Also ensure body has at least one marker; if none, add in executive summary end.
    rebuilt = _join_sections(header, out_sections)
    body_markers = len(re.findall(r"\[1\]|\[2\]", rebuilt))
    if body_markers == 0:
        # append a marker to the first section line deterministically
        parts = rebuilt.splitlines()
        for i,line in enumerate(parts):
            if line.startswith("## "):
                # find end of this section (next heading or EOF)
                j = i+1
                while j < len(parts) and not parts[j].startswith("## "):
                    j += 1
                insert_at = max(i+1, j-1)
                parts.insert(insert_at, "근거: [1] [2]")
                rebuilt = "\n".join(parts).strip() + "\n"
                break

    report = {
        "converted_src1": total_src1,
        "converted_src2": total_src2,
        "has_appendix_mapping": True,
        "mapping": mapping,
        "body_markers": len(re.findall(r"\[1\]|\[2\]", rebuilt)),
    }
    return rebuilt, report
