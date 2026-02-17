# Tools API (예술경영 도메인 툴)

v7부터 FastAPI에 `/tools/*` 엔드포인트가 추가됩니다.
목표는 LLM이 하기 어려운 "구조 계산/템플릿 산출"을 안정적으로 제공하는 것입니다.

## 실행
```bash
docker compose up --build api
```

Swagger:
- `http://localhost:8000/docs`

## 엔드포인트
### 1) 예산 배분
`POST /tools/budget-split`

예:
```bash
curl -s http://localhost:8000/tools/budget-split \
  -H 'Content-Type: application/json' \
  -d '{"total_krw":30000000,"paid_ads_ratio":0.45,"content_ratio":0.3,"community_ratio":0.15,"contingency_ratio":0.1}'
```

### 2) 2주 타임라인 템플릿
`POST /tools/timeline`

### 3) 후원 패키지 템플릿
`POST /tools/sponsorship-package`

### 4) 리포트 Markdown 생성
`POST /tools/report`

## LLM과 결합 패턴
- Plan 모드에서 `agent.py`가 간단 휴리스틱으로 툴을 호출해 TOOL_DATA를 만들고,
  LLM은 그 TOOL_DATA를 바탕으로 계획서를 문서화합니다.
