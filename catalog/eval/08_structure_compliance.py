"""EVAL 08 — Proposal structure compliance

Checks saved proposals in /app/storage/proposals/*/proposal.md against v13 template rules.

Metric:
- score = 1 if all required sections present + order ok + required tables present + sources present
- report saved to /app/storage/eval_structure_compliance.json

Run:
  docker compose run --rm lab python catalog/eval/08_structure_compliance.py
"""
from __future__ import annotations
import os, json, time, glob
from rich import print
from app.utils.console import header
from app.server.proposal_normalizer import check_structure

PROPOSAL_DIR = "/app/storage/proposals"
OUT = "/app/storage/eval_structure_compliance.json"

def main():
    header("EVAL 08 — Structure compliance")
    os.makedirs("/app/storage", exist_ok=True)

    md_files = glob.glob(os.path.join(PROPOSAL_DIR, "*", "proposal.md"))
    checked = 0
    ok = 0
    items = []
    for p in md_files[:200]:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        checked += 1
        chk = check_structure(txt)
        passed = (chk.get("score",0) == 1.0)
        ok += 1 if passed else 0
        items.append({"path": p, "passed": passed, "check": chk})

    report = {"ts": time.time(), "checked": checked, "ok": ok, "rate": (ok/max(checked,1)), "items": items[:30]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(report)
    print(f"saved: {OUT}")

if __name__ == "__main__":
    main()
