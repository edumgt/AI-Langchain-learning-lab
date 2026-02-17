from __future__ import annotations
from rich import print
from app.core.llm_factory import build_chat_model, provider_name

def header(title: str):
    print("\n" + "=" * 80)
    print(f"[bold cyan]{title}[/bold cyan]")
    print("=" * 80)

def show_provider():
    print(f"[green]LLM provider:[/green] {provider_name()}")
