"""JsonOutputParser (모델이 JSON을 잘 뱉어야 함)."""
from rich import print
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("OUTPUT 02 — JsonOutputParser")
    llm = build_chat_model(temperature=0)
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "반드시 JSON만 출력하라."),
        ("human", "관객개발 KPI 3개를 name, definition으로 만들어줘."),
        ("system", "{format_instructions}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser
    print(chain.invoke({}))

if __name__ == "__main__":
    main()
