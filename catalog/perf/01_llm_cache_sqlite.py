"""Perf 01 — LLM Cache (SQLite)

LangChain은 LLM 호출 결과를 캐싱할 수 있습니다.
동일 프롬프트를 반복 호출할 때 비용/지연을 줄이는 패턴입니다.

- SQLiteCache 사용(파일로 저장)
- 같은 질문 2번 호출해 2번째가 캐시 히트인지 확인

주의: 백엔드/버전에 따라 캐시 키 구성이나 동작이 다를 수 있습니다.
"""
import os, time
from rich import print
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from app.core.llm_factory import build_chat_model
from app.utils.console import header

CACHE_PATH = "/app/storage/llm_cache.sqlite"

def main():
    header("PERF 01 — SQLite LLM Cache")
    os.makedirs("/app/storage", exist_ok=True)
    set_llm_cache(SQLiteCache(database_path=CACHE_PATH))

    llm = build_chat_model(temperature=0)
    prompt = [{"role":"user","content":"LangChain LCEL을 한 문단으로 설명해줘."}]

    t0 = time.time()
    r1 = llm.invoke(prompt)
    t1 = time.time()
    print("[bold]1st[/bold]", f"{t1-t0:.2f}s", getattr(r1, "content", str(r1))[:120], "...")

    t2 = time.time()
    r2 = llm.invoke(prompt)
    t3 = time.time()
    print("[bold]2nd[/bold]", f"{t3-t2:.2f}s", getattr(r2, "content", str(r2))[:120], "...")

    print(f"[dim]cache db: {CACHE_PATH}[/dim]")

if __name__ == "__main__":
    main()
