"""RunnablePassthrough: 입력 유지/합성."""
from rich import print
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from app.utils.console import header

def main():
    header("LCEL 02 — RunnablePassthrough")
    # Passthrough로 입력을 그대로 유지하면서 파생값 추가
    chain = (
        RunnablePassthrough.assign(
            length=RunnableLambda(lambda x: len(x["text"])),
            upper=RunnableLambda(lambda x: x["text"].upper()),
        )
    )
    print(chain.invoke({"text":"hello langchain"}))

if __name__ == "__main__":
    main()
