"""LangGraph visualization helpers for catalog demos."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from rich import print


def render_graph_mermaid(app: Any, name: str) -> str:
    """Render and print mermaid graph text, and save it under storage/langgraph."""
    mermaid = app.get_graph().draw_mermaid()

    out_dir = Path("/app/storage/langgraph")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.mmd"
    out_path.write_text(mermaid, encoding="utf-8")

    print(f"\n[bold cyan]Graph (mermaid):[/bold cyan] {out_path}")
    print(mermaid)
    return str(out_path)

