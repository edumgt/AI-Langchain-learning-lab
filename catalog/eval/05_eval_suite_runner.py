"""EVAL 05 — Eval suite runner (v4+v5 합본)

- RAG 회귀평가(v4) 실행
- LLM judge grounding(v5) 실행
- 결과를 하나의 suite report로 합쳐 저장

저장:
- /app/storage/eval_suite_report.json
"""
from __future__ import annotations
import json, os, time, subprocess, sys
from rich import print
from app.utils.console import header

SUITE_REPORT = "/app/storage/eval_suite_report.json"

def run(cmd: list[str]):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return {"cmd": cmd, "code": p.returncode, "out": p.stdout[-4000:]}

def main():
    header("EVAL 05 — Eval suite runner")
    os.makedirs("/app/storage", exist_ok=True)

    here = "/app"
    items = []
    items.append(run([sys.executable, "catalog/eval/03_rag_regression.py"]))
    items.append(run([sys.executable, "catalog/eval/04_llm_judge_grounding.py"]))
    items.append(run([sys.executable, "catalog/eval/07_citation_compliance.py"]))
    items.append(run([sys.executable, "catalog/eval/08_structure_compliance.py"]))
    items.append(run([sys.executable, "catalog/eval/09_tooldata_consistency.py"]))
    items.append(run([sys.executable, "catalog/eval/10_citation_placement.py"]))
    items.append(run([sys.executable, "catalog/eval/11_footnote_mapping.py"]))
    items.append(run([sys.executable, "catalog/eval/06_tools_accuracy.py"]))

    report = {
        "ts": time.time(),
        "items": items,
        "notes": "stdout는 tail만 저장됩니다. 자세한 리포트 파일은 각 eval 스크립트가 /app/storage에 저장합니다."
    }
    with open(SUITE_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[bold]saved[/bold]: {SUITE_REPORT}")
    for it in items:
        print({"code": it["code"], "cmd": " ".join(it["cmd"])})

if __name__ == "__main__":
    main()
