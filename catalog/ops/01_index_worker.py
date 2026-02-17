"""OPS 01 — Index worker (queue-driven)

- /ops/queue-reindex 로 enqueue된 작업을 처리합니다.
- 학습용: 단일 파일 큐(jsonl) 사용. 운영은 Redis/SQS 등으로 확장.

실행:
  docker compose run --rm lab python catalog/ops/01_index_worker.py
"""
from __future__ import annotations
import os, json
from rich import print
from app.utils.console import header
from app.server.index_queue import read_jobs, clear_queue
from app.core import settings
from app.core.rag_utils import ingest_dir

def main():
    header("OPS 01 — Index worker")
    jobs = read_jobs(500)
    if not jobs:
        print("no jobs in queue")
        return

    print(f"jobs: {len(jobs)}")
    for j in jobs:
        mode = j.get("mode","full")
        print({"mode": mode, "ts": j.get("ts")})
        # 학습용: mode 상관없이 전체 재인덱싱(증분은 운영 확장 포인트)
        ingest_dir(settings.DOCS_DIR, settings.CHROMA_PERSIST_DIR, collection="catalog_docs")

    clear_queue()
    print("done; queue cleared")

if __name__ == "__main__":
    main()
