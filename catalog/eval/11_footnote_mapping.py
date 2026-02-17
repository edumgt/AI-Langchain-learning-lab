"""EVAL 11 — Footnote mapping and usage (v16)

Checks saved proposals in /app/storage/proposals/*/proposal.md.

Pass criteria (score=1):
- Body contains at least 2 footnote markers: [1] and [2] (anywhere outside appendix acceptable)
- Appendix contains mapping lines starting with '[1]' and '[2]'

Output:
  /app/storage/eval_footnote_mapping.json

Run:
  docker compose run --rm lab python catalog/eval/11_footnote_mapping.py
"""
from __future__ import annotations
import os, json, time, glob, re
from rich import print
from app.utils.console import header

PROPOSAL_DIR = "/app/storage/proposals"
OUT = "/app/storage/eval_footnote_mapping.json"
APPENDIX_TITLE = "## 10. 부록/근거(Sources & Appendix)"

def _has_appendix_mapping(text: str) -> bool:
    # simple check: mapping lines exist somewhere after appendix heading
    if APPENDIX_TITLE not in text:
        return False
    tail = text.split(APPENDIX_TITLE, 1)[1]
    return ("[1]" in tail) and ("[2]" in tail)

def main():
    header("EVAL 11 — Footnote mapping")
    os.makedirs("/app/storage", exist_ok=True)

    md_files = glob.glob(os.path.join(PROPOSAL_DIR, "*", "proposal.md"))
    checked = 0
    ok = 0
    items = []
    for p in md_files[:200]:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        checked += 1
        body_has_1 = bool(re.search(r"\[1\]", txt))
        body_has_2 = bool(re.search(r"\[2\]", txt))
        appendix_ok = _has_appendix_mapping(txt)
        passed = body_has_1 and body_has_2 and appendix_ok
        ok += 1 if passed else 0
        items.append({"path": p, "passed": passed, "body_has_1": body_has_1, "body_has_2": body_has_2, "appendix_ok": appendix_ok})

    report = {"ts": time.time(), "checked": checked, "ok": ok, "rate": (ok/max(checked,1)), "items": items[:30]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(report)
    print(f"saved: {OUT}")

if __name__ == "__main__":
    main()
