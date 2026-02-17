"""Perf 02 — batch vs single 호출 비교(학습용)

- batch()는 모델/백엔드에 따라 병렬/묶음 처리로 효율이 좋아질 수 있음
"""
import time
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("PERF 02 — batch vs single (toy)")
    llm = build_chat_model(temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system","제목 생성기. 10자 내외."),
        ("human","{topic}"),
    ])
    chain = prompt | llm

    inputs = [{"topic": f"주제 {i}"} for i in range(10)]

    t0 = time.time()
    outs1 = [chain.invoke(x) for x in inputs]
    t1 = time.time()

    t2 = time.time()
    outs2 = chain.batch(inputs)
    t3 = time.time()

    print("single total:", f"{t1-t0:.2f}s")
    print("batch total :", f"{t3-t2:.2f}s")
    print("sample:", getattr(outs2[0],"content",str(outs2[0])))

if __name__ == "__main__":
    main()
