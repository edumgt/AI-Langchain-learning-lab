#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://localhost:8000}"

curl -s "$BASE/artbiz/proposal" -H "Content-Type: application/json" -d '{
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
