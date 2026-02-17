# v13 고정형(8~10p) 제안서 템플릿 + 자동 정규화

## 1) 고정 템플릿
- 템플릿 스켈레톤: `GET /artbiz/proposal/template`
- 섹션(고정 10개):
  1) 요약
  2) 배경/목표
  3) 타깃/전략
  4) 후원 패키지(표)
  5) KPI/측정
  6) 일정/운영(표)
  7) 예산/집행(표)
  8) 노출/활성화
  9) 리스크/컴플라이언스
  10) 부록/근거(SOURCE 1~2)

## 2) 자동 정규화(리라이트/정규화)
- `/artbiz/proposal` 기본값: `"normalize": true`
- 생성 결과가 구조를 벗어나면:
  - 섹션 누락 보정
  - 섹션 순서 고정
  - 필수 표(패키지/일정/예산) 삽입
  - SOURCE 라인 유지(가능하면)

구현:
- `app/server/proposal_template.py`
- `app/server/proposal_normalizer.py`

## 3) 구조 체크 API
- `POST /artbiz/proposal/check`  { markdown: "..." }

## 4) Eval: 구조 준수율
- `catalog/eval/08_structure_compliance.py`
- suite runner 포함:
```bash
docker compose run --rm lab python catalog/eval/05_eval_suite_runner.py
```

## 5) 사용 예
```bash
curl -s http://localhost:8000/artbiz/proposal -H "Content-Type: application/json" -d '{
  "sponsor_name":"ACME",
  "campaign_title":"도시 커뮤니티 예술 캠페인",
  "budget_total_krw":30000000,
  "weeks":2,
  "org_type":"festival",
  "auto_approve":true,
  "save":true,
  "format":"both",
  "normalize":true
}' | jq .
```
