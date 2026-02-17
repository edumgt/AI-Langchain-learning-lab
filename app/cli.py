"""ArtBiz E2E CLI

예:
  docker compose run --rm lab python -m app.cli "관객개발 KPI 3개 제안"
  docker compose run --rm lab python -m app.cli "보도자료 초안 써줘" --mode plan --no-auto-approve

승인 흐름(서버 없이도):
- --no-auto-approve로 실행하면 pending action이 생성될 수 있음(서버 API 쪽이 더 편함).
"""
from __future__ import annotations
import argparse, json, os
from rich import print
from app.server.agent import run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("q", help="question")
    ap.add_argument("--mode", choices=["chat","rag","plan"], default=None)
    ap.add_argument("--top-k", type=int, default=None)
    ap.add_argument("--no-auto-approve", action="store_true")
    args = ap.parse_args()

    out = run(args.q, mode=args.mode, top_k=args.top_k, auto_approve=(None if not args.no_auto_approve else False))
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
