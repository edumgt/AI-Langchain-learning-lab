"""Few-shot 예시."""
from rich import print
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

def main():
    header("PROMPTS 02 — Few-shot")
    llm = build_chat_model()

    examples = [
        {"input":"전시 홍보 문구", "output":"도시의 결, 당신의 하루에 스며들다."},
        {"input":"교육 프로그램 홍보 문구", "output":"배움이 예술이 되는 순간, 함께하세요."},
    ]

    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])

    fewshot = FewShotChatMessagePromptTemplate(example_prompt=example_prompt, examples=examples)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "너는 문화예술 카피라이터다. 짧고 강렬하게."),
        fewshot,
        ("human", "공연 홍보 문구"),
    ])

    resp = (prompt | llm).invoke({})
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
