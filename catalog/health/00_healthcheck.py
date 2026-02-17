from rich import print
from app.core.llm_factory import build_chat_model, provider_name
from app.utils.console import header

def main():
    header("HEALTHCHECK — LLM 연결 확인")
    print(f"[green]provider[/green]: {provider_name()}")
    llm = build_chat_model()
    resp = llm.invoke([{"role":"user","content":"한 문장으로 자기소개 해줘."}])
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
