"""병렬 실행(dict) + assign 패턴."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("LCEL 03 — Parallel + assign")
    llm = build_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 요약 전문가다."),
        ("human", "{text}\n\n요약 3줄."),
    ])

    summarize = prompt | llm | StrOutputParser()
    keywords = ChatPromptTemplate.from_messages([
        ("system", "키워드 추출기다."),
        ("human", "{text}\n\n키워드 5개만, 콤마로."),
    ]) | llm | StrOutputParser()

    chain = {
        "summary": summarize,
        "keywords": keywords,
        "len": RunnableLambda(lambda x: len(x["text"])),
    }

    out = chain.invoke({"text":"문화예술기관은 관객개발을 위해 데이터 기반 캠페인과 커뮤니티 협업을 병행해야 한다."})
    print(out)

if __name__ == "__main__":
    main()
