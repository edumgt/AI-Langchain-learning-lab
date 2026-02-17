from __future__ import annotations
import os, re, json
from typing import Any, Dict, Tuple

def _read_text_head(path: str, max_chars: int = 4000) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in [".md", ".txt", ".log", ".csv"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_chars)
        if ext == ".pdf":
            try:
                from pypdf import PdfReader
                r = PdfReader(path)
                parts = []
                for i, page in enumerate(r.pages[:2]):
                    parts.append(page.extract_text() or "")
                return "\n".join(parts)[:max_chars]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""

def infer_metadata_from_text(filename: str, text: str) -> Dict[str, Any]:
    lower = (text or "").lower()
    fn = filename.lower()

    # type inference
    if any(k in lower for k in ["규정", "policy", "개인정보", "privacy"]):
        doc_type = "policy"
    elif any(k in lower for k in ["보도", "press", "pr", "media"]):
        doc_type = "pr"
    elif any(k in lower for k in ["후원", "sponsor", "제안서", "proposal"]):
        doc_type = "proposal"
    else:
        doc_type = "general"

    # year inference
    year = None
    m = re.search(r"(20\d{2})", text or "")
    if m:
        try:
            y = int(m.group(1))
            if 2000 <= y <= 2100:
                year = y
        except Exception:
            year = None

    # org inference (very light heuristics)
    org = None
    # common patterns: "OOO재단", "OOO극장", "OOO미술관"
    m2 = re.search(r"([가-힣A-Za-z0-9\- ]{2,30})(재단|극장|미술관|박물관|문화재단|페스티벌|축제)", text or "")
    if m2:
        org = (m2.group(1) + m2.group(2)).strip()
    if not org:
        # fallback from filename
        m3 = re.search(r"([가-힣A-Za-z0-9\-]{2,30})(재단|극장|미술관|박물관|축제)", fn)
        if m3:
            org = (m3.group(1) + m3.group(2)).strip()

    return {"type": doc_type, "year": year, "org": org}

def build_sidecar_meta(doc_path: str) -> Dict[str, Any]:
    filename = os.path.basename(doc_path)
    head = _read_text_head(doc_path)
    meta = infer_metadata_from_text(filename, head)
    meta.update({"filename": filename})
    return meta
