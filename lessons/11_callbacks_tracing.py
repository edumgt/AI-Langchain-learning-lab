from __future__ import annotations
import time
from rich import print
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from app.core import settings
from lessons._utils import header, show_provider

class SimpleTimingCallback(BaseCallbackHandler):
    def __init__(self):
        self.t0 = None

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.t0 = time.time()
        print("[yellow]chain_start[/yellow]", serialized.get("name"))

    def on_chain_end(self, outputs, **kwargs):
        dt = time.time() - (self.t0 or time.time())
        print(f"[yellow]chain_end[/yellow] elapsed={dt:.2f}s")

    def on_llm_start(self, serialized, prompts, **kwargs):
        print("[magenta]llm_start[/magenta]")

    def on_llm_end(self, response, **kwargs):
        print("[magenta]llm_end[/magenta]")

def main():
    header("11) Callbacks / Tracing")
    show_provider()

    if settings.LANGCHAIN_TRACING_V2:
        print("[green]LangSmith tracing enabled[/green] (LANGCHAIN_TRACING_V2=true)")
        print("[dim]LANGCHAIN_API_KEY / LANGCHAIN_PROJECT 설정이 필요합니다.[/dim]")
    else:
        print("[dim]LangSmith tracing은 꺼져 있습니다. 필요하면 .env에서 LANGCHAIN_TRACING_V2=true[/dim]")

    cb = SimpleTimingCallback()
    llm = build_chat_model().with_config({"callbacks": [cb]})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 실행 계획을 만드는 코치다."),
        ("human", "2주 안에 문화예술기관 SNS 캠페인을 런칭하려고 한다. 체크리스트와 일정표를 제시해줘."),
    ])

    resp = (prompt | llm).invoke({})
    print("\n[bold]Answer[/bold]")
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
