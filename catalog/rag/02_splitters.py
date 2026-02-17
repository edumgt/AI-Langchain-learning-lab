"""Splitters: RecursiveCharacterTextSplitter."""
from rich import print
from app.core import settings
from app.core.rag_utils import load_documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.console import header

def main():
    header("RAG 02 — Splitters")
    docs = load_documents(settings.DOCS_DIR)
    if not docs:
        print("[yellow]docs가 없습니다. data/docs에 문서를 넣어보세요.[/yellow]")
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)
    print("chunks:", len(chunks))
    print(chunks[0].page_content[:300])

if __name__ == "__main__":
    main()
