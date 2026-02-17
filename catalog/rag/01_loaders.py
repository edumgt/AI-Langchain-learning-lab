"""Loaders: PDF/MD/TXT 로딩."""
from rich import print
from app.core import settings
from app.core.rag_utils import load_documents
from app.utils.console import header

def main():
    header("RAG 01 — Loaders")
    docs = load_documents(settings.DOCS_DIR)
    print(f"docs: {len(docs)}")
    if docs:
        print("sample metadata:", docs[0].metadata)
        print("sample content:", docs[0].page_content[:200])

if __name__ == "__main__":
    main()
