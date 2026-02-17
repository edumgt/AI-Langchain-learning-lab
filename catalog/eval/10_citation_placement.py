"""EVAL 10 — Citation placement across sections (v15)

Checks saved proposals in /app/storage/proposals/*/proposal.md.

Pass criteria (score=1):
- Every required section has at least 1 SOURCE marker
- total markers >= 6
- non-appendix markers >= 3  (citations not only in appendix)

Output:
  /app/storage/eval_citation_placement.json

Run:
  docker compose run --rm lab python catalog/eval/10_citation_placement.py
"""
from __future__ import annotations
import os, json, time, glob
from rich import print
from app.utils.console import header
from app.server.proposal_citation_enforcer import citation_placement_check

PROPOSAL_DIR = "/app/storage/proposals"
OUT = "/app/storage/eval_citation_placement.json"

def main():
    header("EVAL 10 — Citation placement")
    os.makedirs("/app/storage", exist_ok=True)

    md_files = glob.glob(os.path.join(PROPOSAL_DIR, "*", "proposal.md"))
    checked = 0
    ok = 0
    items = []
    for p in md_files[:200]:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        checked += 1
        rep = citation_placement_check(txt, min_total_markers=6)
        passed = (rep.get("score", 0) == 1.0)
        ok += 1 if passed else 0
        items.append({"path": p, "passed": passed, "report": rep})

    report = {"ts": time.time(), "checked": checked, "ok": ok, "rate": (ok/max(checked,1)), "items": items[:30]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(report)
    print(f"saved: {OUT}")

if __name__ == "__main__":
    main()
