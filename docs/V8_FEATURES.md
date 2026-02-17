# v8 주요 기능

## 1) 문서 업로드 → 메타데이터 추출 → 인덱싱
- `POST /docs/upload` (pdf/md/txt)
- 업로드 파일은 `data/docs/`에 저장
- 메타데이터는 `data/docs/.meta/index.json`에 저장(type/year/org/filename)
- 인덱싱은 metadata 포함 버전(`ingest_dir_meta`)로 실행

## 2) Self-Query Retriever (metadata filtering)
- `POST /rag/self-query`
- 질문에서 필터 조건(year/type/org)을 추정해 retriever가 metadata filter를 반영

## 3) 후원사 맞춤 제안서 생성(근거 인용 + 리스크 체크)
- `POST /artbiz/proposal`
- 내부 문서 기반으로 '근거' 섹션에 SOURCE 인용
- 리스크 체크리스트 포함(개인정보/과장 약속/브랜드 가이드/운영 인허가 등)

## 4) 평가(Eval suite) 확장
- v4: RAG 회귀평가
- v5: LLM Judge grounding
- v8: Tools accuracy / schema checks (`catalog/eval/06_tools_accuracy.py`)
