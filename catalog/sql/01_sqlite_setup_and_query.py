"""SQLite + SQLDatabase + create_sql_query_chain."""
import os, sqlite3
from rich import print
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import build_chat_model
from app.utils.console import header

DB_PATH = "/app/storage/catalog.db"

def init_db():
    os.makedirs("/app/storage", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS programs;")
    cur.execute("CREATE TABLE programs (name TEXT, audience TEXT, budget_krw INTEGER);")
    cur.executemany("INSERT INTO programs VALUES (?,?,?)", [
        ("전시A","20-30", 12000000),
        ("공연B","30-40", 15000000),
        ("교육C","10-20", 3000000),
    ])
    con.commit()
    con.close()

def main():
    header("SQL 01 — SQL query chain (SQLite)")
    init_db()
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    llm = build_chat_model(temperature=0)

    chain = create_sql_query_chain(llm, db)
    q = "관객 타깃별 예산 합계를 알려줘."
    sql = chain.invoke({"question": q})
    print("[bold]SQL[/bold]\n", sql)

    res = db.run(sql)
    print("\n[bold]DB result[/bold]\n", res)

    summary = (ChatPromptTemplate.from_messages([
        ("system","결과를 3줄로 요약하고, 개선 포인트 1개 제시."),
        ("human","Q:{q}\nSQL:{sql}\nRES:{res}"),
    ]) | llm).invoke({"q": q, "sql": sql, "res": res})
    print("\n[bold]Summary[/bold]\n", getattr(summary,"content",str(summary)))

if __name__ == "__main__":
    main()
