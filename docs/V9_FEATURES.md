# v9 운영형 확장 기능

## 1) 본문 기반 메타데이터 추출
- 업로드 시 첫 페이지/헤더 텍스트를 읽어 `type/year/org`를 추정해 메타 인덱스에 저장합니다.
- 구현: `app/server/metadata_extractor.py`

## 2) Self-Query 파싱 결과 노출
- `/rag/self-query` 응답에:
  - `parsed.rewritten_query`
  - `parsed.doc_type/year/org`
  - `where_filter`
를 포함해 'LLM이 어떤 필터를 적용했는지' 확인할 수 있습니다.

## 3) 후원사 맞춤 제안서 생성 + HITL 승인 연동
- `/artbiz/proposal`:
  - TOOL_DATA(예산/타임라인/패키지)를 자동 생성해 제안서에 삽입
  - 내부 문서 CONTEXT 기반 근거 인용(SOURCE 1~2)
  - `auto_approve=false`면 pending action 생성 → `/approve` 승인 후 최종 반환

## 실행
```bash
cp .env.example .env
docker compose up --build api
```
Swagger: `http://localhost:8000/docs`
