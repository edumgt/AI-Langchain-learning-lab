"""EVAL 07 — Citation compliance check

목표:
- 생성물(답변/제안서)에 'SOURCE 1' 또는 'SOURCE 2' 인용이 포함되는지 체크
- 간단 규칙 기반 지표를 /app/storage/eval_citation_compliance.json 로 저장

실행:
  docker compose run --rm lab python catalog/eval/07_citation_compliance.py
"""
from __future__ import annotations
import os, json, time, glob
from rich import print
from app.utils.console import header

PROPOSAL_DIR = "/app/storage/proposals"
OUT = "/app/storage/eval_citation_compliance.json"

def has_citation(text: str) -> bool:
    t = text or ""
    return ("SOURCE 1" in t) or ("SOURCE 2" in t)

def main():
    header("EVAL 07 — Citation compliance")
    os.makedirs("/app/storage", exist_ok=True)

    md_files = glob.glob(os.path.join(PROPOSAL_DIR, "*", "proposal.md"))
    checked = 0
    ok = 0
    items = []
    for p in md_files[:200]:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        checked += 1
        c = has_citation(txt)
        ok += 1 if c else 0
        items.append({"path": p, "ok": c})

    report = {"ts": time.time(), "checked": checked, "ok": ok, "rate": (ok/max(checked,1)), "items": items[:50]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(report)
    print(f"saved: {OUT}")

if __name__ == "__main__":
    main()
