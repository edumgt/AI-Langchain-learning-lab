# VectorStore / Retriever 비교 노트 (카탈로그)

## VectorStore(저장소) vs Retriever(검색 전략)
- VectorStore: 임베딩 기반 저장/검색 엔진 (Chroma, FAISS, etc.)
- Retriever: "어떤 방식으로" 문서를 가져올지 전략(TopK, MMR, MultiQuery, Compression 등)

## 이 레포에서 다루는 것
- Chroma VectorStore: `catalog/rag/03_vectorstore_chroma.py`
- MMR Retriever: `catalog/rag/06_retriever_mmr.py`
- MultiQuery + Compression: `catalog/rag/04_multiquery_compression.py`

## 실전 팁
- TopK는 단순하지만 중복/편향이 생길 수 있음
- MMR(Maximal Marginal Relevance)은 "다양성"을 주어 중복을 줄이는 데 유리
- MultiQuery는 질문을 여러 관점으로 재작성해 Recall을 올림
- Compression은 가져온 문서에서 관련 부분만 뽑아 Context 길이를 줄임
