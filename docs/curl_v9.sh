#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://localhost:8000}"

echo "== upload sample doc =="
curl -s "$BASE/docs/upload" -F "file=@data/docs/sample_artbiz_notes.md" | jq .

echo "== self-query =="
curl -s "$BASE/rag/self-query" -H "Content-Type: application/json" -d '{"q":"2026년 proposal 문서 기반으로 후원 패키지 혜택 요약","top_k":4}' | jq .

echo "== proposal auto approve =="
curl -s "$BASE/artbiz/proposal" -H "Content-Type: application/json" -d '{"sponsor_name":"ACME","campaign_title":"도시 커뮤니티 예술 캠페인","budget_total_krw":30000000,"weeks":2,"org_type":"festival","auto_approve":true}' | jq .
