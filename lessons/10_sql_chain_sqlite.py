from __future__ import annotations
import os, sqlite3
from rich import print
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_factory import build_chat_model
from lessons._utils import header, show_provider

DB_PATH = "/app/storage/sample.db"

def init_db():
    os.makedirs("/app/storage", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ticket_sales;")
    cur.execute("""
      CREATE TABLE ticket_sales (
        date TEXT,
        program TEXT,
        channel TEXT,
        tickets INTEGER,
        revenue_krw INTEGER
      );
    """)
    rows = [
        ("2026-01-05", "전시A", "온라인", 120, 2400000),
        ("2026-01-05", "전시A", "현장", 80, 1600000),
        ("2026-01-12", "공연B", "온라인", 300, 15000000),
        ("2026-01-12", "공연B", "제휴", 90, 4050000),
        ("2026-02-01", "교육C", "온라인", 60, 600000),
        ("2026-02-01", "교육C", "현장", 40, 400000),
    ]
    cur.executemany("INSERT INTO ticket_sales VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()

def main():
    header("10) SQL — LLM이 SQL을 생성하고 DB에서 답 얻기 (SQLite)")
    show_provider()

    init_db()

    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    llm = build_chat_model(temperature=0)

    # 1) SQL query chain: 질문 -> SQL 생성
    sql_chain = create_sql_query_chain(llm, db)

    question = "채널별 매출 합계와 티켓 수 합계를 알려줘."
    sql = sql_chain.invoke({"question": question})
    print("[bold]Generated SQL[/bold]")
    print(sql)

    # 2) SQL 실행
    result = db.run(sql)
    print("\n[bold]Raw DB result[/bold]")
    print(result)

    # 3) 결과 해석(요약)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "아래 SQL 결과를 운영 관점으로 요약하고, 개선 포인트 2개를 제시하라."),
        ("human", "QUESTION: {q}\nSQL: {sql}\nRESULT: {res}"),
    ])
    resp = (prompt | llm).invoke({"q": question, "sql": sql, "res": result})
    print("\n[bold]Summary[/bold]")
    print(getattr(resp, "content", str(resp)))

if __name__ == "__main__":
    main()
