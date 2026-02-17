# ArtBiz E2E App (FastAPI + LangChain/LangGraph patterns)

이 문서는 v6 템플릿의 '엔드투엔드' 흐름을 설명합니다.

## 구성
- API 서버: `app/server/main.py`
  - `POST /chat` : 라우팅 + (chat|rag|plan) 실행
  - `POST /approve` : 승인된 액션 실행(HITL 패턴)
  - `GET /health`
  - `/` : 초간단 웹 클라이언트(static)

- Agent 로직: `app/server/agent.py`
  - `route()` : LLM structured router
  - `answer_rag()` : context-only + citation-required 패턴
  - `run()` : 승인 필요 시 action 저장 후 대기

- Action Store: `app/server/store.py`
  - SQLite에 pending/approved/done 상태 관리

## 실행
```bash
cp .env.example .env
docker compose up --build api
```

브라우저:
- `http://localhost:8000/` (간단 UI)
- `http://localhost:8000/docs` (Swagger)

## 승인(HITL)
`.env`:
- `AUTO_APPROVE=true` → 승인 없이 실행
- `AUTO_APPROVE=false` → `/approve`로 승인해야 실행

승인 예:
```bash
# 1) 먼저 /chat 호출 결과의 pending_action.id를 확인
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' -d '{"q":"보도자료 초안 써줘","mode":"plan","auto_approve":false}' | jq

# 2) 승인
curl -s http://localhost:8000/approve -H 'Content-Type: application/json' -d '{"action_id":"<ID>","approve":true,"token":"YES"}' | jq
```

## 문서(RAG) 넣는 곳
- `data/docs/` 폴더에 PDF/TXT/MD 등을 넣고 실행하면 인덱싱됩니다.
