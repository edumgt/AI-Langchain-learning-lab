"""CallbackHandler: timing/logging."""
import time
from rich import print
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.core import settings
from app.utils.console import header

class TimingCallback(BaseCallbackHandler):
    def __init__(self):
        self.t0 = None
    def on_chain_start(self, serialized, inputs, **kwargs):
        self.t0 = time.time()
        print("[yellow]chain_start[/yellow]", serialized.get("name"))
    def on_chain_end(self, outputs, **kwargs):
        dt = time.time() - (self.t0 or time.time())
        print(f"[yellow]chain_end[/yellow] elapsed={dt:.2f}s")

def main():
    header("CALLBACKS 01 — Timing callback")
    if settings.LANGCHAIN_TRACING_V2:
        print("[green]LangSmith tracing enabled[/green]")
    llm = build_chat_model().with_config({"callbacks":[TimingCallback()]})

    prompt = ChatPromptTemplate.from_messages([
        ("system","너는 계획 수립 코치다."),
        ("human","2주 안에 SNS 캠페인 런칭 체크리스트를 만들어줘."),
    ])
    resp = (prompt | llm).invoke({})
    print(getattr(resp,"content",str(resp)))

if __name__ == "__main__":
    main()
