# v11 개선 사항

## 1) PDF 품질 개선 (Markdown → Styled PDF)
- 단순 텍스트 출력 대신 ReportLab Platypus로 렌더링합니다.
- 지원:
  - 제목/소제목 (#, ##, ###)
  - 불릿 목록 (-, *)
  - 파이프 테이블(간단)
  - 코드블록(```)

구현: `app/server/pdf_renderer.py`

## 2) 제안서 버전 메타데이터 확장
- 저장 시 기록:
  - `tags` (예: ["festival","ACME"])
  - `template_version` (기본: env `PROPOSAL_TEMPLATE_VERSION`, v11)
  - `status` (draft/approved)
  - `approved_by`, `approved_at`

구현: `app/server/proposal_store.py`

## 3) 승인(HITL) 시 버전 승인 기록
- `/approve`로 proposal_publish 승인 시 저장된 버전(id)이 있으면 `approved_*` 필드를 업데이트합니다.

## 사용 예
### 제안서 생성 + 저장 + PDF
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
  "tags":["festival","ACME"],
  "template_version":"v11"
}' | jq .
```

### 버전 목록
```bash
curl -s http://localhost:8000/artbiz/proposals | jq .
```
