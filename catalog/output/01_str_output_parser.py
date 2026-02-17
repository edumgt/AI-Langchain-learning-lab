"""StrOutputParser."""
from rich import print
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("OUTPUT 01 — StrOutputParser")
    llm = build_chat_model()
    prompt = ChatPromptTemplate.from_messages([("human","{q}")])
    chain = prompt | llm | StrOutputParser()
    print(chain.invoke({"q":"한 줄로 '후원 패키지'를 설명해줘."}))

if __name__ == "__main__":
    main()
