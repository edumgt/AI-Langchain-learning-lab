# v14 (LLM 섹션 리라이트 + TOOL_DATA 결정론 매핑 + 일관성 검사)

## 1) 섹션별 LLM 리라이트(서술만) + 표는 TOOL_DATA로 결정론적 채우기
- 기본 모드: `rewrite_mode="llm_sections"` (v14)
- LLM은 서술 섹션만 생성:
  - 요약 / 배경·목표 / 타깃·전략 / KPI / 노출·활성화 / 리스크 / 근거
- 표(후원 패키지/일정/예산)는 TOOL_DATA로 **코드가 직접 생성** → 숫자 추측 방지

구현:
- `app/server/proposal_section_rewriter.py`
- `app/server/proposal_table_fillers.py`

## 2) 일관성 리포트
응답에 `consistency_report` 추가:
- 예산 표 합계 vs tool_data 총액
- 패키지 티어 금액 vs tool_data 티어 금액
- SOURCE 1/2 존재 여부

구현:
- `app/server/proposal_consistency.py`

## 3) 사용 예
```bash
curl -s http://localhost:8000/artbiz/proposal -H "Content-Type: application/json" -d '{
  "sponsor_name":"ACME",
  "campaign_title":"도시 커뮤니티 예술 캠페인",
  "budget_total_krw":30000000,
  "weeks":2,
  "org_type":"festival",
  "rewrite_mode":"llm_sections",
  "normalize":true,
  "auto_approve":true,
  "save":true,
  "format":"both"
}' | jq .
```

## 4) Eval suite 확장
- `catalog/eval/09_tooldata_consistency.py` 포함
