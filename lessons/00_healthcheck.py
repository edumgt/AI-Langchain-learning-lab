from __future__ import annotations
import os
from rich import print
from app.core.llm_factory import build_chat_model, provider_name

def main():
    print("[bold]LangChain Learning Lab — Healthcheck[/bold]")
    print(f"Provider: {provider_name()}")
    llm = build_chat_model()

    resp = llm.invoke([{"role":"user","content":"한 문장으로 자기소개 해줘."}])
    print("\n[bold]LLM response[/bold]")
    print(getattr(resp, "content", str(resp)))

    print("\n[dim]Tip: .env에서 LLM_PROVIDER/OLLAMA_BASE_URL 등을 변경해 보세요.[/dim]")

if __name__ == "__main__":
    main()
